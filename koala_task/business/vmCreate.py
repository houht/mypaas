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
        @summary: 软件创建任务
        @param：taskinfo 任务内容
        taskStatus :
          10 : 等待创建
          20 : 创建询问广播
          30 : 接收资源应答
          40 : 创建申请
          90 : 创建成功
          91 : 创建失败
        """
        taskId = taskinfo['taskId']        
        taskStatus = taskinfo['taskStatus']        
        if taskStatus == '10':
            self.vmCreate_10(taskinfo)
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskStatus:'+taskStatus)
     
    #------vmdeploy------#
    #任务一
    def vmCreate_10(self, taskinfo):
        """
        @summary: 待创建任务
        @param：taskinfo 任务内容
        """
        #发送ask广播action=bdct.vm.deploy.ask
        #更改taskStatus=20等待资源，dealwith=close
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
        
        
        #获取数据操作对象
        db = self.__getDb()
        router_key = 'bdct.vm.create.ask'
        action = 'vm.create.ask'
        dealwithId = UUIDUtils.getId()
        
        
        # 查询vm类型
        vmImage = VmImageModule(db)
        ImageInfo = vmImage.getByImageId(imageId)
        vmType = ImageInfo['vtype']
        
        #创建询问广播消息
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['vmType'] = vmType
        message = jsonParser.encode(message)
        
        #写任务处理表库(DealwithInfoModule)
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
        #开启事物
        db.begin()
        try :
            #修改任务信息表(TaskinfoModule)
            self.logger.debug('vmCreate_10: update task status')
            
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '20'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #发送广播消息
            self.logger.debug('vmCreate_10: send ask message to the bdct of mq')
            self.mq.send_bdct_message(router_key, message)
            db.end()
            self.logger.debug('vmCreate_10: process task is over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.error('vmCreate_10: process task error, error message: '+str(e))
            
        finally :
            db.close()
     
    #任务二，由mq接收到广播应答触发
    def vmCreate_can(self, json_msg):
        """
        @summary: 资源应答处理，向第一个应答的引擎下发创建任务
        @param：taskinfo 任务内容
        """
        
        #发送创建任务 action=task_rst.vm.deploy.can
        #更改taskStatus=30等待创建结果，dealwith=close
        #写应用实例信息
        self.logger.debug('vmCreate_can: received vmcreate ask reply from mq')
        jsonParser = JsonParser()
        
        dealwithId = json_msg['taskId']
        engineId = json_msg['content']['engineId']
        engineIp = json_msg['content']['engineIp']
        
        self.logger.debug('vmCreate_can: reply engineId: '+engineId+",taskId: "+dealwithId)
        
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('vmCreate_can: read task dealwithinfo by dealwithid: '+dealwithId)
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('vmCreate_can: read task info by taskId: '+taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        if taskStatus != '20' :
            '已经接收到资源应答，并且执行了创建'
            self.logger.debug('vmCreate_can: the task has  access to resources: taskStatus:'+taskStatus)
            return
            
        #写任务处理表(DealwithInfoModule) 接收应答 
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
        
        
        #创建申请开始-----------------------------
        self.logger.debug('vmCreate_can: begin deploy the task to engine')
        contentObj = jsonParser.decode(content)
        #资源参数
        vmName = contentObj['vmName']
        cpu = contentObj['cpu']
        mem = contentObj['mem']
        disk = contentObj['size']
        imageId = contentObj['imageId']
        
        # 查询vm类型
        vmImage = VmImageModule(db)
        ImageInfo = vmImage.getByImageId(imageId)
        vmType = ImageInfo['vtype']
        
        action = 'vm.create.apply'
        router_key = engineId + ".vm.create.apply"
        dealwithId = UUIDUtils.getId()
        
        #创建创建申请消息
        message = {}
        message['action'] = action
        message['taskId'] = dealwithId
        message['content'] = {}
        message['content']['vmName'] =  vmName
        message['content']['cpu'] = cpu
        message['content']['mem'] = mem
        message['content']['disk'] = disk
        message['content']['vmType'] = vmType
        # 磁盘
        if 'attachDisks' in contentObj:
            message['content']['attachDisks'] = contentObj['attachDisks']
        # 主机名
        if 'hostName' in contentObj:
            message['content']['hostName'] = contentObj['hostName']
        
        message['content']['imageId'] = imageId 
        message = jsonParser.encode(message) 
        
        # 暂时没有
        # host
        # attachDisks
        
        #写任务处理表(DealwithInfoModule) 创建申请
        self.logger.debug('vmCreate_can: write deploy message to dealwithinfo table')
        dim_param = {}
        dim_param['dealwithId'] = dealwithId
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '40'
        dim_param['message'] = message
        dim_param['status'] = 'success'        
        dealwithInfoModule.insert(dim_param)
        
        #开启事物
        self.logger.debug('vmCreate_can: begin change the task status')
        db.begin()
        try :
            #修改任务信息表(TaskinfoModule)
            self.logger.debug('vmCreate_can: update task status taskStatus=40 and dealwith=close')
            
            tim_param = {}
            tim_param['taskId'] = taskId
            tim_param['taskStatus'] = '40'
            tim_param['dealwith'] = 'close'
            taskinfoModule = TaskinfoModule(db)
            res = taskinfoModule.update(tim_param)
            
            #修改应用实例表(InstanceInfoModule)
            self.logger.debug('vmCreate_can: update vminfo engineId=%s'%engineId)
            
            iim_param = {}
            iim_param['vmId'] = businessId
            iim_param['engineId'] = engineId
            iim_param['engineIp'] = engineIp
            #engineIp
            vminfo = VminfoModule(db)
            vminfo.update(iim_param)
            
            #发送广播消息
            self.logger.debug('vmCreate_can: send deploy request to task of mq')
            self.mq.send_task_message(router_key, message)
            db.end()
            self.logger.debug('vmCreate_can: send deploy request was over')
        except Exception,e:
            db.end(option='rollback')
            self.logger.debug('vmCreate_can: process status error, error message: '+str(e))
        finally :
            db.close()
    
    #任务三 ,由mq接收到创建结果触发，task_rst.app.deploy.ok
    def vmCreate_ok(self, json_msg):
        """
        @summary: 任务执行结果
        @param：taskinfo 任务内容
        """
        #写任务执行结果
        #创建成功，taskStatus=90创建成功，dealwith=close
        #写应用实例信息
        self.logger.debug('vmCreate_ok: received deploy ok from mq')
        jsonParser = JsonParser()
        
        # 返回参数
        dealwithId = json_msg['taskId']
        ip = json_msg['content']['ip']
        vncPort = json_msg['content']['vncPort']
        vncPasswd = json_msg['content']['vncPasswd']
        
        self.logger.debug('vmCreate_ok: received dealwithId: %s ' % dealwithId)
        
        
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('vmCreate_ok: read dealwithinfo')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('vmCreate_ok: read tas info')
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        content = taskinfo['content']
        taskStatus = taskinfo['taskStatus']
        
        #写任务处理表(DealwithInfoModule) 接收到的信息 
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
        
        #修改任务信息表(TaskinfoModule)
        self.logger.debug('vmCreate_ok: update taskinfo status taskStatus=90,dealwith=close')
        'taskStatus=90,dealwith=close'
        tim_param = {}
        tim_param['taskId'] = taskId
        tim_param['taskStatus'] = '90'
        tim_param['dealwith'] = 'close'
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.update(tim_param)
        
        #修改应用实例表(InstanceInfoModule)
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
    
    #任务三 ,由mq接收到创建结果触发，task_rst.app.deploy.error
    def vmCreate_error(self, json_msg):
        """
        @summary: 任务执行结果
        @param：taskinfo 任务内容
        """
        #写任务执行结果
        #创建失败，taskStatus=10等待创建，dealwith=open
        #写应用实例信息
        self.logger.debug('vmCreate_error: received deploy error message')
        jsonParser = JsonParser() 
        dealwithId = json_msg['taskId']
        
        self.logger.debug('vmCreate_error: dealwithId=%s'%dealwithId)
                
        #获取数据操作对象
        db = self.__getDb()
        
        #读取任务处理表(DealwithInfoModule)
        self.logger.debug('vmCreate_error: read dealwithinfo by dealwithid')
        dealwithInfoModule = DealwithInfoModule(db)
        dealwithInfo = dealwithInfoModule.getById(dealwithId)
        taskId = dealwithInfo['taskId']
        
        #写任务处理表(DealwithInfoModule) 接收到的消息
        self.logger.debug('vmCreate_error: received received message to dealwithinfo table')
        'dealwithId,taskId,dealwithType,message,status'
        dim_param = {}
        dim_param['dealwithId'] = UUIDUtils.getId()
        dim_param['taskId'] = taskId
        dim_param['dealwithType'] = '91'
        dim_param['message'] = jsonParser.encode(json_msg)
        dim_param['status'] = 'success'
        
        #读取任务信息表(TaskinfoModule)
        self.logger.debug('vmCreate_error: read task info by taskid=%s'%taskId)
        taskinfoModule = TaskinfoModule(db)
        taskinfo = taskinfoModule.getById(taskId)
        businessId = taskinfo['businessId']
        taskStatus = taskinfo['taskStatus']
        if taskStatus != '40':
            self.logger.warning('vmCreate_error: task status=%s, is not 40'%taskStatus)
            return
        #读取创建询问广播次数20
        self.logger.debug('vmCreate_error: read ask times')
        dealwithInfoList = dealwithInfoModule.getById(dealwithId,'20')
        if len(dealwithInfoList) > 4 :
            #写失败
            #读取任务信息表(TaskinfoModule)
            self.logger.debug('vmCreate_error: read ask times>4,write task process error')
            taskinfoModule = TaskinfoModule(db)
            tim_param = {}
            tim_param['taskStatus'] = '91'
            tim_param['dealwith'] = 'close'
            tim_param['taskId'] = taskId
            taskinfoModule.update(tim_param)            
        
            #修改应用实例表(InstanceInfoModule)
            self.logger.debug('vmCreate_error: update vminfo status=failed,businessid=%s'%businessId)
            
            iim_param = {}
            iim_param['vmId'] = businessId
            iim_param['status'] = 'createFail'
            
            vminfo = VminfoModule(db)
            vminfo.update(iim_param)
        else :
            #将任务表 继续创建taskStatus=10,dealwith=open
            #读取任务信息表(TaskinfoModule)
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