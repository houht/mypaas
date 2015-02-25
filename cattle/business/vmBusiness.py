#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from cattle.utils import JsonParser
from cattle.utils import RabbitMq
from cattle.utils import LoggerUtil
from cattle.utils import UUIDUtils

from cattle.services import VmManage
from cattle.services import ConfigManage


class VmBusiness:
    ""
    
    def __init__(self):
        ""

        self.vm = VmManage()
        
        self.logger = LoggerUtil().getLogger()
        
        conf = ConfigManage()
        # mq����
        mq_conf = conf.get_mq_conf()
        self.mq_addr = mq_conf['mq_addr']
        self.task_exchange = mq_conf['task_exchange']
        self.task_type = mq_conf['task_type']
        
        # ncΨһid
        cattle_conf = conf.get_cattle_conf()
        self.engine_id = cattle_conf['engineId']
        
        # agent ip
        net_conf = conf.get_network_conf()
        self.engine_ip = net_conf['agent_ip']
        
        
        # vm type
        virtual_conf = conf.get_virtual_conf()
        self.vm_type = virtual_conf['type']

        self.messages={}
        # ��Դ��Ӧ
        res = 'task_rst'
        self.messages['vm_ask_can'] = 'vm.create.can'
        self.messages['vm_ask_router'] = res + '.vm.create.can'
        
        # ������
        self.messages['vm_create_step'] = 'vm.create.step'
        self.messages['vm_create_step_router'] = res + '.vm.create.step'
        
        # ����ʧ��
        self.messages['vm_create_error'] = 'vm.create.error'
        self.messages['vm_create_error_router'] = res  + '.vm.create.error'
        self.messages['vm_create_error_code'] = 1001
        
        # �����ɹ�
        self.messages['vm_create_ok'] = 'vm.create.ok'
        self.messages['vm_create_ok_router'] = res + '.vm.create.ok'

        # �����ɹ�
        self.messages['vm_start_ok'] = 'vm.start.ok'
        self.messages['vm_start_ok_router'] = res + '.vm.start.ok'
        
        # ����ʧ��
        self.messages['vm_start_error'] = 'vm.start.error'
        self.messages['vm_start_error_router'] = res + '.vm.start.error'
        self.messages['vm_start_error_code'] = 1002
        
        
        # �رյ�Դ�ɹ�
        self.messages['vm_destory_ok'] = 'vm.destory.ok'
        self.messages['vm_destory_ok_router'] = res + '.vm.destory.ok'
        
        # �رյ�Դʧ��
        self.messages['vm_destory_error'] = 'vm.destory.error'
        self.messages['vm_destory_error_router'] = res + '.vm.destory.error'
        self.messages['vm_destory_error_code'] = 1003
        
        # ��ػ��ɹ�
        self.messages['vm_shutdown_ok'] = 'vm.shutdown.ok'
        self.messages['vm_shutdown_ok_router'] = res + '.vm.shutdown.ok'
        
        # ��ػ�ʧ��
        self.messages['vm_shutdown_error'] = 'vm.shutdown.error'
        self.messages['vm_shutdown_error_router'] = res + '.vm.shutdown.error'
        self.messages['vm_shutdown_error_code'] = 1004
        
        
        # ��ͣ�ɹ�
        self.messages['vm_suspend_ok'] = 'vm.suspend.ok'
        self.messages['vm_suspend_ok_router'] = res + '.vm.suspend.ok'
        
        # ��ͣʧ��
        self.messages['vm_suspend_error'] = 'vm.suspend.error'
        self.messages['vm_suspend_error_router'] = res + '.vm.suspend.error'
        self.messages['vm_suspend_error_code'] = 1005
        
        
        # ����ͣ�ɹ�
        self.messages['vm_resume_ok'] = 'vm.resume.ok'
        self.messages['vm_resume_ok_router'] = res + '.vm.resume.ok'
        
        # ����ͣʧ��
        self.messages['vm_resume_error'] = 'vm.resume.error'
        self.messages['vm_resume_error_router'] = res + '.vm.resume.error'
        self.messages['vm_resume_error_code'] = 1006
        
        
        # �����޸ĳɹ�
        self.messages['vm_conf_ok'] = 'vm.conf.ok'
        self.messages['vm_conf_ok_router'] = res + '.vm.conf.ok'
        
        # �����޸�ʧ��
        self.messages['vm_conf_error'] = 'vm.conf.error'
        self.messages['vm_conf_error_router'] = res + '.vm.conf.error'
        self.messages['vm_conf_error_conf'] = 1007
        
        
        # ���Ӳ�̳ɹ�
        self.messages['vm_disk_ok'] = 'vm.disk.ok'
        self.messages['vm_disk_ok_router'] = res + '.vm.disk.ok'
        
        # ���Ӳ��ʧ��
        self.messages['vm_disk_error'] = 'vm.disk.error'
        self.messages['vm_disk_error_router'] = res + '.vm.disk.error'
        self.messages['vm_disk_error_code'] = 1008
        
        
        # ɾ��������ɹ�
        self.messages['vm_drop_ok'] = 'vm.drop.ok'
        self.messages['vm_drop_ok_router'] = res + '.vm.drop.ok'
        
        # ɾ�������ʧ��
        self.messages['vm_drop_error'] = 'vm.drop.error'
        self.messages['vm_drop_error_router'] = res + '.vm.drop.error'
        self.messages['vm_drop_error_code'] = 1009

        
        # ��ѯ������ɹ�
        self.messages['vm_find_ok'] = 'vm.find.ok'
        self.messages['vm_find_ok_router'] = res + '.vm.find.ok'
        
        # ��ѯ�����ʧ��
        self.messages['vm_find_error'] = 'vm.find.error'
        self.messages['vm_find_error_router'] = res + '.vm.find.error'
        self.messages['vm_find_error_code'] = 1010

        
    
    # ��Դ��Ӧ����
    def vm_ask(self,json_msg):
        ""
        
        # 1 ������Ϣ
        
        cpu = json_msg['content']['cpu']
        mem = json_msg['content']['mem']
        disk = json_msg['content']['disk']
        
        # 2 �ж��Ƿ���Դ����
        flag = self.vm.vm_resource(vcpus=cpu,memary=mem,disk=disk)
        
        # 3 �ж�����
        vm_type = json_msg['content']['vmType']
        if self.vm_type != vm_type:
            return
        
        # 4 ��Ӧ����
        if flag:
            response_msg = {}
            response_msg['action'] = self.messages['vm_ask_can']
            response_msg['taskId'] = json_msg['taskId']
            content_msg = {}
            
            content_msg['engineId'] = self.engine_id
            content_msg['engineIp'] = self.engine_ip
            
            response_msg['content'] = content_msg
            
            
            # ����
            self.send_msg(self.messages['vm_ask_router'],response_msg)
    
    
    # ����VM
    def vm_create(self,json_msg):
        ""
        
        
        # 1 ����vm������Ϣ
        message_step = json_msg
        message_step['action'] = self.messages['vm_create_step']
        message_step['content']['stepCode'] = 0001
        message_step['content']['stepMessage'] = 'create vm'
        self.send_msg(self.messages['vm_create_step_router'],message_step)
        
        # ������Ϣ
        message_error = json_msg
        message_error['action'] = self.messages['vm_create_error']
       
        
        # 2 ����VM
        cpu = json_msg['content']['cpu']
        mem = json_msg['content']['mem']
        disk = json_msg['content']['disk']
        image_id = json_msg['content']['imageId']
        host = UUIDUtils.getId()
        
        if 'hostName' in json_msg['content']:
            host = json_msg['content']['hostName']
        
        name = json_msg['content']['vmName']
        try:
            infos = self.vm.create_vm(image_name=image_id,vm_name=name,mem_size=mem,vcpus=cpu,vm_size=disk,host_name=host)
        except Exception , e:
            message_error['content']['errorCode'] = self.messages['vm_create_error_code']
            message_error['content']['errorMessage'] = 'create vm error: ' + str(e) 
            self.send_msg(self.messages['vm_create_error_router'],message_error)
            return
        
        
        if 'attachDisks' in  json_msg['content']:
            
            # 3 ����disk������Ϣ
            message_step = json_msg
            message_step['action'] = self.messages['vm_create_step']
            message_step['content']['stepCode'] = 0002
            message_step['content']['stepMessage'] = 'create disk'
            self.send_msg(self.messages['vm_create_step_router'],message_step)
            
            # 4 ���Ӳ��
            attach_disks =json_msg['content']['attachDisks']
            for attach_disk in attach_disks:
                hardpoints = attach_disk['hardpoints']
                disk_size = attach_disk['size']
                try:
                    self.vm.attach_disk(name,hardpoints,disk_size)
                except Exception , e:
                    message_error['content']['errorCode'] = self.messages['vm_create_error_code']
                    message_error['content']['errorMessage'] = 'create disk error: ' + str(e) 
                    self.send_msg(self.messages['vm_create_error_router'],message_error)
                    return
        
        # 5 ����������
        self.vm.set_os_hostname(name,host)
        
        
        # 6 ���ͳɹ���Ϣ
        message_ok = json_msg
        
        message_ok['content']['ip'] = infos['ip']
        message_ok['content']['vncPort'] = infos['vncPort']
        message_ok['content']['vncPasswd'] = infos['vncPasswd']
        
        message_ok['action'] = self.messages['vm_create_ok']
        self.send_msg(self.messages['vm_create_ok_router'],message_ok)
    
    # ����VM
    def vm_start(self,json_msg):
        ""
       
        name = json_msg['content']['vmName']
        try:
            self.vm.start_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_start_error_code']
            message_error['content']['errorMessage'] = 'start vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_start_error']
            self.send_msg(self.messages['vm_start_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_start_ok']
        self.send_msg(self.messages['vm_start_ok_router'],message_ok)
    
        
    # ��ػ�
    def vm_shutdown(self,json_msg):
        ""

        name = json_msg['content']['vmName']
        try:
            self.vm.shutdown_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_shutdown_error_code']
            message_error['content']['errorMessage'] = 'shutdown vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_shutdown_error']
            self.send_msg(self.messages['vm_shutdown_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_shutdown_ok']
        self.send_msg(self.messages['vm_shutdown_ok_router'],message_ok)
        
    
    
    # Ӳ�ػ�
    def vm_destroy(self,json_msg):
        ""

        name = json_msg['content']['vmName']

        
        try:
            self.vm.destroy_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_destory_error_code']
            message_error['content']['errorMessage'] = 'destroy vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_destory_error']
            self.send_msg(self.messages['vm_destory_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_destory_ok']
        self.send_msg(self.messages['vm_destory_ok_router'],message_ok)
    
    
    # ��ͣ
    def vm_suspend(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        try:
            self.vm.pause_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_suspend_error_code']
            message_error['content']['errorMessage'] = 'suspend vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_suspend_error']
            self.send_msg(self.messages['vm_suspend_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_suspend_ok']
        self.send_msg(self.messages['vm_suspend_ok_router'],message_ok)
    
    
    
    # ��ͣ�ָ�
    def vm_resume(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        try:
            self.vm.resume_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_resume_error_code']
            message_error['content']['errorMessage'] = 'resume vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_resume_error']
            self.send_msg(self.messages['vm_resume_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_resume_ok']
        self.send_msg(self.messages['vm_resume_ok_router'],message_ok)
    
    
    def vm_conf(self,json_msg):
        ""
        
        # vm����
        name = json_msg['content']['vmName']
        
        # ������Ϣ
        message_error = json_msg
        message_error['action'] = self.messages['vm_conf_error']
       
        
        # 1 �޸�cpu
        if "cpu" in json_msg['content']:
            cpu = json_msg['content']['cpu']
            try:
                self.vm.set_vm_cpu(name,cpu)
            except Exception , e:
                message_error['content']['errorCode'] = self.messages['vm_conf_error_conf']
                message_error['content']['errorMessage'] = 'conf vm vcpus error: ' + str(e) 
                self.send_msg(self.messages['vm_conf_error_router'],message_error)
                return
        
        # 2 �޸��ڴ�
        if "mem" in json_msg['content']:
            mem = json_msg['content']['mem']
            try:
                self.vm.set_vm_mem(name,mem)
            except Exception , e:
                message_error['content']['errorCode'] = self.messages['vm_conf_error_conf']
                message_error['content']['errorMessage'] = 'conf vm mem error: ' + str(e) 
                self.send_msg(self.messages['vm_conf_error_router'],message_error)
                return
        
        # 3 �޸�������,����
        if "hostName" in json_msg['content']:
            host_name = json_msg['content']['hostName']
            
        
        # 4 �޸�Ӳ�� 
        if "attachDisks" in json_msg['content']:
            attach_disks = json_msg['content']['attachDisks']
            for disk in attach_disks:
                hardpoints = disk['hardpoints']
                size = disk['size']
                try:
                    self.vm.extend_disk(name,hardpoints,size)
                except Exception , e:
                    message_error['content']['errorCode'] = self.messages['vm_conf_error_conf']
                    message_error['content']['errorMessage'] = 'conf vm disk error: ' + str(e) 
                    self.send_msg(self.messages['vm_conf_error_router'],message_error)
                    return
        
        # 5 �ɹ���Ϣ
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_conf_ok']
        self.send_msg(self.messages['vm_conf_ok_router'],message_ok)
    
    
    # vm���Ӳ��
    def vm_disk(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        hardpoints = json_msg['content']['hardpoints']
        size = json_msg['content']['size']
        
        try:
            self.vm.attach_disk(name,hardpoints,size)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_disk_error_code']
            message_error['content']['errorMessage'] = 'disk vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_disk_error']
            self.send_msg(self.messages['vm_disk_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_disk_ok']
        self.send_msg(self.messages['vm_disk_ok_router'],message_ok)
    
    
    # ɾ��vm
    def vm_drop(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        try:
            self.vm.delete_vm(name)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_drop_error_code']
            message_error['content']['errorMessage'] = 'drop vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_drop_error']
            self.send_msg(self.messages['vm_drop_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_drop_ok']
        self.send_msg(self.messages['vm_drop_ok_router'],message_ok)

    
    # ��ѯvm
    def vm_find(self,json_msg):
        ""
        
        name = None
        if 'vmName' in json_msg['content']:
            name = json_msg['content']['vmName']
        
        message_ok = json_msg
        try:
            lis = self.vm.find_vm(name)
            message_ok['content']['list'] = lis
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['vm_find_error_code']
            message_error['content']['errorMessage'] = 'find vm error: ' + str(e) 
            message_error['action'] = self.messages['vm_find_error']
            self.send_msg(self.messages['vm_find_error_router'],message_error)
            return
        
        message_ok = json_msg
        message_ok['action'] = self.messages['vm_find_ok']
        self.send_msg(self.messages['vm_find_ok_router'],message_ok)


    
    # ����mq��Ϣ 
    def send_msg(self,routing_key,message):
        ""

        self.logger.info(str(message))
        js = JsonParser()
        message = js.encode(message)
        
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.task_exchange,mq_type=self.task_type)
        mq.mq_send(msg=message,exchange_name=self.task_exchange,routing_key=routing_key)
        mq.mq_close()