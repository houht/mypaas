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
    
    #vm 所有列表
    def list_vm(self):
    	"""get all vm list
    	
    	:returns: List of vm
        """
        vms = list_vms()
        return vms
    
    #vm 运行列表
    def list_active(self):
    	"""get active vm list
    	
    	:returns: List of active vm
        """
        
        vms = list_active_vms()  
        return vms
    
    
    #vm 非运行列表
    def list_inactive(self):
    	"""get inactive vm list
    	
    	:returns: List of inactive vm
        """
        
        vms = list_inactive_vms() 
        return vms
    
    #nc信息
    def nc_info(self):
    	"""get nc node  list
    	
    	:returns: dict of nc info
        """
        
        node = node_info()
        return node
    
    #vm状态
    def vm_states(self,vm_name=None):
        """get vm states
    	
    	:returns: dict of vm : {vmName:vmstate,...}
        """
        
        if vm_name is not None:
            states = vm_state(vm_name)
        else:
            states = vm_state()
        
        return states
    
    
    #vm启动
    def start_vm(self,vm_name=None):
        "start vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] !=  "running" :
                start(vm_name)
    
    #vm关机 软
    def stop_vm(self,vm_name=None):
        "stop vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running" :
                shutdown(vm_name)
    
    
    #vm关机 硬
    def destroy_vm(self,vm_name=None):
        "destroy vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] !=  "shutdown" :
                destroy(vm_name)        
    
    
    #vm重启
    def reboot_vm(self,vm_name=None):
        "reboot vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running":
                reboot(vm_name)
            
    
    #vm暂停
    def pause_vm(self,vm_name=None):
        "pause vm."

        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "running":
                pause(vm_name)
       
    
    #vm重设 关机暂停 需要 restart 或者 resume重启
    def reset_vm(self,vm_name=None):
        "reset vm."

        if vm_name is not None:
            reset(vm_name)
    
    
    #vm暂停恢复
    def resume_vm(self,vm_name=None):
        "resume vm."
        
        if vm_name is not None:
            state = self.vm_states(vm_name)
            if state[vm_name] ==  "paused":
                resume(vm_name)
    
    #vm迁移
    def migrate_vm(self,vm_name=None,target=None):
        """migrate vm
    	
    	:vm_name: 
    	:target : The target nc ip
        """
        
        if vm_name is not None and target is not None:
            migrate_non_shared(vm_name,target)
        
    
    #vm内存设置,默认冷添加
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
                #/etc/libvirt/qemu修改，需要改配置文件，否则重启不生效
                setmem(vm_name,memory)
                
        
    
    #vm cpu设置，热添加暂有问题,默认冷添加
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
    
    #vm 网卡信息
    def vm_nics(self,vm_name=None):
        "get vm nics."
        
        if vm_name is not None:
            nics = get_nics(vm_name)
            return nics
 
    #vm 硬盘信息
    def vm_disks(self,vm_name=None):
        "get vm disks."
        
        if vm_name is not None:
            disks = get_disks(vm_name)
            return disks
 
    #vm 硬盘状态
    def vm_disks_stats(self,vm_name=None):
        "get vm disks stats."
        
        if vm_name is not None:
            disks_stats = vm_diskstats(vm_name)
            return disks_stats
        else:
            disks_stats = vm_diskstats()
            return disks_stats

    
    #vm 网络状态
    def vm_net_stats(self,vm_name=None):
        "get vm net stats."
        
        if vm_name is not None:
            disks_stats = vm_netstats(vm_name)
            return disks_stats
        else:
            disks_stats = vm_netstats()
            return disks_stats
            

    #vm 信息
    def vm_info(self,vm_name=None):
        "get vm net stats."

        if vm_name is not None:
            infos = vm_information(vm_name)
        else:
            infos = vm_information()
        return infos
    
        
    #vm 删除
    def vm_delete(self,vm_name=None):
        "delete vm."
        
        if vm_name is not None:
            #1 判断状态是否关闭
            state = self.vm_states(vm_name)
            if state[vm_name] == "running" :
                self.destroy_vm(vm_name)
            #3 清除文件
            purge(vm_name)
            #2 定义取消
            undefine(vm_name)

    
    #vm 添加硬盘（热）,暂时没写
    def vm_add_disk(self,vm_name=None,size=None):
        "vm add disk."
        
        if vm_name is not None and size is not None:
            pass
            #方法1 直接添加 需要进入vm格式化
            #1 创建磁盘
            #qemu-img create -f raw test_add.img 2G （或2000M）
            #2 磁盘添加
            #virsh attach-disk sql02  /data/vm/mysql/test_add.img vdb  --cache none 
            
            #方法2 拉伸 只有raw格式的镜像才可以
            #qemu-img resize vm2.raw +2GB 
            
    
    #网桥管理 包括（增删查）,暂时没写
    def manage_ovs(self):
        "manage ovs."
        
        pass
        #ovs-vsctl
           
    
    #openflow管理 包括（增删查）,暂时没写
    def manage_openflow(self):
        "manage openflow."
    
        pass
        #ovs-ofctl
    
    #添加磁盘
    def attach_disk(self,vm_name,disk_target,disk_file):
        ""
        
        cmd = Command()
        cmd.execute("virsh attach-disk --domain %s --source %s --target %s --persistent "%(vm_name,disk_file,disk_target))
    
    #删除磁盘
    def detach_disk(self,vm_name,disk_target):
        ""
        
        cmd = Command()
        cmd.execute("virsh detach-disk --domain %s --target %s --persistent"%(vm_name,disk_target))
    
    
    #扩展磁盘,主要是扩展lvm
    def extend__disk(self,vm_name,disk_target):
        ""

        pass
        
    
    #vm创建
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
        
        
        # 1 生成xml文件
        result = create_domain_xml(vm_name,str(mem_size),str(vcpus),dev_type,img_vm,str(vnc_port),clock_type,str(vnc_passwd),arch,machine,interfaces)
        doc = Document()
        doc.appendChild(result)
        
        vm_file = img_vm.replace('.img','.xml') 
        file = open(vm_file, 'w')
        file.write(doc.toprettyxml(indent='', newl=''))
        file.close()
        
        # 2 定义vm
        cmd = Command()
        cmd.execute("virsh define %s"%vm_file)

    #将主机的ip加入的dchp中，使用dhcp进行分配
    def add_host_dhcp(groupName,mac,ip,hostname):
        return add_host_network(groupName,mac,ip,hostname)
    #将主机的ip从dhcp中删除，取消dhcp分配
    def del_host_dhcp(groupName,mac,ip,hostname) :
        return del_host_network(groupName,mac,ip,hostname)