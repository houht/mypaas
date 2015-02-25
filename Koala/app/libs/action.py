#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from dbTool import DbTool

from cattle.utils import JsonParser

import uuid
import time


from app.models import Appinfo,instanceinfo


#表
appinfo = 'app_appinfo'
instanceinfos = 'app_instanceinfo'
taskinfo = 'app_taskinfo'

# 响应处理
class Action() :
    ""
    
    
    def __init__(self,data) :
        ""
        
        # 需要处理的数据
        self.data = data
        self.db = DbTool()
        self.js = JsonParser()
        
        
        self.process()
        
    
    
    def process(self):
        ""
        
        
        action = self.data['action']
        
        if action == "create":
            self.appCreate()
        elif action == "update":
            self.appUpdate()
        elif action == "start":
            self.appStart()
        elif action == "stop":
            self.appStop()
        elif action == "drop":
            self.appDrop()
     
    # app创建
    def appCreate(self):
        ""
        
        # 1 解析数据
        taskId = self.data['taskId']
        command = self.data['command']
        
        appId = str(uuid.uuid1()).replace('-','')
        
        status = "creating"
        # 2 更新appinfo表
        
        if 'appFileId' not in command:
            command['appFileId'] = ""
        if 'appEnv' not in command:
            command['appEnv'] = ""
        if 'userEnv' not in command:
            command['userEnv'] = ""
        if 'domain' not in command:
            command['domain'] = "" 
        
        if 'user' not in command:
            command['user'] = "" 
        
        
        status = "deploy"
        appinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s',%d,%d,%d,'%s','%s','%s','%s','%s',%d,'%s','%s')"%(appinfo,appId,command['serviceId'],command['appName'],command['cpu'],command['mem'],command['disk'],command['appFileId'],command['appEnv'],command['userEnv'],command['domain'],taskId,0,command['user'],status)
        self.db.execute(appinfo_sql)
        
        
        # 3 更新instanceinfo表
        size = int(command['unit'])
        for i in range(0, size):
            instanceId = str(uuid.uuid1()).replace('-','')
            instanceinfo_sql = "INSERT INTO %s  (instanceId,app_id,status,createTime) VALUES ('%s','%s','%s',now())"%(instanceinfos,instanceId,appId,status)
            self.db.execute(instanceinfo_sql)
           
            # 更新taskinfo表
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appDeploy'
            taskStatus = '10'
            dealwith = 'open'
            content = str(self.js.encode(command))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
    
    # app更新
    def appUpdate(self):
        ""
        
        print "update"
    
    
    
    # app启动
    def appStart(self):
        ""
        
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        status = 'starting'
        
        # app状态修改
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        for instance in info:

            instanceId = instance.instanceId
            
            # 更新表
            instance.status=status
            instance.save()
            
            # 插入taskinfo表
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appStart'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
            
    # app停止
    def appStop(self):
        ""
        
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        status = 'stoping'
        
        # app状态修改
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        for instance in info:

            instanceId = instance.instanceId
            
            # 更新表
            instance.status=status
            instance.save()

            # 插入taskinfo表
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appStop'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
    # app 删除
    def appDrop(self):
        ""
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        
        status = 'droping'
        
        # app状态修改
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        
        for instance in info:

            instanceId = instance.instanceId
            
            # 更新表
            instance.status=status
            instance.save()
            
            # 插入taskinfo表
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appDrop'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
            