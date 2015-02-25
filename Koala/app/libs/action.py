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


#��
appinfo = 'app_appinfo'
instanceinfos = 'app_instanceinfo'
taskinfo = 'app_taskinfo'

# ��Ӧ����
class Action() :
    ""
    
    
    def __init__(self,data) :
        ""
        
        # ��Ҫ���������
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
     
    # app����
    def appCreate(self):
        ""
        
        # 1 ��������
        taskId = self.data['taskId']
        command = self.data['command']
        
        appId = str(uuid.uuid1()).replace('-','')
        
        status = "creating"
        # 2 ����appinfo��
        
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
        
        
        # 3 ����instanceinfo��
        size = int(command['unit'])
        for i in range(0, size):
            instanceId = str(uuid.uuid1()).replace('-','')
            instanceinfo_sql = "INSERT INTO %s  (instanceId,app_id,status,createTime) VALUES ('%s','%s','%s',now())"%(instanceinfos,instanceId,appId,status)
            self.db.execute(instanceinfo_sql)
           
            # ����taskinfo��
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appDeploy'
            taskStatus = '10'
            dealwith = 'open'
            content = str(self.js.encode(command))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
    
    # app����
    def appUpdate(self):
        ""
        
        print "update"
    
    
    
    # app����
    def appStart(self):
        ""
        
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        status = 'starting'
        
        # app״̬�޸�
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        for instance in info:

            instanceId = instance.instanceId
            
            # ���±�
            instance.status=status
            instance.save()
            
            # ����taskinfo��
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appStart'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
            
    # appֹͣ
    def appStop(self):
        ""
        
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        status = 'stoping'
        
        # app״̬�޸�
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        for instance in info:

            instanceId = instance.instanceId
            
            # ���±�
            instance.status=status
            instance.save()

            # ����taskinfo��
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appStop'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
    # app ɾ��
    def appDrop(self):
        ""
        command = self.data['command']
        app = command['appId']
        info = instanceinfo.objects.filter(app=app)
        
        
        status = 'droping'
        
        # app״̬�޸�
        app = Appinfo.objects.get(appId=app)
        app.status=status
        app.save()
        
        
        for instance in info:

            instanceId = instance.instanceId
            
            # ���±�
            instance.status=status
            instance.save()
            
            # ����taskinfo��
            taskId = str(uuid.uuid1()).replace('-','')
            taskType = 'appDrop'
            taskStatus = '10'
            dealwith = 'open'
            info={}
            info['instanceId'] = instance.instanceId
            content = str(self.js.encode(info))
            instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(taskinfo,taskId,taskType,content,taskStatus,dealwith,instanceId)
            self.db.execute(instanceinfo_sql)
    
            