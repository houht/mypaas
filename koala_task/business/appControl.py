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

class AppDControl:
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
    
    def appControl(self, taskinfo):
        """
        @summary: �����������
        @param��taskinfo ��������
        taskStatus :
          10 : �ȴ�����
          20 : ������
          30 : �����ɹ�
          31 : ����ʧ��
          30 : ���ر�
          40 : �ر���
          50 : �رճɹ�
          51 : �ر�ʧ��
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.appStart(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
            
    #------appControl------#
    #����һ
    def appStart(self, taskinfo):
        """
        @summary: �������
        @param��taskinfo ��������
        """
        self.logger.debug('appStart: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡӦ��ʵ����Ϣ��
        dealwithInfoModule = DealwithInfoModule(db)
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfo = instanceInfoModule.getById(businessId)
        if not instanceInfo or not instanceInfo['engineId']:
            #д������Ϣ��
            self.logger.debug('appDeploy_can: update task status taskStatus=40 and dealwith=close')
            'taskStatus=40,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '31'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #д�������(DealwithInfoModule) ��������
            self.logger.debug('appDeploy_can: write deploy message to dealwithinfo table')
            message = {}
            dealwithId = UUIDUtils.getId()
            message['action'] = 'app.start.error'
            message['taskId'] = dealwithId
            message['content'] = {}
            message['instanceId'] = businessId
            message['errorCode'] = '2011'
            message['errorMessage'] = 'app instance not exist'
            message = jsonParser.encode(message)
            
            dim_param = {}
            dim_param['dealwithId'] = dealwithId
            dim_param['taskId'] = taskId
            dim_param['dealwithType'] = '31'
            dim_param['message'] = message
            dim_param['status'] = 'failure'        
            dealwithInfoModule.insert(dim_param)
            return
        engineId = instanceInfo['engineId']
        
        router_key = engineId+".app.start.apply"
        action = ".app.start.apply"
        
        dealwithId = UUIDUtils.getId()
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['instanceId'] = businessId
        message = jsonParser.encode(message)
        
        #д�������(DealwithInfoModule) ����������Ϣ
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '20'
        dim_param['message'] = message
        dim_param['status'] = 'success'        
        dealwithInfoModule.insert(dim_param)
        
        #��������
        self.logger.debug('appStart: begin change the task status')
        db.begin()
        try :
            #����������Ϣ�� ״̬
            self.logger.debug('appStart: update task status taskStatus=20 and dealwith=close')
            'taskStatus=40,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('appStart: send app start request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('appStart: send app start request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('appStart: process status error, error message: '+str(e))
        finally :
            db.close()
            
    #�����
    def appStartOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ɹ���taskStatus=90����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('appStartOk: received start ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appStartOk: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('appStartOk: write received deploy message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '30'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
              
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appStartOk: update taskinfo status taskStatus=30,dealwith=close')
        'taskStatus=30,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '30'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appStartOk: update instanceinfo ')
        'status=running'
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['status'] = 'running'  
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appStartOk: start was over')
        
        
    def appStartError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=31��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('appStartError: received start error from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appStartError: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('appStartError: write received start message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '31'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'failure'
                
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appStartError: update taskinfo status taskStatus=31,dealwith=close')
        'taskStatus=31,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '31'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appStartError: update instanceinfo ')
        'status=running'
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['status'] = 'startFail'  
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appStartError: start was over')
        
            
    #������
    def appClose(self, taskinfo):
        """
        @summary: �������
        @param��taskinfo ��������
        """
        self.logger.debug('appClose: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡӦ��ʵ����Ϣ��
        dealwithInfoModule = DealwithInfoModule(db)
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfo = instanceInfoModule.getById(businessId)
        if not instanceInfo or not instanceInfo['engineId']:
            #д������Ϣ��
            self.logger.debug('appDeploy_can: update task status taskStatus=40 and dealwith=close')
            'taskStatus=40,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '51'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #д�������(DealwithInfoModule) ��������
            self.logger.debug('appDeploy_can: write deploy message to dealwithinfo table')
            message = {}
            dealwithId = UUIDUtils.getId()
            message['action'] = 'app.stop.error'
            message['taskId'] = dealwithId
            message['content'] = {}
            message['instanceId'] = businessId
            message['errorCode'] = '2012'
            message['errorMessage'] = 'app instance not exist'
            message = jsonParser.encode(message)
            
            dim_param = {}
            dim_param['dealwithId'] = dealwithId
            dim_param['taskId'] = taskId
            dim_param['dealwithType'] = '51'
            dim_param['message'] = message
            dim_param['status'] = 'failure'        
            dealwithInfoModule.insert(dim_param)
            return
        engineId = instanceInfo['engineId']
        
        router_key = engineId+".app.stop.apply"
        action = ".app.stop.apply"
        
        dealwithId = UUIDUtils.getId()
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['instanceId'] = businessId
        message = jsonParser.encode(message)
        
        #д�������(DealwithInfoModule) ����������Ϣ
        
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '40'
        dim_param['message'] = message
        dim_param['status'] = 'success'        
        dealwithInfoModule.insert(dim_param)
        
        #��������
        self.logger.debug('appStart: begin change the task status')
        db.begin()
        try :
            #����������Ϣ�� ״̬
            self.logger.debug('appStart: update task status taskStatus=20 and dealwith=close')
            'taskStatus=40,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '40'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('appStart: send app start request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('appStart: send app start request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('appStart: process status error, error message: '+str(e))
        finally :
            db.close()
     
    #������
    def appCloseOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #�رճɹ���taskStatus=50��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('appCloseOk: received close ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appCloseOk: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('appCloseOk: write received deploy message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '50'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
              
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appCloseOk: update taskinfo status taskStatus=50,dealwith=close')
        'taskStatus=50,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '50'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appCloseOk: update instanceinfo ')
        'status=closed'
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['status'] = 'closed'  
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appCloseOk: close was over')
        
    def appCloseError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=31��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('appCloseError: received close error from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('appCloseError: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('appCloseError: write received start message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '51'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'failure'
               
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('appCloseError: update taskinfo status taskStatus=51,dealwith=close')
        'taskStatus=51,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '51'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('appCloseError: update instanceinfo ')
        'status=closeFail'
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['status'] = 'closeFail'  
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appCloseError: close was over')
    
    
    