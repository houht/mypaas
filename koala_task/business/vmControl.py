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
from koala_task.services import TaskinfoModule, DealwithInfoModule, InstanceInfoModule, AppInfoModule, ServiceInfoModule,VminfoModule,VmImageModule,VmnetModule
from koala_task.services import Mq

class VmControl:
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
    
    def vmControl(self, taskinfo):
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
            self.vmStart(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
    
    
    #------vmControl------#
    # ����
    def vmStart(self, taskinfo):
        """
        @summary: �������
        @param��taskinfo ��������
        """
        self.logger.debug('vmStart: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡӦ��ʵ����Ϣ��
        dealwithInfoModule = DealwithInfoModule(db)
        vm = VminfoModule(db)
        vmInfo = vm.getById(businessId)
        
        if not vmInfo or not vmInfo['engineId']:
            #д������Ϣ��
            self.logger.debug('vmStart: update task status taskStatus=40 and dealwith=close')
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '31'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #д�������(DealwithInfoModule) ��������
            self.logger.debug('vmStart: write deploy message to dealwithinfo table')
            message = {}
            dealwithId = UUIDUtils.getId()
            message['action'] = 'vm.start.error'
            message['taskId'] = dealwithId
            message['content'] = {}
            message['instanceId'] = businessId
            message['errorCode'] = '2011'
            message['errorMessage'] = 'vm not exist.'
            message = jsonParser.encode(message)
            
            dim_param = {}
            dim_param['dealwithId'] = dealwithId
            dim_param['taskId'] = taskId
            dim_param['dealwithType'] = '31'
            dim_param['message'] = message
            dim_param['status'] = 'failure'        
            dealwithInfoModule.insert(dim_param)
            return
        
        engineId = vmInfo['engineId']
        vmName = vmInfo['vmName']
        
        router_key = engineId+".vm.start.apply"
        action = ".vm.start.apply"
        
        dealwithId = UUIDUtils.getId()
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] = vmName
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
        self.logger.debug('vmStart: begin change the task status')
        db.begin()
        try :
            #����������Ϣ�� ״̬
            self.logger.debug('vmStart: update task status taskStatus=20 and dealwith=close')

            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('vmStart: send vm start request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('vmStart: send vm start request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('vmStart: process status error, error message: '+str(e))
        finally :
            db.close()

    #�����
    def vmStartOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ɹ���taskStatus=90����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmStartOk: received start ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']

        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmStartOk: read dealwithinfo')
        
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmStartOk: write received deploy message')

        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '30'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
              
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmStartOk: update taskinfo status taskStatus=30,dealwith=close')

        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '30'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�vm��(InstanceInfoModule)
        self.logger.debug('vmStartOk: update vminfo ')

        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'running'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmStartOk: start was over')

    def vmStartError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=31��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmStartError: received start error from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmStartError: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmStartError: write received start message')

        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '31'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'failure'
                
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmStartError: update taskinfo status taskStatus=31,dealwith=close')
        'taskStatus=31,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '31'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�Ӧ��ʵ����(InstanceInfoModule)
        self.logger.debug('vmStartError: update vminfo ')

        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'startFail'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmStartError: start was over')

    
    
    # ǿ�ƹػ�
    def vmDestroy(self, taskinfo):
        """
        @summary: �������
        @param��taskinfo ��������
        """
        self.logger.debug('vmDestroy: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡӦ��ʵ����Ϣ��
        dealwithInfoModule = DealwithInfoModule(db)
        vm = VminfoModule(db)
        vmInfo = vm.getById(businessId)
        
        if not vmInfo or not vmInfo['engineId']:
            #д������Ϣ��
            self.logger.debug('vmDestroy: update task status taskStatus=40 and dealwith=close')
            
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '51'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #д�������(DealwithInfoModule) ��������
            self.logger.debug('vmDestroy: write deploy message to dealwithinfo table')
            message = {}
            dealwithId = UUIDUtils.getId()
            message['action'] = 'vm.destory.error'
            message['taskId'] = dealwithId
            message['content'] = {}
            message['instanceId'] = businessId
            message['errorCode'] = '2012'
            message['errorMessage'] = 'vm not exist'
            message = jsonParser.encode(message)
            
            dim_param = {}
            dim_param['dealwithId'] = dealwithId
            dim_param['taskId'] = taskId
            dim_param['dealwithType'] = '51'
            dim_param['message'] = message
            dim_param['status'] = 'failure'        
            dealwithInfoModule.insert(dim_param)
            return
        
        engineId = vmInfo['engineId']
        vmName = vmInfo['vmName']
        
        router_key = engineId+".vm.destroy.apply"
        action = ".vm.destroy.apply"
        
        dealwithId = UUIDUtils.getId()
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] = vmName
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
        self.logger.debug('vmDestroy: begin change the task status')
        db.begin()
        try :
            #����������Ϣ�� ״̬
            self.logger.debug('vmStart: update task status taskStatus=20 and dealwith=close')

            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '40'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('vmDestroy: send vm start request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('vmDestroy: send vm start request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('vmDestroy: process status error, error message: '+str(e))
        finally :
            db.close()
     
    #������
    def vmDestroyOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #�رճɹ���taskStatus=50��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmDestroyOk: received close ok from mq')
        jsonParser = JsonParser()
        dealwithId = json_msg['taskId']

        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmDestroyOk: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmDestroyOk: write received deploy message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '50'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
              
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDestroyOk: update taskinfo status taskStatus=50,dealwith=close')
        'taskStatus=50,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '50'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�vm��(VmInfoModule)
        self.logger.debug('vmDestroyOk: update instanceinfo ')
  
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'stoped'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)

        
        db.close()
        self.logger.debug('vmDestroyOk: close was over')
        
    def vmDestroyError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=31��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmDestroyError: received close error from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        instanceId = json_msg['content']['instanceId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmDestroyError: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmDestroyError: write received start message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '51'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'failure'
               
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmDestroyError: update taskinfo status taskStatus=51,dealwith=close')
        'taskStatus=51,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '51'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�vm��(VmInfoModule)
        self.logger.debug('vmDestroyOk: update instanceinfo ')
  
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'stopFail'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmDestroyError: close was over')
    
    
    # ����������
    def vmProxy(self, taskinfo):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """

        self.logger.debug('vmProxy: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']

        content = jsonParser.decode(content)
        
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡӦ��ʵ����Ϣ��
        dealwithInfoModule = DealwithInfoModule(db)
        
        # ����
        proxyType = content['type']
        proxyPort = content['port']
        
        # ��ѯvm��Ϣ
        vmId = content['vmId']
        vm = VminfoModule(db)
        vmInfo = vm.getById(vmId)
        
        if not vmInfo or not vmInfo['engineId']:
            #д������Ϣ��
            self.logger.debug('vmProxy: update task status taskStatus=40 and dealwith=close')
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '31'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #д�������(DealwithInfoModule) ��������
            self.logger.debug('vmProxy: write message to dealwithinfo table')
            message = {}
            dealwithId = UUIDUtils.getId()
            message['action'] = 'network.portproxy.error'
            message['taskId'] = dealwithId
            message['content'] = {}
            message['instanceId'] = businessId
            message['errorCode'] = '2011'
            message['errorMessage'] = 'vm not exist.'
            message = jsonParser.encode(message)
            
            dim_param = {}
            dim_param['dealwithId'] = dealwithId
            dim_param['taskId'] = taskId
            dim_param['dealwithType'] = '31'
            dim_param['message'] = message
            dim_param['status'] = 'failure'        
            dealwithInfoModule.insert(dim_param)
            return
        
        self.logger.debug('vmProxy: start send mq msg.')
        
        engineId = vmInfo['engineId']
        vmName = vmInfo['vmName']
        ip = vmInfo['ip']
        
        router_key = engineId+".network.portproxy.apply"
        action = ".network.portproxy.apply"
        
        dealwithId = UUIDUtils.getId()
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] = vmName
        message['content']['type'] = proxyType
        message['content']['ip'] = ip
        message['content']['port'] = proxyPort
        
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
        self.logger.debug('vmProxy: begin change the task status')
        db.begin()
        try :
            #����������Ϣ�� ״̬
            self.logger.debug('vmProxy: update task status taskStatus=20 and dealwith=close')

            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #���͹㲥��Ϣ
            self.logger.debug('vmProxy: send vm proxy request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('vmProxy: send vm proxy request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('vmProxy: process status error, error message: '+str(e))
        finally :
            db.close()
        
    
    def vmProxyOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ɹ���taskStatus=90����ɹ���dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmProxyOk: received start ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        content = json_msg['content']
        
        proxyIp = content['proxyIp']
        proxyPort = content['proxyPort']
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmProxyOk: read dealwithinfo')
        
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmProxyOk: write received message')

        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '30'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
              
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmProxyOk: update taskinfo status taskStatus=30,dealwith=close')

        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '30'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #�޸�vmnet��
        self.logger.debug('vmProxyOk: update vmnet ')
        
        tim_param = {}
        iim_param = {}
        iim_param['netId'] = businessId
        iim_param['proxyIP'] = proxyIp
        iim_param['proxyPort'] = proxyPort
        vmnet = VmnetModule(db)
        vmnet.update(iim_param)
        
        db.close()
        self.logger.debug('vmProxyOk: start was over')
    
    def vmProxyError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        #д����ִ�н��
        #����ʧ�ܣ�taskStatus=31��dealwith=close
        #дӦ��ʵ����Ϣ
        self.logger.debug('vmProxyError: received start error from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        
        #��ȡ���ݲ�������
        db = self.__getDb()
        
        #��ȡ�������(DealwithInfoModule)
        self.logger.debug('vmProxyError: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        # ��ȡtask�� 
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        #д�������(DealwithInfoModule) ���յ�����Ϣ 
        self.logger.debug('vmProxyError: write received start message')

        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '31'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'failure'
                
        dealwithInfoModule.insert(dim_param)
        
        #�޸�������Ϣ��(TaskinfoModule)
        self.logger.debug('vmProxyError: update taskinfo status taskStatus=31,dealwith=close')
        
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '31'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        db.close()
        self.logger.debug('vmProxyError: proxy was over')
        
    # �����޸ĵ�
    def vmConf(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmConfOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmConfError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
    
    # �����ػ�
    def vmShutdown(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmShutdownOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmShutdownError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
    
    # ���Ӵ���
    def vmDisk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmDiskOk(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        
    def vmDiskError(self, json_msg):
        """
        @summary: ����ִ�н��
        @param��json_msg ��Ϣ����
        """
        pass
        

if __name__ == "__main__" :
    
    conf = ConfigManage()
    db_conf = conf.get_db_conf()
    db = MysqlTools(db_conf)
    
#    aa = VmnetModule(db)
#    print aa.getById('f0cf6774954711e49109fe5400e41488')
#    
#    
#    tim_param = {}
#    tim_param['proxyIP'] = '1.1.2.1'
#    tim_param['proxyPort'] = '8009'
#    tim_param['netId'] = 'f0cf6774954711e49109fe5400e41488'
#    print aa.update(tim_param)  