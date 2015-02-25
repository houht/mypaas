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


class VmCreate:
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
    
    
    def vmCreate(self, taskinfo):
        """
        @summary: �����������
        @param��taskinfo ��������
        taskStatus :
          10 : �ȴ�����
          20 : ����ѯ�ʹ㲥
          30 : ������ԴӦ��
          40 : ��������
          90 : �����ɹ�
          91 : ����ʧ��
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.vmCreate_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
     
    #------vmdeploy------#
    #����һ
    def vmCreate_10(self, taskinfo):
        """
        @summary: ����������
        @param��taskinfo ��������
        """
        #����ask�㲥action=bdct.vm.deploy.ask
        #����taskStatus=20�ȴ���Դ��dealwith=close
        self.logger.debug('vmCreate_10: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        contentObj = jsonParser.decode(content)
        cpu = contentObj['cpu']
        mem = contentObj['mem']
        disk = contentObj['size']
        imageId = contentObj['imageId']
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        router_key = 'bdct.vm.create.ask'
        action = 'vm.create.ask'
        dealwithId = UUIDUtils.getId()
        
        
        # ��ѯvm����
        vmImage = VmImageModule(db)
        ImageInfo = vmImage.getByImageId(imageId)
        vmType = ImageInfo['vtype']
        
        #����ѯ�ʹ㲥��Ϣ
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['vmType'] = vmType
        message = jsonParser.encode(message)
        
        #д��������(DealwithInfoModule)
        self.logger.debug('vmCreate_10: write send ask message to dealwithInfo table')

        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '20'
        dim_param['message'] = message
        dim_param['status'] = 'success'
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        self.logger.debug('vmCreate_10: begin change task status')
        #��������
        db.begin()
        try :
            #�޸�������Ϣ��(TaskinfoModule)
            self.logger.debug('vmCreate_10: update task status')
            
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('vmCreate_10: send ask message to the bdct of mq')
            self.mq.send_bdct_message(router_key, message)
            db.end()
            self.logger.debug('vmCreate_10: process task is over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.error('vmCreate_10: process task error, error message: '+str(e))
            
        finally :
            db.close()
     
    #���������mq���յ��㲥Ӧ�𴥷�
    def vmCreate_can(self, json_msg):
        """
        @summary: ��ԴӦ�������һ��Ӧ��������·���������
        @param��taskinfo ��������
        """
        
        #���ʹ������� action=task_rst.vm.deploy.can
        #����taskStatus=30�ȴ����������dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmCreate_can: received vmcreate ask reply from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        engineId = json_msg['content']['engineId']
        engineIp = json_msg['content']['engineIp']
        
        self.logger.debug('vmCreate_can: reply engineId: '+engineId+",taskId: "+dealwithId)
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmCreate_can: read task dealwithinfo by dealwithid: '+dealwithId)
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('vmCreate_can: read task info by taskId: '+taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        if taskStatus != '20' :
            '�Ѿ����յ���ԴӦ�𣬲���ִ���˴���'
            self.logger.debug('vmCreate_can: the task has  access to resources: taskStatus:'+taskStatus)
            return
            
        #д�������(DealwithInfoModule) ����Ӧ�� 
        self.logger.debug('vmCreate_can: write received ask reply message to dealwithinfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '30'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        
        #�������뿪ʼ-----------------------------
        self.logger.debug('vmCreate_can: begin deploy the task to engine')
        contentObj = jsonParser.decode(content)
        #��Դ����
        vmName = contentObj['vmName']
        cpu = contentObj['cpu']
        mem = contentObj['mem']
        disk = contentObj['size']
        imageId = contentObj['imageId']
        
        # ��ѯvm����
        vmImage = VmImageModule(db)
        ImageInfo = vmImage.getByImageId(imageId)
        vmType = ImageInfo['vtype']
        
        action = 'vm.create.apply'
        router_key = engineId + ".vm.create.apply"
        dealwithId = UUIDUtils.getId()
        
        #��������������Ϣ
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] =  vmName
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['vmType'] = vmType
        # ����
        if 'attachDisks' in contentObj:
            message['content']['attachDisks'] = contentObj['attachDisks']
        # ������
        if 'hostName' in contentObj:
            message['content']['hostName'] = contentObj['hostName']
        
        message['content']['imageId'] = imageId 
        message = jsonParser.encode(message) 
        
        # ��ʱû��
        # host
        # attachDisks
        
        #д�������(DealwithInfoModule) ��������
        self.logger.debug('vmCreate_can: write deploy message to dealwithinfo table')
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '40'
        dim_param['message'] = message
        dim_param['status'] = 'success'        
        dealwithInfoModule.insert(dim_param)
        
        #��������
        self.logger.debug('vmCreate_can: begin change the task status')
        db.begin()
        try :
            #�޸�������Ϣ��(TaskinfoModule)
            self.logger.debug('vmCreate_can: update task status taskStatus=40 and dealwith=close')
            
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '40'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #�޸�Ӧ��ʵ����(InstanceInfoModule)
            self.logger.debug('vmCreate_can: update vminfo engineId=%s'%engineId)
            
            iim_param = {}
            iim_param['vmId'] = businessId
            iim_param['engineId'] = engineId
            iim_param['engineIp'] = engineIp
            #engineIp
            vminfo = VminfoModule(db)
            vminfo.update(iim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('vmCreate_can: send deploy request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('vmCreate_can: send deploy request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('vmCreate_can: process status error, error message: '+str(e))
        finally :
            db.close()
    
    #������ ,��mq���յ��������������task_rst.app.deploy.ok
    def vmCreate_ok(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��taskinfo ��������
        """
        #д����ִ�н��
        #�����ɹ���taskStatus=90�����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmCreate_ok: received deploy ok from mq')
        jsonParser = JsonParser()
        
        # ���ز���
        dealwithId = json_msg['taskId']
        ip = json_msg['content']['ip']
        vncPort = json_msg['content']['vncPort']
        vncPasswd = json_msg['content']['vncPasswd']
        
        self.logger.debug('vmCreate_ok: received dealwithId: %s ' % dealwithId)
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmCreate_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('vmCreate_ok: read tas info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmCreate_ok: write received deploy message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '90'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmCreate_ok: update taskinfo status taskStatus=90,dealwith=close')
        'taskStatus=90,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('vmCreate_ok: update vminfo ')

        iim_param = {}
        iim_param['vmId'] = businessId
        
        iim_param['ip'] = ip
        iim_param['vncPort'] = vncPort
        iim_param['vncPasswd'] = vncPasswd
        
        iim_param['status'] = 'created'
        
        iim_param['beginTime'] = 'now'  
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmCreate_ok: deploy was over')
    
    #������ ,��mq���յ��������������task_rst.app.deploy.error
    def vmCreate_error(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��taskinfo ��������
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=10�ȴ�������dealwith=open
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmCreate_error: received deploy error message')
        jsonParser = JsonParser() 
        dealwithId = json_msg['taskId']
        
        self.logger.debug('vmCreate_error: dealwithId=%s'%dealwithId)
                
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmCreate_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ
        self.logger.debug('vmCreate_error: received received message to dealwithinfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        #��ȡ������Ϣ��(TaskinfoModule)
        self.logger.debug('vmCreate_error: read task info by taskid=%s'%taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        taskStatus = taskinfo['taskStatus']
        if taskStatus != '40':
            self.logger.warning('vmCreate_error: task status=%s, is not 40'%taskStatus)
            return
        #��ȡ����ѯ�ʹ㲥����20
        self.logger.debug('vmCreate_error: read ask times')
        dealwithInfoList = dealwithInfoModule.getById(dealwithId,'20')
        if len(dealwithInfoList) > 4 :
            #дʧ��
            #��ȡ������Ϣ��(TaskinfoModule)
            self.logger.debug('vmCreate_error: read ask times>4,write task process error')
            taskinfoModule = TaskinfoModule(db)
            tim_param = {}
            tim_param['taskStatus'] = '91'
            tim_param['dealwith'] = 'close'
            tim_param['taskId'] = taskId
            taskinfoModule.update(tim_param)            
        
            #�޸�Ӧ��ʵ����(InstanceInfoModule)
            self.logger.debug('vmCreate_error: update vminfo status=failed,businessid=%s'%businessId)
            
            iim_param = {}
            iim_param['vmId'] = businessId
            iim_param['status'] = 'createFail'
            
            vminfo = VminfoModule(db)
            vminfo.update(iim_param)
        else :
            #������� ��������taskStatus=10,dealwith=open
            #��ȡ������Ϣ��(TaskinfoModule)
            self.logger.debug('vmCreate_error: read ask times<=4,write task process to reprocess,taskStatus=10,dealwith=open,taskId=%s'%taskId)
            taskinfoModule = TaskinfoModule(db)
            tim_param = {}
            tim_param['taskStatus'] = '10'
            tim_param['dealwith'] = 'open'
            tim_param['taskId'] = taskId
            taskinfoModule.update(tim_param)
        
        db.close()
        self.logger.debug('vmCreate_error: error process was over')



if __name__ == "__main__" :
    
    conf = ConfigManage()
    db_conf = conf.get_db_conf()
    db = MysqlTools(db_conf)
    aa = VminfoModule(db)
    print aa.getById('ca09caa68ff411e4b80efe5400e41488')
    
    cc = VmImageModule(db)
    print cc.getByImageId('0F7620DDF32543A097372F11C5B8877F')
    
#    tim_param = {}
#    tim_param['status'] = 'stoping'
#    tim_param['engineId'] = '11111111'
#    tim_param['vmId'] = 'ca09caa68ff411e4b80efe5400e41488'
#    aa.update(tim_param)  