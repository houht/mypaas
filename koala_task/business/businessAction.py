#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
from koala_task.utils import JsonParser
from koala_task.utils import ParserConf
from koala_task.utils import LoggerUtil
from koala_task.utils import UUIDUtils

from appDeploy import AppDeploy
from appControl import AppDControl
from appDrop import AppDrop

from vmControl import VmControl
from vmCreate import VmCreate
from vmDrop import VmDrop


class BusinessAction:
    ""

    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
    
        
    def processMq(self, action, json_msg) :
        """
        @summary: mq消息处理
        @param：action 消息类型
        @param: json_msg 消息内容
        """
        if action=='app.deploy.can' :
            appDeploy = AppDeploy()
            appDeploy.appDeploy_can(json_msg)
        elif action=='app.deploy.ok' :
            appDeploy = AppDeploy()
            appDeploy.appDeploy_ok(json_msg)
        elif action=='app.deploy.error' :
            appDeploy = AppDeploy()
            appDeploy.appDeploy_error(json_msg)
            
        elif action=='app.start.ok':
            appDControl = AppDControl()
            appDControl.appStartOk(json_msg)
        elif action=='app.start.error':
            appDControl = AppDControl()
            appDControl.appStartError(json_msg)
        elif action=='app.stop.ok':
            appDControl = AppDControl()
            appDControl.appCloseOk(json_msg)
        elif action=='app.stop.error':
            appDControl = AppDControl()
            appDControl.appCloseError(json_msg)
        elif action=='app.drop.ok':
            appDrop = AppDrop()
            appDrop.appDrop_ok(json_msg)
        elif action=='app.drop.error':
            appDrop = AppDrop()
            appDrop.appDrop_error(json_msg)
        # vm create
        if action=='vm.create.can' :
            vmCreate = VmCreate()
            vmCreate.vmCreate_can(json_msg)
        elif action=='vm.create.ok' :
            vmCreate = VmCreate()
            vmCreate.vmCreate_ok(json_msg)
        elif action=='vm.create.error' :
            vmCreate = VmCreate()
            vmCreate.vmCreate_error(json_msg)
        # vm drop
        elif action=='vm.drop.ok' :
            vmDrop = VmDrop()
            vmDrop.vmDrop_ok(json_msg)
        elif action=='vm.drop.error' :
            vmDrop = VmDrop()
            vmDrop.vmDrop_error(json_msg)
        # vm start
        elif action=='vm.start.ok' :
            vmControl = VmControl()
            vmControl.vmStartOk(json_msg)
        elif action=='vm.start.error' :
            vmControl = VmControl()
            vmControl.vmStartError(json_msg)
        # vm destory
        elif action=='vm.destory.ok' :
            vmControl = VmControl()
            vmControl.vmDestroyOk(json_msg)
        elif action=='vm.destory.error' :
            vmControl = VmControl()
            vmControl.vmDestroyError(json_msg)
        # vm proxy
        elif action=='network.portproxy.ok' :
            vmControl = VmControl()
            vmControl.vmProxyOk(json_msg)
        elif action=='network.portproxy.error' :
            vmControl = VmControl()
            vmControl.vmProxyError(json_msg)
        else :
            print 'error'  
        pass
    
    
    def processTask(self, taskinfo) :
        """
        @summary: 任务处理
        @param：taskinfo 消息内容
        """
        self.logger.error("processTask in")
        taskId = taskinfo['taskId']
        taskType = taskinfo['taskType']
        taskStatus = taskinfo['taskStatus']
        self.logger.debug('begin process task:(taskId:'+taskId+",taskType:"+taskType+",taskStatus:"+taskStatus+")")
        if taskType == 'appDeploy' :
            appDeploy = AppDeploy()
            appDeploy.appDeploy(taskinfo)
        elif taskType == 'appStart' :
            appDControl = AppDControl()
            appDControl.appStart(taskinfo)
        elif taskType == 'appStop' :
            appDControl = AppDControl()
            appDControl.appClose(taskinfo)
        elif taskType == 'appDrop' :
            appDrop = AppDrop()
            appDrop.appDrop(taskinfo)
        elif taskType == 'vmCreate' :
            vmCreate = VmCreate()
            vmCreate.vmCreate(taskinfo)
        elif taskType == 'vmDrop' :
            vmDrop = VmDrop()
            vmDrop.vmDrop(taskinfo)
        elif taskType == 'vmStart' :
            vmControl = VmControl()
            vmControl.vmStart(taskinfo)
        elif taskType == 'vmDestroy' :
            vmControl = VmControl()
            vmControl.vmDestroy(taskinfo)
        elif taskType == 'vmProxy' :
            vmControl = VmControl()
            vmControl.vmProxy(taskinfo)  
        else :
            self.logger.warning('Not support taskinfo,taskId:'+taskId+',taskType:'+taskType)
    
