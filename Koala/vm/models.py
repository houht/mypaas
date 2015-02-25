#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models



#�����
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
    
    # ״̬
    status = models.CharField(max_length=32,null=True)
    
    # ���⻯����
    vtype = models.CharField(max_length=12,null=True)
    
    # ����
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)



#�������
class vminfo(models.Model):
    ""
    
    vmId = models.CharField(max_length=32,primary_key=True)
    vmName = models.CharField(max_length=32,null=True)
    vmAlias = models.CharField(max_length=128,null=True)

    cpu = models.IntegerField()
    mem = models.IntegerField()
    size = models.IntegerField()
    
    
    # �������
    image = models.ForeignKey(image,to_field='imageId',)
    
    # nc
    engineId = models.CharField(max_length=32,null=True)
    engineIp = models.CharField(max_length=128,null=True)
    
    ip = models.CharField(max_length=32,null=True)
    
    vncPasswd = models.CharField(max_length=32,null=True)
    vncPort = models.IntegerField(null=True)
    
    username = models.CharField(max_length=32,null=True)
    password = models.CharField(max_length=32,null=True)
    
    # �����û�
    user = models.CharField(max_length=32,null=True)
    
    # vm״̬
    status = models.CharField(max_length=32,null=True)
    
    remark = models.TextField(null=True)
    
    createTime = models.DateTimeField(auto_now_add=True,null=True)
    
    tokenId = models.CharField(max_length=32)
    
    
    # ��Ч��
    beginTime  = models.DateTimeField(auto_now_add=True,null=True)
    endTime = models.DateTimeField(auto_now_add=True,null=True)


#���̱�
class disk(models.Model):
    ""
    
    
    diskId = models.CharField(max_length=32,primary_key=True)
    
    diskName = models.CharField(max_length=32,null=True)
    
    diskType = models.CharField(max_length=24,null=True)
    
    # vm ���
    vm = models.ForeignKey(vminfo)
    target =  models.CharField(max_length=10,null=True)
    size = models.IntegerField(null=True)
    
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)



#�����
class net(models.Model):
    ""
    
    netId = models.CharField(max_length=32,primary_key=True)
    
    # ����˿�
    proxyIP = models.CharField(max_length=128,null=True)
    proxyPort = models.IntegerField(null=True)
    # �������ͣ�tcp / udp
    proxyType = models.CharField(max_length=12,null=True)
    
    ip = models.CharField(max_length=128,null=True)
    port =  models.IntegerField(null=True)
    
    
    # vm ���
    vm = models.ForeignKey(vminfo)
    
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(auto_now_add=True,null=True)