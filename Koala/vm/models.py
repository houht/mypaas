#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models



#镜像表
class image(models.Model):
    ""
    
    imageId = models.CharField(max_length=32,unique=True)
    imageName = models.CharField(max_length=32,null=True)
    
    system = models.CharField(max_length=32,null=True)
    version = models.CharField(max_length=12,null=True)

    arch =  models.CharField(max_length=24,null=True)
    machine = models.CharField(max_length=24,null=True)
    
    size = models.IntegerField()
    
    username = models.CharField(max_length=32,null=True)
    password = models.CharField(max_length=32,null=True)
    
    # 状态
    status = models.CharField(max_length=32,null=True)
    
    # 虚拟化类型
    vtype = models.CharField(max_length=12,null=True)
    
    # 描述
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)



#虚拟机表
class vminfo(models.Model):
    ""
    
    vmId = models.CharField(max_length=32,primary_key=True)
    vmName = models.CharField(max_length=32,null=True)
    vmAlias = models.CharField(max_length=128,null=True)

    cpu = models.IntegerField()
    mem = models.IntegerField()
    size = models.IntegerField()
    
    
    # 镜像外键
    image = models.ForeignKey(image,to_field='imageId',)
    
    # nc
    engineId = models.CharField(max_length=32,null=True)
    engineIp = models.CharField(max_length=128,null=True)
    
    ip = models.CharField(max_length=32,null=True)
    
    vncPasswd = models.CharField(max_length=32,null=True)
    vncPort = models.IntegerField(null=True)
    
    username = models.CharField(max_length=32,null=True)
    password = models.CharField(max_length=32,null=True)
    
    # 创建用户
    user = models.CharField(max_length=32,null=True)
    
    # vm状态
    status = models.CharField(max_length=32,null=True)
    
    remark = models.TextField(null=True)
    
    createTime = models.DateTimeField(auto_now_add=True,null=True)
    
    tokenId = models.CharField(max_length=32)
    
    
    # 有效期
    beginTime  = models.DateTimeField(auto_now_add=True,null=True)
    endTime = models.DateTimeField(auto_now_add=True,null=True)


#磁盘表
class disk(models.Model):
    ""
    
    
    diskId = models.CharField(max_length=32,primary_key=True)
    
    diskName = models.CharField(max_length=32,null=True)
    
    diskType = models.CharField(max_length=24,null=True)
    
    # vm 外键
    vm = models.ForeignKey(vminfo)
    target =  models.CharField(max_length=10,null=True)
    size = models.IntegerField(null=True)
    
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)



#网络表
class net(models.Model):
    ""
    
    netId = models.CharField(max_length=32,primary_key=True)
    
    # 代理端口
    proxyIP = models.CharField(max_length=128,null=True)
    proxyPort = models.IntegerField(null=True)
    # 代理类型：tcp / udp
    proxyType = models.CharField(max_length=12,null=True)
    
    ip = models.CharField(max_length=128,null=True)
    port =  models.IntegerField(null=True)
    
    
    # vm 外键
    vm = models.ForeignKey(vminfo)
    
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)