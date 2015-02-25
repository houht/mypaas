#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models

class Serviceinfo(models.Model):
    ""
    
    serviceId = models.CharField(max_length=32,primary_key=True)
    serviceType = models.CharField(max_length=10)
    serviceName = models.CharField(max_length=256)
    status = models.CharField(max_length=10)
    protocol = models.CharField(max_length=10)
    
    

class Appinfo(models.Model):
    ""
    
    appId = models.CharField(max_length=32,primary_key=True)
    service = models.ForeignKey(Serviceinfo)
    appName = models.CharField(max_length=256,null=True)
    
    cpu = models.IntegerField()
    mem = models.IntegerField()
    disk = models.IntegerField()
    appFileId = models.CharField(max_length=32,null=True)
    
    
    appEnv = models.TextField(null=True)
    userEnv = models.TextField(null=True)
    
    domain = models.CharField(max_length=128,null=True)
    
    tokenId = models.CharField(max_length=32)
    listenPort = models.IntegerField(null=True)
    
    user = models.CharField(max_length=32,null=True)
    status = models.CharField(max_length=32,null=True)
    

class instanceinfo(models.Model):
    ""
    
    instanceId = models.CharField(max_length=32,primary_key=True)
    app = models.ForeignKey(Appinfo)
    engineId = models.CharField(max_length=32,null=True)
    
    ip = models.CharField(max_length=32,null=True)
    port = models.IntegerField(null=True)
    
    status = models.CharField(max_length=32)
    
    createTime = models.DateTimeField(auto_now_add=True,null=True)
    beginTime  = models.DateTimeField(auto_now_add=True,null=True)
    endTime = models.DateTimeField(auto_now_add=True,null=True)

    
class taskinfo(models.Model):
    ""
    
    taskId = models.CharField(max_length=32,primary_key=True)
    taskType = models.CharField(max_length=10,null=True)
    content = models.TextField(null=True)
    taskStatus = models.CharField(max_length=10,null=True)
    dealwith = models.CharField(max_length=10,null=True,db_index=True)
    createTime = models.DateTimeField(auto_now_add=True)
    business_id = models.CharField(max_length=32,null=True)
    updateTime = models.DateTimeField(auto_now_add=True)
    
class dealwithinfo(models.Model):
    ""
    
    dealwithId = models.CharField(max_length=32,primary_key=True)
    task = models.ForeignKey(taskinfo)
    
    dealwithType =  models.CharField(max_length=10,null=True)
    message = models.TextField(null=True)
    status =  models.CharField(max_length=10,null=True)
    createTime = models.DateTimeField(auto_now_add=True)
    
