#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from koala_task.services import InstanceInfoModule, AppInfoModule
from koala_task.services import TaskinfoModule
from koala_task.services import ConfigManage

from koala_task.utils import JsonParser
from koala_task.utils import MysqlTools
from koala_task.utils import UUIDUtils
from koala_task.utils import LoggerUtil
from koala_task.utils import UUIDUtils



# 任务响应类
class TaskProcess:
    "Task process list"

    
    def __init__(self):
        
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
    
    
    # 得到数据连接
    def __getDb(self) :
        db_conf = self.conf.get_db_conf()
        db = MysqlTools(db_conf)
        return db        
    
    
    # 任务：增加app实例
    def IncreaseInstance(self,appId):
        ""
        
        self.logger.debug('IncreaseInstance: begin')
        
        # 获取数据对象
        db = self.__getDb()
        
        jsonParser = JsonParser()
        
        
        # 1 查询app信息
        appInfoModule = AppInfoModule(db)
        appInfo = appInfoModule.getById(appId)
        # 准备参数
        command = {}
        command['domain'] = appInfo['domain']
        command['cpu'] = appInfo['cpu']
        command['mem'] = appInfo['mem']
        command['disk'] = appInfo['disk']
        command['serviceId'] = appInfo['serviceId']
        command['domain'] = appInfo['domain']
        command['appName'] = appInfo['appName']
        command['appFileId'] = appInfo['appFileId']
        command['appEnv'] = appInfo['appEnv']
        command['userEnv'] = appInfo['userEnv']
        
        # 2 新建instance
        instanceId = UUIDUtils.getId()
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['appId'] = appId
        iim_param['status'] = 'deploy'
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.insert(iim_param)
        
        # 3 新建任务
        tim_param = {}
        tim_param['taskId'] = UUIDUtils.getId()
        tim_param['taskType'] = 'appDeploy'
        tim_param['dealwith'] = 'open'
        tim_param['taskStatus'] = '10'
        tim_param['content'] = str(jsonParser.encode(command))
        tim_param['businessId'] = instanceId
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.insert(tim_param)
        
        self.logger.debug('IncreaseInstance: end')

    
    # 任务：减少app实例
    def ReduceInstance(self,instanceId):
        ""

        self.logger.debug('ReduceInstance: begin')
        # 1 更改instance状态
        iim_param = {}
        iim_param['instanceId'] = instanceId
        iim_param['status'] = 'droping'      
        instanceInfoModule = InstanceInfoModule(db)
        instanceInfoModule.update(iim_param)
        
        # 2 新建任务
        tim_param = {}
        tim_param['taskId'] = UUIDUtils.getId()
        tim_param['taskType'] = 'appDrop'
        tim_param['dealwith'] = 'open'
        tim_param['taskStatus'] = '10'
        info={}
        info['instanceId'] = instanceId
        tim_param['content'] = str(self.js.encode(info))
        tim_param['businessId'] = instanceId
        taskinfoModule = TaskinfoModule(db)
        res = taskinfoModule.insert(tim_param)
        
        self.logger.debug('ReduceInstance: end')
        
        
if __name__ == "__main__" :
    
    aa = TaskProcess()
    aa.addInstance('7912539e897c11e48a66fe5400e41488')
    
