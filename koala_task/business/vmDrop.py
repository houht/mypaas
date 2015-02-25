#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
from koala_task.utils import JsonParser
from koala_task.utils import ParserConf
from koala_task.utils import RabbitMq
from koala_task.utils import LoggerUtil
from koala_task.utils import MysqlTools
from koala_task.utils import UUIDUtils

from koala_task.services import ConfigManage
from koala_task.services import TaskinfoModule
from koala_task.services import TaskinfoModule, DealwithInfoModule, InstanceInfoModule, AppInfoModule, ServiceInfoModule,VminfoModule,VmImageModule
from koala_task.services import Mq

# vmɾ��
class VmDrop:
    ""

    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.mq = Mq()
    
    def __getDb(self) :
        db_conf = self.conf.get_db_conf()
        db = MysqlTools(db_conf)
        return db        
    
    
    def vmDrop(self, taskinfo):
        """
        taskStatus :
          10 : �ȴ�ɾ��
          20 : ɾ��MQ��Ϣ����
          
          90 : ɾ���ɹ�
          91 : ɾ��ʧ��
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.vmDrop_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
    
    
    
    #------vmDrop------#
    #����һ
    def vmDrop_10(self, taskinfo):
        ""
        self.logger.debug('vmDrop_10: begin drop vm ')
        jsonParser = JsonParser()  
              
        businessId = taskinfo['businessId']
        taskId = taskinfo['taskId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        # ��ѯvminfo��
        vm = VminfoModule(db)
        vmInfo = vm.getById(businessId)
        # ��ȡengineid��vmName
        engineId = vmInfo['engineId']
        vmName = vmInfo['vmName']
        
        # ������Ϣ
        action = 'vm.drop.apply'
        router_key = engineId + ".vm.drop.apply"
        dealwithId = UUIDUtils.getId()
        
        # ɾ��Ӧ����Ϣ
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] = vmName
        message = jsonParser.encode(message)

        
        #д��������(DealwithInfoModule)
        self.logger.debug('vmDrop_10: write drop message to dealwithInfo table')
        
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '20'
        dim_param['message'] = message
        dim_param['status'] = 'success'
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        
        #��������
        db.begin()
        try :
            #�޸�������Ϣ��(TaskinfoModule)
            self.logger.debug('vmDrop_10: update task status')
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #������Ϣ
            self.logger.debug('vmDrop_10: send drop vm request to task of mq')
            self.mq.send_task_message(router_key, message)
            
            db.end()
            self.logger.debug('vmDrop_10: process task is over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.error('vmDrop_10: process task error, error message: '+str(e))
            
        finally :
            db.close()
    
    
    
    def vmDrop_ok(self, json_msg):
        ""
        
        
        #д����ִ�н��
        #����ɹ���taskStatus=90����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        
        self.logger.debug('vmDrop_ok: received drop vm ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmDrop_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDrop_ok: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmDrop_ok: write received drop vm message')
    
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '90'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDrop_ok: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�vm��(VmInfoModule)
        self.logger.debug('vmDrop_ok: update VmInfo ')
        
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'destroyed'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmDrop_ok: drop vm was over')
        
    #������ ,��mq���յ�������������task_rst.app.deploy.error
    def vmDrop_error(self, json_msg):
        ""
        
        
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=10�ȴ�����dealwith=open
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmDrop_error: received deploy error message')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
  
        self.logger.debug('vmDrop_error: dealwithId=%s'%(dealwithId))
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmDrop_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDrop_error: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ
        self.logger.debug('vmDrop_error:  received message to dealwithinfo table')
        
        
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDrop_error: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '91'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(VmInfo)
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'dropFail'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmDrop_error: drop vm process was over')
    