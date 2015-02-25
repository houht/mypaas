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


from vm.models import vminfo,disk,net,image

#��
vm_info = 'vm_vminfo'
vm_image = 'vm_image'
vm_disk = 'vm_disk'
vm_net = 'vm_net'
task_info = 'app_taskinfo'

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
            self.vmCreate()
        elif action == "update":
            self.vmUpdate()
        elif action == "start":
            self.vmStart()
        elif action == "proxy":
            self.vmProxy()
        elif action == "destroy":
            self.vmDestroy()
        elif action == "drop":
            self.vmDrop()

    # vm����
    def vmCreate(self):
        ""
        
        taskId = self.data['taskId']
        command = self.data['command']
        
        # ����
        
        # ����
        vmAlias = command['vmAlias']
        # ���
        vmName = str(uuid.uuid1()).replace('-','')
        command['vmName'] = vmName
        
        cpu = command['cpu']
        mem = command['mem']
        size = command['size']
        imageId = command['imageId']
        
        remark = ''
        if 'remark' in command:
            remark = command['remark']
        
        vmId = str(uuid.uuid1()).replace('-','')
        status = "creating"
        
        # vminfo��
        vminfo_sql = "INSERT INTO %s (vmId,vmName,vmAlias,cpu,mem,size,image_id,status,tokenId,remark,createTime) VALUES ('%s','%s','%s',%d,%d,%d,'%s','%s','%s','%s',now())"%(vm_info,vmId,vmName,vmAlias,cpu,mem,size,imageId,status,taskId,remark)
        self.db.execute(vminfo_sql)
        
        # ���̱�
        if 'attachDisks' in command:
            attachDisks = command['attachDisks']
            for disk in attachDisks:
                target = disk['hardpoints']
                size = disk['size']
                diskId = str(uuid.uuid1()).replace('-','')
                remark = ''
                if 'remark' in disk:
                    remark = disk['remark']
                disk_sql = "INSERT INTO %s (diskId,vm_id,target,size,remark,createTime) VALUES ('%s','%s','%s',%d,'%s',now())"%(vm_disk,diskId,vmId,target,size,remark)
                self.db.execute(disk_sql)
        
        # �������
        taskId = str(uuid.uuid1()).replace('-','')
        taskType = 'vmCreate'
        taskStatus = '10'
        dealwith = 'open'
        content = str(self.js.encode(command))
        instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(task_info,taskId,taskType,content,taskStatus,dealwith,vmId)
        self.db.execute(instanceinfo_sql)
        
    
    # vm����
    def vmUpdate(self):
        ""
        
        pass
    
    
    # vmɾ��
    def vmDrop(self):
        ""
        
        command = self.data['command']
        vmId = command['vmId']
        
        info = vminfo.objects.get(vmId=vmId)
        
        status = 'dropping'
        
        # vm״̬�޸�
        info.status=status
        info.save()
        
        # ����taskinfo��
        taskId = str(uuid.uuid1()).replace('-','')
        taskType = 'vmDrop'
        taskStatus = '10'
        dealwith = 'open'
        info={}
        info['vmId'] = vmId
        content = str(self.js.encode(info))
        instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(task_info,taskId,taskType,content,taskStatus,dealwith,vmId)
        self.db.execute(instanceinfo_sql)
        
        
    
    # vm����
    def vmStart(self):
        ""
        
        command = self.data['command']
        vmId = command['vmId']
        
        info = vminfo.objects.get(vmId=vmId)
        
        status = 'starting'
        
        # vm״̬�޸�
        info.status=status
        info.save()
        
        # ����taskinfo��
        taskId = str(uuid.uuid1()).replace('-','')
        taskType = 'vmStart'
        taskStatus = '10'
        dealwith = 'open'
        info={}
        info['vmId'] = vmId
        content = str(self.js.encode(info))
        instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(task_info,taskId,taskType,content,taskStatus,dealwith,vmId)
        self.db.execute(instanceinfo_sql)
        
    
    # vm�ر�
    def vmProxy(self):
        ""
        
        command = self.data['command']
        vmId = command['vmId']
        port = command['port']
        proxyType =  command['type']
        
        info = vminfo.objects.get(vmId=vmId)
        
        ip = info.ip
#        vmName = info.vmName
#        
#        command['vmName'] = vmName
#        command['ip'] = ip
        
        netId = str(uuid.uuid1()).replace('-','')
        
        remark = ''
        if 'remark' in command:
                    remark = command['remark']
        # vm net ��
        disk_sql = "INSERT INTO %s (netId,ip,port,proxyType,vm_id,remark,createTime) VALUES ('%s','%s',%d,'%s','%s','%s',now())"%(vm_net,netId,ip,port,proxyType,vmId,remark)
        self.db.execute(disk_sql)
        
        # �����
        taskId = str(uuid.uuid1()).replace('-','')
        taskType = 'vmProxy'
        taskStatus = '10'
        dealwith = 'open'
        content = str(self.js.encode(command))
        instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(task_info,taskId,taskType,content,taskStatus,dealwith,netId)
        self.db.execute(instanceinfo_sql)
        
        
    
    # vm�ر�
    def vmDestroy(self):
        ""
        
        command = self.data['command']
        vmId = command['vmId']
        
        info = vminfo.objects.get(vmId=vmId)
        
        status = 'stopping'
        
        # vm״̬�޸�
        info.status=status
        info.save()
        
        # ����taskinfo��
        taskId = str(uuid.uuid1()).replace('-','')
        taskType = 'vmDestroy'
        taskStatus = '10'
        dealwith = 'open'
        info={}
        info['vmId'] = vmId
        content = str(self.js.encode(info))
        instanceinfo_sql = "INSERT INTO %s  VALUES ('%s','%s','%s','%s','%s',now(),'%s',now())"%(task_info,taskId,taskType,content,taskStatus,dealwith,vmId)
        self.db.execute(instanceinfo_sql)
        