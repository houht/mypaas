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

# vm删除
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
          10 : 等待删除
          20 : 删除MQ消息发送
          
          90 : 删除成功
          91 : 删除失败
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.vmDrop_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
    
    
    
    #------vmDrop------#
    #任务一
    def vmDrop_10(self, taskinfo):
        ""
        self.logger.debug('vmDrop_10: begin drop vm ')
        jsonParser = JsonParser()  
              
        businessId = taskinfo['businessId']
        taskId = taskinfo['taskId']
        
        #获取数据操作对象
        db = self.__getDb()
        # 查询vminfo表
        vm = VminfoModule(db)
        vmInfo = vm.getById(businessId)
        # 获取engineid和vmName
        engineId = vmInfo['engineId']
        vmName = vmInfo['vmName']
        
        # 发现消息
        action = 'vm.drop.apply'
        router_key = engineId + ".vm.drop.apply"
        dealwithId = UUIDUtils.getId()
        
        # 删除应用消息
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] = vmName
        message = jsonParser.encode(message)

        
        #写任务处理表库(DealwithInfoModule)
        self.logger.debug('vmDrop_10: write drop message to dealwithInfo table')
        
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '20'
        dim_param['message'] = message
        dim_param['status'] = 'success'
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        
        #开启事物
        db.begin()
        try :
            #修改任务信息表(TaskinfoModule)
            self.logger.debug('vmDrop_10: update task status')
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #发送消息
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
        
        
        #写任务执行结果
        #部署成功，taskStatus=90部署成功，dealwith=close
        #写应用实例信息
        
        self.logger.debug('vmDrop_ok: received drop vm ok from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        
        
        #获取数据操作对象
        db = self.__getDb()
        
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('vmDrop_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('vmDrop_ok: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #写任务处理表(DealwithInfoModule) 接收到的信息 
        self.logger.debug('vmDrop_ok: write received drop vm message')
    
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '90'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        dealwithInfoModule = DealwithInfoModule(db)        
        dealwithInfoModule.insert(dim_param)
        
        #修改任务信息表(TaskinfoModule)
        self.logger.debug('vmDrop_ok: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #修改vm表(VmInfoModule)
        self.logger.debug('vmDrop_ok: update VmInfo ')
        
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'destroyed'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmDrop_ok: drop vm was over')
        
    #任务三 ,由mq接收到部署结果触发，task_rst.app.deploy.error
    def vmDrop_error(self, json_msg):
        ""
        
        
        #写任务执行结果
        #部署失败，taskStatus=10等待部署，dealwith=open
        #写应用实例信息
        self.logger.debug('vmDrop_error: received deploy error message')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
  
        self.logger.debug('vmDrop_error: dealwithId=%s'%(dealwithId))
        
        
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('vmDrop_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('vmDrop_error: read task info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        
        
        #写任务处理表(DealwithInfoModule) 接收到的消息
        self.logger.debug('vmDrop_error:  received message to dealwithinfo table')
        
        
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        
        #修改任务信息表(TaskinfoModule)
        self.logger.debug('vmDrop_error: update taskinfo status taskStatus=90,dealwith=close')
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '91'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #修改应用实例表(VmInfo)
        iim_param = {}
        iim_param['vmId'] = businessId
        iim_param['status'] = 'dropFail'
        vminfo = VminfoModule(db)
        vminfo.update(iim_param)
        
        db.close()
        self.logger.debug('vmDrop_error: drop vm process was over')
    