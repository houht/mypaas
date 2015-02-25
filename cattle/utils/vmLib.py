#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************


from libvirtVm import *
import json
import shutil
from threading import Thread
from command import Command


class VmLib:
    "manage vm."
    
    def __init__(self):
        
        pass
    
    #vm �����б�
    def list_vm(self):
    	"""get all vm list
    	
    	:returns: List of vm
        """
        vms = list_vms()
        return vms
    
    #vm �����б�
    def list_active(self):
    	"""get active vm list
    	
    	:returns: List of active vm
        """
        
        vms = list_active_vms()  
        return vms
    
    
    #vm �������б�
    def list_inactive(self):
    	"""get inactive vm list
    	
    	:returns: List of inactive vm
        """
        
        vms = list_inactive_vms() 
        return vms
    
    #nc��Ϣ
    def nc_info(self):
    	"""get nc node  list
    	
    	:returns: dict of nc info
        """
        
        node = node_info()
        return node
    
    #vm״̬
    def vm_states(self,vm_name=None):
        """get vm states
    	
    	:returns: dict of vm : {vmName:vmstate,...}
        """
        
        if vm_name is not None:
            states = vm_state(vm_name)
        else:
            states = vm_state()
        
        return states
    
    
    #vm����
    def start_vm(self,vm_name=None):
        "start vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] !=  "running" :
                start(vm_name)
    
    #vm�ػ� ��
    def stop_vm(self,vm_name=None):
        "stop vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running" :
                shutdown(vm_name)
    
    
    #vm�ػ� Ӳ
    def destroy_vm(self,vm_name=None):
        "destroy vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] !=  "shutdown" :
                destroy(vm_name)        
    
    
    #vm����
    def reboot_vm(self,vm_name=None):
        "reboot vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running":
                reboot(vm_name)
            
    
    #vm��ͣ
    def pause_vm(self,vm_name=None):
        "pause vm."

        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running":
                pause(vm_name)
       
    
    #vm���� �ػ���ͣ ��Ҫ restart ���� resume����
    def reset_vm(self,vm_name=None):
        "reset vm."

        if vm_name is not None:
            reset(vm_name)
    
    
    #vm��ͣ�ָ�
    def resume_vm(self,vm_name=None):
        "resume vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "paused":
                resume(vm_name)
    
    #vmǨ��
    def migrate_vm(self,vm_name=None,target=None):
        """migrate vm
    	
    	:vm_name: 
    	:target : The target nc ip
        """
        
        if vm_name is not None and target is not None:
            migrate_non_shared(vm_name,target)
        
    
    #vm�ڴ�����,Ĭ�������
    def set_mem(self,vm_name=None,memory=None,cold=True):
        """set vm memory
    	
    	:vm_name: 
    	:memory : memory size(M)
    	:Cold: is cold add
        """
        
        if vm_name is not None and memory is not None:
            if cold:
                state = self.vm_states(vm_name)
                if state[vm_name] == "running" :
                    raise CustomException("vm name is running.")
                cold_setmem(vm_name,int(memory))
            else:
                #/etc/libvirt/qemu�޸ģ���Ҫ�������ļ���������������Ч
                setmem(vm_name,memory)
                
        
    
    #vm cpu���ã��������������,Ĭ�������
    def set_vcpus(self,vm_name=None,vcpus=None,cold=True):
        """set vm vcpus
    	
    	:vm_name: 
    	:vcpus : vcpus size
    	:Cold: is cold add
        """
    
        if vm_name is not None and vcpus is not None:
            if cold:
                state = self.vm_states(vm_name)
                if state[vm_name] == "running" :
                    raise CustomException("vm name is running.")
                cold_setvcpus(vm_name,vcpus)
            else:                    
                setvcpus(vm_name,vcpus)
    
    #vm ������Ϣ
    def vm_nics(self,vm_name=None):
        "get vm nics."
        
        if vm_name is not None:
            nics = get_nics(vm_name)
            return nics
 
    #vm Ӳ����Ϣ
    def vm_disks(self,vm_name=None):
        "get vm disks."
        
        if vm_name is not None:
            disks = get_disks(vm_name)
            return disks
 
    #vm Ӳ��״̬
    def vm_disks_stats(self,vm_name=None):
        "get vm disks stats."
        
        if vm_name is not None:
            disks_stats = vm_diskstats(vm_name)
            return disks_stats
        else:
            disks_stats = vm_diskstats()
            return disks_stats

    
    #vm ����״̬
    def vm_net_stats(self,vm_name=None):
        "get vm net stats."
        
        if vm_name is not None:
            disks_stats = vm_netstats(vm_name)
            return disks_stats
        else:
            disks_stats = vm_netstats()
            return disks_stats
            

    #vm ��Ϣ
    def vm_info(self,vm_name=None):
        "get vm net stats."

        if vm_name is not None:
            infos = vm_information(vm_name)
        else:
            infos = vm_information()
        return infos
    
        
    #vm ɾ��
    def vm_delete(self,vm_name=None):
        "delete vm."
        
        if vm_name is not None:
            #1 �ж�״̬�Ƿ�ر�
            state = self.vm_states(vm_name)
            if state[vm_name] == "running" :
                self.destroy_vm(vm_name)
            #3 ����ļ�
            purge(vm_name)
            #2 ����ȡ��
            undefine(vm_name)

    
    #vm ���Ӳ�̣��ȣ�,��ʱûд
    def vm_add_disk(self,vm_name=None,size=None):
        "vm add disk."
        
        if vm_name is not None and size is not None:
            pass
            #����1 ֱ����� ��Ҫ����vm��ʽ��
            #1 ��������
            #qemu-img create -f raw test_add.img 2G ����2000M��
            #2 �������
            #virsh attach-disk sql02  /data/vm/mysql/test_add.img vdb  --cache none 
            
            #����2 ���� ֻ��raw��ʽ�ľ���ſ���
            #qemu-img resize vm2.raw +2GB 
            
    
    #���Ź��� ��������ɾ�飩,��ʱûд
    def manage_ovs(self):
        "manage ovs."
        
        pass
        #ovs-vsctl
           
    
    #openflow���� ��������ɾ�飩,��ʱûд
    def manage_openflow(self):
        "manage openflow."
    
        pass
        #ovs-ofctl
    
    #��Ӵ���
    def attach_disk(self,vm_name,disk_target,disk_file):
        ""
        
        cmd = Command()
        cmd.execute("virsh attach-disk --domain %s --source %s --target %s --persistent "%(vm_name,disk_file,disk_target))
    
    #ɾ������
    def detach_disk(self,vm_name,disk_target):
        ""
        
        cmd = Command()
        cmd.execute("virsh detach-disk --domain %s --target %s --persistent"%(vm_name,disk_target))
    
    
    #��չ����,��Ҫ����չlvm
    def extend__disk(self,vm_name,disk_target):
        ""

        pass
        
    
    #vm����
    def create_vm(self,**kwargs):
        """ method to create vm.

        Allows optional retry.
    
        :param vm_name:             the  name of create vm.
        :type vm_name:              string
        
        :param mem_size:            the  memory size of create vm.
        :type mem_size:             int(M)
        
        :param vcpus:               the vcpus number of create vm.
        :type vcpus:                int(unit)
        
        :param dev_type:            the disk type of create vm,default "hd".
        :type dev_type:             string
        
        
        :param img_vm:              the vm file of create vm.
        :type img_vm:               string
        
        :param arch:                the architecture of create vm,default "x86_64".
        :type arch:                 string
        
        :param machine:             the machine type of create vm,default "rhel6.4.0".
        :type machine:              string
        
        :param vnc_port:            the vnc port of create vm.
        :type vnc_port:             int
        
        :param vnc_passwd:          the vnc password of create vm,default "8888".
        :type vnc_passwd:           string
        
        :param interface:          the network of create vm,default "".
        :type interface:           dict,For example,[{'br_type': 'virtio', 'macs': '24:42:53:2e:52:55', 'br': 'br0', 'vif_name': 'port00001'}, {'br_type': 'virtio', 'macs': '24:42:53:2e:52:55', 'br': 'br0', 'vif_name': 'port00002'}]
        
        :param xml_path:           the conf file path of create vm.
        :type xml_path:            string
        
        
        :returns:               
        :raises:
        """
        
        vm_name = kwargs.pop('vm_name', None)
        
        
        mem_size   = kwargs.pop('mem_size', None)
        vcpus      = kwargs.pop('vcpus', None)

        img_vm     = kwargs.pop('img_vm', None)
        
        vnc_port   = kwargs.pop('vnc_port', None)
        vnc_passwd = kwargs.pop('vnc_passwd', "8888")
        
        dev_type   = kwargs.pop('dev_type', "hd")
        clock_type = kwargs.pop('clock_type', "utc")
        arch       = kwargs.pop('arch', "x86_64")
        machine    = kwargs.pop('machine', "rhel6.4.0")
        
        interfaces  = kwargs.pop('interfaces', None)
       
        #xml_path = kwargs.pop('xml_path', None)
        
        
        # 1 ����xml�ļ�
        result = create_domain_xml(vm_name,str(mem_size),str(vcpus),dev_type,img_vm,str(vnc_port),clock_type,str(vnc_passwd),arch,machine,interfaces)
        doc = Document()
        doc.appendChild(result)
        
        vm_file = img_vm.replace('.img','.xml') 
        file = open(vm_file, 'w')
        file.write(doc.toprettyxml(indent='', newl=''))
        file.close()
        
        # 2 ����vm
        cmd = Command()
        cmd.execute("virsh define %s"%vm_file)

    #��������ip�����dchp�У�ʹ��dhcp���з���
    def add_host_dhcp(groupName,mac,ip,hostname):
        return add_host_network(groupName,mac,ip,hostname)
    #��������ip��dhcp��ɾ����ȡ��dhcp����
    def del_host_dhcp(groupName,mac,ip,hostname) :
        return del_host_network(groupName,mac,ip,hostname)