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

class AppDeploy:
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
    
    def appDeploy(self, taskinfo):
        """
        @summary: 软件部署任务
        @param：taskinfo 任务内容
        taskStatus :
          10 : 等待部署
          20 : 部署询问广播
          30 : 接收资源应答
          40 : 部署申请
          90 : 部署成功
          91 : 部署失败
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.appDeploy_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
            
    #------appdeploy------#
    #任务一
    def appDeploy_10(self, taskinfo):
        """
        @summary: 待部署任务
        @param：taskinfo 任务内容
        """
        #发送ask广播action=bdct.app.deploy.ask
        #更改taskStatus=20等待资源，dealwith=close
        self.logger.debug('appDeploy_10: begin dealwith task')
        jsonParser = JsonParser()
        
        taskId = taskinfo['taskId']
        content = taskinfo['content']
        businessId = taskinfo['businessId']
        contentObj = jsonParser.decode(content)
        cpu = contentObj['cpu']
        mem = contentObj['mem']
        disk = contentObj['disk']
        serviceId = contentObj['serviceId']
        
        #获取数据操作对象
        db = self.__getDb()
        router_key = 'bdct.app.deploy.ask'
        action = 'app.deploy.ask'
        dealwithId = UUIDUtils.getId()
        
        #部署询问广播消息
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['serviceId'] = serviceId
        message = jsonParser.encode(message)
        
        #写任务处理表库(DealwithInfoModule)
        self.logger.debug('appDeploy_10: write send ask message to dealwithInfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '20'
        dim_param['message'] = message
        dim_param['status'] = 'success'
        print "1999"
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        self.logger.debug('appDeploy_10: begin change task status')
        #开启事物
        db.begin()
        try :
            #修改任务信息表(TaskinfoModule)
            self.logger.debug('appDeploy_10: update task status')
            'taskStatus=20,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #修改应用实例表(InstanceInfoModule)
            self.logger.debug('appDeploy_10: update instance status')
            'status=deploy'
            iim_param = {}
            iim_param['instanceId'] = businessId
            iim_param['status'] = 'deploy'
            instanceInfoModule = InstanceInfoModule(db)
            instanceInfoModule.update(iim_param)
            
            #发送广播消息
            self.logger.debug('appDeploy_10: send ask message to the bdct of mq')
            self.mq.send_bdct_message(router_key, message)
            db.end()
            self.logger.debug('appDeploy_10: process task is over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.error('appDeploy_10: process task error, error message: '+str(e))
            
        finally :
            db.close()
        
    #任务二，由mq接收到广播应答触发
    def appDeploy_can(self, json_msg):
        """
        @summary: 资源应答处理，向第一个应答的引擎下发部署任务
        @param：taskinfo 任务内容
        """
        #发送部署任务 action=task_rst.app.deploy.can
        #更改taskStatus=30等待部署结果，dealwith=close
        #写应用实例信息
        self.logger.debug('appDeploy_can: received deploy ask reply from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        engineId = json_msg['content']['engineId']
        self.logger.debug('appDeploy_can: reply engineId: '+engineId+",taskId: "+dealwithId)
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('appDeploy_can: read task dealwithinfo by dealwithid: '+dealwithId)
        dealwithInfoModule = DealwithInfoModule(db)
        self.logger.debug('appDeploy_can: ssss1111 ')
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        self.logger.debug('appDeploy_can: ssss22222 ')
        taskId = dealwithInfo['taskId']
        self.logger.debug('appDeploy_can: ssss33333 ')
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('appDeploy_can: read task info by taskId: '+taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        if taskStatus != '20' :
            '已经接收到资源应答，并且执行了部署'
            self.logger.debug('appDeploy_can: the task has  access to resources: taskStatus:'+taskStatus)
            return
            
        #写任务处理表(DealwithInfoModule) 接收应答 
        self.logger.debug('appDeploy_can: write received ask reply message to dealwithinfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '30'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #部署申请开始-----------------------------
        self.logger.debug('appDeploy_can: begin deploy the task to engine')
        contentObj = jsonParser.decode(content)
        #资源参数
        cpu = contentObj['cpu']
        mem = contentObj['mem']
        disk = contentObj['disk']
        serviceId = contentObj['serviceId']
        
        #软件信息
        domain = contentObj['domain']
        appName = contentObj['appName']
        appFileId = contentObj['appFileId']
        #环境变量
        contentKeys = contentObj.keys()
        appEnv = None
        userEnv = None
        if 'appEnv' in contentKeys :
            appEnv = contentObj['appEnv']
        if 'userEnv' in contentKeys :            
            userEnv = contentObj['userEnv']
            
        #”listenPort”
        
        action = 'app.deploy.apply'
        router_key = engineId + ".app.deploy.apply"
        dealwithId = UUIDUtils.getId()
        
        #部署部署申请消息
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['serviceId'] = serviceId
        message['content']['instanceId'] = businessId
        
        message['content']['domain'] = domain
        message['content']['appName'] = appName
        message['content']['filename'] = appFileId
        
        message['content']['param'] = {}
        if appEnv is not None :
            message['content']['env'] = appEnv
        if userEnv is not None :
            message['content']['userEnv'] = userEnv
        message = jsonParser.encode(message) 
               
        #写任务处理表(DealwithInfoModule) 部署申请
        self.logger.debug('appDeploy_can: write deploy message to dealwithinfo table')
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '40'
        dim_param['message'] = message
        dim_param['status'] = 'success'        
        dealwithInfoModule.insert(dim_param)
        
        #开启事物
        self.logger.debug('appDeploy_can: begin change the task status')
        db.begin()
        try :
            #修改任务信息表(TaskinfoModule)
            self.logger.debug('appDeploy_can: update task status taskStatus=40 and dealwith=close')
            'taskStatus=40,dealwith=close'
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '40'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #修改应用实例表(InstanceInfoModule)
            self.logger.debug('appDeploy_can: update instanceinfo status engineId=%s'%engineId)
            'engineId=$engineId'
            iim_param = {}
            iim_param['instanceId'] = businessId
            iim_param['engineId'] = engineId
            instanceInfoModule = InstanceInfoModule(db)
            instanceInfoModule.update(iim_param)
            
            #发送广播消息
            self.logger.debug('appDeploy_can: send deploy request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('appDeploy_can: send deploy request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('appDeploy_can: process status error, error message: '+str(e))
        finally :
            db.close()
        
    #任务三 ,由mq接收到部署结果触发，task_rst.app.deploy.ok
    def appDeploy_ok(self, json_msg):
        """
        @summary: 任务执行结果
        @param：taskinfo 任务内容
        """
        #写任务执行结果
        #部署成功，taskStatus=90部署成功，dealwith=close
        #写应用实例信息
        self.logger.debug('appDeploy_can: received deploy ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        serviceId = json_msg['content']['serviceId']
        instanceId = json_msg['content']['instanceId']
        
        self.logger.debug('appDeploy_ok: received dealwithId: %s,serviceId: %s,instanceId: %s'%(dealwithId,serviceId,instanceId))
        app_ip = None
        app_port = None
        
        content_keys  = json_msg['content'].keys()
        if 'param' in content_keys:
            param = json_msg['content']['param']
            param_keys = param.keys()
            if 'ip' in param_keys :
                app_ip = param['ip']
                app_port = param['port']
                
                
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('appDeploy_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('appDeploy_ok: read tas info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        #写任务处理表(DealwithInfoModule) 接收到的信息 
        self.logger.debug('appDeploy_ok: write received deploy message')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '90'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #修改任务信息表(TaskinfoModule)
        self.logger.debug('appDeploy_ok: update taskinfo status taskStatus=90,dealwith=close')
        'taskStatus=90,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #修改应用实例表(InstanceInfoModule)
        self.logger.debug('appDeploy_ok: update instanceinfo ip=%s,port=%s'%(app_ip,app_port))
        'status=deployed'
        iim_param = {}
        iim_param['instanceId'] = businessId
        iim_param['status'] = 'deployed'
        if app_ip is not None :
            iim_param['ip'] = app_ip
        if app_port is not None :
            iim_param['port'] = app_port 
        iim_param['beginTime'] = 'now'       
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        db.close()
        self.logger.debug('appDeploy_ok: deploy was over')
    
    #任务三 ,由mq接收到部署结果触发，task_rst.app.deploy.error
    def appDeploy_error(self, json_msg):
        """
        @summary: 任务执行结果
        @param：taskinfo 任务内容
        """
        #写任务执行结果
        #部署失败，taskStatus=10等待部署，dealwith=open
        #写应用实例信息
        self.logger.debug('appDeploy_error: received deploy error message')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        serviceId = json_msg['content']['serviceId']
        instanceId = json_msg['content']['instanceId']
        self.logger.debug('appDeploy_error: dealwithId=%s,serviceId=%s,instanceId=%s'%(dealwithId,serviceId,instanceId))
        
                
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('appDeploy_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #写任务处理表(DealwithInfoModule) 接收到的消息
        self.logger.debug('appDeploy_error: received received message to dealwithinfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('appDeploy_error: read task info by taskid=%s'%taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        taskStatus = taskinfo['taskStatus']
        if taskStatus != '40':
            self.logger.warning('appDeploy_error: task status=%s, is not 40'%taskStatus)
            return
        #读取部署询问广播次数20
        self.logger.debug('appDeploy_error: read ask times')
        dealwithInfoList = dealwithInfoModule.getById(dealwithId,'20')
        if len(dealwithInfoList) > 4 :
            #写失败
            #读取任务信息表(TaskinfoModule)
            self.logger.debug('appDeploy_error: read ask times>4,write task process error')
            taskinfoModule = TaskinfoModule(db)
            tim_param = {}
            tim_param['taskStatus'] = '91'
            tim_param['dealwith'] = 'close'
            tim_param['taskId'] = taskId
            taskinfoModule.update(tim_param)            
        
            #修改应用实例表(InstanceInfoModule)
            self.logger.debug('appDeploy_error: update instanceinfo status=failed,businessid=%s'%businessId)
            'status=failed'
            iim_param = {}
            iim_param['instanceId'] = businessId
            iim_param['status'] = 'failed'
            instanceInfoModule = InstanceInfoModule(db)
            instanceInfoModule.update(iim_param)
        else :
            #将任务表 继续部署taskStatus=10,dealwith=open
            #读取任务信息表(TaskinfoModule)
            self.logger.debug('appDeploy_error: read ask times<=4,write task process to reprocess,taskStatus=10,dealwith=open,taskId=%s'%taskId)
            taskinfoModule = TaskinfoModule(db)
            tim_param = {}
            tim_param['taskStatus'] = '10'
            tim_param['dealwith'] = 'open'
            tim_param['taskId'] = taskId
            taskinfoModule.update(tim_param)
        
        db.close()
        self.logger.debug('appDeploy_error: deploy error process was over')
    