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
from koala_task.services import TaskinfoModule, DealwithInfoModule, InstanceInfoModule, AppInfoModule, ServiceInfoModule
from koala_task.services import Mq


class AppDrop:
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
    
    
    def appDrop(self, taskinfo):
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
            self.appDrop_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
    
    
    
    #------appdrop------#
    #����һ
    def appDrop_10(self, taskinfo):
        ""
        self.logger.debug('appDrop_10: begin drop app ')
        jsonParser = JsonParser()        
        instanceId = taskinfo['businessId']
        taskId = taskinfo['taskId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        # ��ѯinstance��
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfo = instanceInfoModule.getById(instanceId)
        # ��ȡengineid
        engineId = instanceInfo['engineId']
        
        
        # ������Ϣ
        action = 'app.drop.apply'
        router_key = engineId + ".app.drop.apply"
        dealwithId = UUIDUtils.getId()
        
        # ɾ��Ӧ����Ϣ
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['instanceId'] = instanceId
        message = jsonParser.encode(message)
        
        
        
        #д��������(DealwithInfoModule)
        self.logger.debug('appDrop_10: write drop message to dealwithInfo table')
        
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
            self.logger.debug('appDrop_10: update task status')
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            
            #������Ϣ
            self.logger.debug('appDrop_10: send drop app request to task of mq')
            self.mq.send_task_message(router_key, message)
            
            db.end()
            self.logger.debug('appDrop_10: process task is over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.error('appDrop_10: process task error, error message: '+str(e))
            
        finally :
            db.close()
    
    
    
    def appDrop_ok(self, json_msg):
        ""
        
        
        #д����ִ�н��
        #����ɹ���taskStatus=90����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        
        self.logger.debug('appDrop_ok: received drop app ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
          
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appDrop_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('appDrop_ok: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('appDrop_ok: write received drop app message')
    
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '90'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appDrop_ok: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appDrop_ok: update instanceinfo ')
        iim_param = {}
        iim_param['instanceId'] = businessId
        iim_param['status'] = 'destroyed'      
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        
        #�޸�Ӧ�ñ�(AppInfoModule)
        self.logger.debug('appDrop_ok: update appinfo status')
        # ��ȡappid
        instanceInfo = instanceInfoModule.getById(businessId)
        appId = instanceInfo['appId']
        iim_param = {}
        iim_param['appId'] = appId
        iim_param['status'] = 'destroyed'
        AppInfoModule = AppInfoModule(db)
        AppInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appDrop_ok: drop app was over')
        
    #������ ,��mq���յ�������������task_rst.app.deploy.error
    def appDrop_error(self, json_msg):
        ""
        
        
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=10�ȴ�����dealwith=open
        #дӦ��ʵ����Ϣ
        self.logger.debug('appDrop_error: received deploy error message')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        self.logger.debug('appDrop_error: dealwithId=%s,instanceId=%s'%(dealwithId,instanceId))
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appDrop_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('appDrop_error: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ
        self.logger.debug('appDrop_error:  received message to dealwithinfo table')
        
        
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appDrop_error: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '91'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appDrop_error: update instanceinfo ')
        iim_param = {}
        iim_param['instanceId'] = businessId
        iim_param['status'] = 'dropFail' 
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        
        #�޸�Ӧ�ñ�(AppInfoModule)
        self.logger.debug('appDrop_error: update appinfo status')
        # ��ȡappid
        instanceInfo = instanceInfoModule.getById(businessId)
        appId = instanceInfo['app_id']
        iim_param = {}
        iim_param['appId'] = appId
        iim_param['status'] = 'dropFail'
        AppInfoModule = AppInfoModule(db)
        AppInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appDrop_error: drop app process was over')
    