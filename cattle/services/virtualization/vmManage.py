#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import os
import random
import time


from cattle.utils import VmLib
from cattle.utils import CustomException
from cattle.utils import QemuTools
from cattle.utils import SqliteTools
from cattle.utils import JsonParser
from cattle.utils import WinRegedit
from cattle.utils import VirtGuestfs


from cattle.services import ConfigManage
from cattle.services import StorageManage
from cattle.services import ImageManage
from cattle.services import NetworkService



VMTABLE = "vm"
DISKTABLE = "vmDisk"
VMPROXY = "vmProxy"


class VmManage:
    "virtualization management"
    
    
    def __init__(self,vm_name=None):
        ""

        self.vm = VmLib()
        self.conf = ConfigManage()
        self.image = ImageManage()
        self.storageManage = StorageManage()
        self.qemu = QemuTools()
        self.vm_tools = VmLib()
        self.net = NetworkService()
    
    
    # ��ѯ���ݿⵥ��vm��Ϣ
    def info_vm(self,vm_name):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        
        fetchone_sql = 'SELECT * FROM %s WHERE vmName = ? '%VMTABLE
        data = vm_name
        item = sql_tools.fetchone(fetchone_sql,data)
        infos = {}
        if item is not None:
            infos['vm_name']      = item[0]
            infos['vm_file']      = item[1]
            infos['image_name']   = item[2]
            infos['image_file']   = item[3]
            infos['vm_size']      = item[4]
            infos['mem_size']     = item[5]
            infos['vcpus']        = item[6]
            
            infos['vnc_port']     = item[7]
            infos['vnc_passwd']   = item[8]
            infos['interfaces']   = item[9]
            infos['ip']           = item[10]
            
            infos['createtime']   = item[11]
            infos['remark']       = item[12]
        else:
            return None
            
        return infos
    
    # ��ѯ���ݿ�����vm��Ϣ
    def info_vms(self):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        
        fetchall_sql = 'SELECT * FROM %s '%VMTABLE
        infos = sql_tools.fetchall(fetchall_sql)
        vms = []
        for item in infos:
            vm = {}
            if item is not None:
                vm['vm_name']      = item[0]
                vm['vm_file']      = item[1]
                vm['image_name']   = item[2]
                vm['image_file']   = item[3]
                vm['vm_size']      = item[4]
                vm['mem_size']     = item[5]
                vm['vcpus']        = item[6]
                
                vm['vnc_port']     = item[7]
                vm['vnc_passwd']   = item[8]
                vm['interfaces']   = item[9]
                vm['ip']           = item[10]
                
                vm['createtime']   = item[11]
                vm['remark']       = item[12]
            vms.append(vm)
        
        
        return vms
    
    
    def find_vm(self,vm_name=None):
        ""
      
      
        sql = "select * from %s where 1=1" % VMTABLE
        data = ()
        cond_conf = ''
        
        if vm_name is not None :
            cond_conf += ' and vmName=?'
            data += (vm_name,)
            
            
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        if len(data) > 0 :
            sql += cond_conf
            infos = sql_tools.fetchall(sql,data)
        else :
            infos = sql_tools.fetchall(sql)
        
        vms = []
        for item in infos:
            vm = {}
            if item is not None:
                vm['vmName']      = item[0]
                #vm['vm_file']      = item[1]
                vm['imageName']   = item[2]
                #vm['image_file']   = item[3]
                vm['vmSize']      = item[4]
                vm['memSize']     = item[5]
                vm['vcpus']        = item[6]
                
                vm['vncPort']     = item[7]
                vm['vncPasswd']   = item[8]
                vm['interfaces']   = item[9]
                vm['ip']           = item[10]
                
                vm['createtime']   = item[11]
                vm['remark']       = item[12]
            vms.append(vm)
        
        
        return vms
        
        
        
        
    
    # ��ѯvm�����д���
    def info_disks(self,vm_name):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        
        fetchall_sql = 'SELECT * FROM %s where vmName = ?'%DISKTABLE
        data = (vm_name,)
        infos = sql_tools.fetchall(fetchall_sql,data)
        disks = []
        for item in infos:
            disk = {}
            if item is not None:
                disk['vm_name']     = item[0]
                
                disk['disk_size']   = item[1]
                disk['disk_name']   = item[2]
                disk['disk_target'] = item[3]
                disk['disk_file']   = item[4]
                disk['disk_type']   = item[5]

                disk['createtime']  = item[6]
                disk['remark']      = item[7]
            disks.append(disk)
        
        return disks
        
    
    
    # �жϴ����Ƿ����
    def exist_disk(self,disk_name):
        ""
        
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        
        fetchall_sql = 'SELECT * FROM %s where diskName = ?'%DISKTABLE
        data = disk_name
        infos = sql_tools.fetchone(fetchall_sql,data)
        if infos is None:
            return False
        else:
            return True
        
    # vm����Ƿ����
    def check(self,vm_name):
        ""
        
        if vm_name is None:
            raise CustomException("vm name is None.")
            return
        
        if self.info_vm(vm_name) is None:
            raise CustomException("vm is not exists.")
            return
    
    # ����VM
    def create_vm(self,**kwargs):
        ""
        
        image_name = kwargs.pop('image_name', None)
        vm_name    = kwargs.pop('vm_name', None)
        # VM��С����λM
        vm_size    = kwargs.pop('vm_size', None)
        # �ڴ��С����λM
        mem_size   = kwargs.pop('mem_size', None)
        # cpu��С����λ����
        vcpus      = kwargs.pop('vcpus', None)
        host_name  = kwargs.pop('host_name', "")
        
        
        infos = {}
        
        
        # �ж�
        if vm_name is None:
            raise CustomException("vm name is None.")
            return
        
        if self.info_vm(vm_name) is not None:
            raise CustomException("vm is exists.")
            return
        
        # 1 �жϾ����ļ��Ƿ���ڣ��ж��Ƿ�����
        try:
            image_file = self.image.download_image(image_name)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
        img_infos = self.image.info_image(image_name)
        
        arch = img_infos['arch']
        machine = img_infos['machine']
        
        # 2 ����lvm
        lvm_mount_dir = self.storageManage.create_lvm(lvm_name=vm_name,lvm_size=vm_size,mount=True)
        
        # 3 ���ڸ�����img
        vm_file = os.path.join(lvm_mount_dir,vm_name+'.img') 
        self.qemu.create_img(basefile=image_file,filename=vm_file)
       
        # 4 ��ѯ������Ϣ
        interfaces = []
        interface = {}
        try:
            info = self.net.fixedIpRegister(hostName=host_name)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
        ip = info['ipAddress']
        
        interface['ip'] = info['ipAddress']
        interface['br_type'] = 'virtio'
        interface['br'] = info['groupName']
        interface['vif_name'] = info['ifName']
        interface['macs'] = info['macAddress']
        interfaces.append(interface)
        
        infos['ip'] = info['ipAddress']
        
        # 5 �õ�vnc port
        vnc_port = self.get_vnc_port()
        if vnc_port is None:
            raise CustomException("Error: vnc port is none.")
        
        # 6 ����vm
        
        # vnc���룬������� 
        vnc_passwd = random.randint(1000,9999)
        
        infos['vncPort'] = vnc_port
        infos['vncPasswd'] = vnc_passwd

        try:
            self.vm_tools.create_vm(vm_name=vm_name,
                               mem_size=mem_size,
                               vcpus=vcpus,
                               img_vm=vm_file,
                               vnc_port=vnc_port,
                               vnc_passwd=vnc_passwd,
                               arch=arch,
                               machine=machine,
                               interfaces=interfaces)
        except Exception , e:
            for tmp in interfaces:
                ip = tmp['ip']
                br = tmp['br']
                self.net.fixedIpRemove(br, ip)
            raise CustomException("Error: %s" % str(e) )
        
        
        # 7 �������ݿ�
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        save_sql = '''INSERT INTO %s values (?, ?, ?,?, ?,?,?,?,?,?,?,?,?)'''%VMTABLE
        data = [(vm_name, vm_file,image_name,image_file,vm_size, mem_size,vcpus,vnc_port,vnc_passwd,str(interfaces),ip,time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)
    
        
        return infos
       
    def config_vm(self):
        ""
        
        pass
    
    # Ӳ�ػ�
    def destroy_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.destroy_vm(vm_name)
    
    # ��ػ� 
    def shutdown_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.stop_vm(vm_name)
    
    # virsh list --all
    def list_vm(self):
        ""
        
        return self.vm_tools.list_vm()
    
    
    # ���������
    def start_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.start_vm(vm_name)
    
    
    # ����״̬
    def state_vm(self,vm_name=None):
        ""
        
        self.check(vm_name)
        return self.vm_tools.vm_states(vm_name)
    
    
    #�޸��ڴ棬��λM���ػ��޸�(����������ڴ棿)
    def set_vm_mem(self,vm_name,size):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        # 2 �����ڴ�
        self.vm_tools.set_mem(vm_name=vm_name,memory=size)
        
        # 3 �޸����ݿ�
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET memSize = ? WHERE vmName = ? '%VMTABLE
        data = [(size, vm_name)]
        sql_tools.update(update_sql,data)


    
    #�޸�cpu����λ�������ػ��޸�
    def set_vm_cpu(self,vm_name,vcpus):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ����cpu
        self.vm_tools.set_vcpus(vm_name=vm_name,vcpus=vcpus)
        
        # 3 �޸����ݿ�
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET vcpus = ? WHERE vmName = ? '%VMTABLE
        data = [(vcpus, vm_name)]
        sql_tools.update(update_sql,data)

    
    # ��ͣ
    def pause_vm(self,vm_name):
        ""
        
        # 1 ���
        self.check(vm_name)

        # 2 ��ͣ
        self.vm_tools.pause_vm(vm_name)
    
    # ��ͣ�ָ�
    def resume_vm(self,vm_name):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ����ͣ
        self.vm_tools.resume_vm(vm_name)
    
    
    # ����
    def reboot_vm(self,vm_name):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ����
        self.vm_tools.reboot_vm(vm_name)
        

    # ɾ�������
    def delete_vm(self,vm_name=None):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ɾ��vm��ȡ������
        self.vm_tools.vm_delete(vm_name)
        
        # 3 ɾ��lvm
        try:
            self.storageManage.remove_lvm(vm_name,True)
        except Exception , e:
            raise CustomException("Error: remove lvm failed!")
        
        # 4 ɾ������
        vm_info = self.info_vm(vm_name)
        js = JsonParser()
        if vm_info is not None:
            tmps = js.decode(vm_info['interfaces'].replace('\'','\"'))
            for tmp in tmps:
                ip = tmp['ip']
                br = tmp['br']
                self.net.fixedIpRemove(br, ip)
        
        # 5 ɾ������˿�
        proxy_infos = self.proxy_list(vm_name = vm_name)
        for proxy_info in proxy_infos:
            self.proxy_del(vm_name = proxy_info["vmName"],ip = proxy_info["ip"],port = proxy_info["port"])
        
        
        # 6 �ж��Ƿ�����ӵĴ��̣�ɾ��
        disks = self.info_disks(vm_name)
        for disk in disks:
            self.detach_disk(vm_name,disk['disk_name'])
            
        
        # 7 ɾ�����ݿ�
        delete_sql = 'DELETE FROM %s WHERE vmName = ? '%VMTABLE
        data = [(vm_name,)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
        
    def control_vm(self):
        ""
        
        pass

    # ��Ӵ��̣�disk_size ���̴�С����λM
    def attach_disk(self,vm_name,target,disk_size):
        ""

        # 1 ���
        self.check(vm_name)

        disk_name = vm_name+"_"+target
        # 2 �жϴ����Ƿ����
        if self.exist_disk(disk_name):
             raise CustomException("Error: disk name is exist!")
             return
        
        # 3 ��ѯ��ǰ����������õ�δʹ�õĴ������̷�
        disk_target = target
#        disks = self.info_disks(vm_name)
#        targets = []
#        for disk in disks:
#            targets.append(disk['disk_target'])
#        
#        for i in range(98,123):
#            i =  "vd"+ chr(i)
#            if i not in targets:
#                disk_target = i
#                break
        
        # 4 ����lvm����
        self.storageManage.create_lvm(lvm_name=disk_name,lvm_size=disk_size)
        disk_file = self.storageManage.get_lvm_path(disk_name)
        
        
        # 5 ��ʽ��ϵͳ��ʽ
        self.disk_mkfs(vm_name,disk_file)
        
        
        # 6 Ӳ�̹���
        self.vm_tools.attach_disk(vm_name,disk_target,disk_file)
        
        
        # 7 �������ݿ�
        # �������ͣ�ntfs or ext4
        disk_type =  self.get_os_type(vm_name)
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        save_sql = '''INSERT INTO %s values (?, ?, ?, ?, ?, ?, ?, ?)'''%DISKTABLE
        data = [(vm_name, disk_size,disk_name,disk_target,disk_file,disk_type,time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)

    
    # ɾ������
    def detach_disk(self,vm_name,disk_name):
        ""

        # 1 ���
        self.check(vm_name)
        
        
        # 2 ��ѯ
        disks = self.info_disks(vm_name)
        disk_target = None
        for disk in disks:
            if disk_name == disk['disk_name']:
                disk_target = disk['disk_target']
                break
        
        if disk_target is None:
            raise CustomException("Error: disk name is not exist!")
            return
        
        # 3 ж�ش���
        self.vm_tools.detach_disk(vm_name,disk_target)
        
        # 4 ɾ��lvm
        try:
            self.storageManage.remove_lvm(disk_name)
        except Exception , e:
            raise CustomException("Error: remove lvm failed!")
        
        # 5 ɾ�����ݿ�
        delete_sql = 'DELETE FROM %s WHERE vmName = ? and diskName = ? '%DISKTABLE
        data = [(vm_name,disk_name)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
        
    
    # ��չ����
    def extend_disk(self,vm_name,target,total_size):
        ""
        
        # 1 ���
        self.check(vm_name)
        
        disk_name = vm_name+"_"+target
        # 2 �ж��Ƿ�����
        state = self.vm_tools.vm_states(vm_name)
        if state[vm_name] == "running" :
            raise CustomException("vm name is running.")
        
        
        # 3 �жϴ����Ƿ����
        disks = self.info_disks(vm_name)
        disk_size = None
        for disk in disks:
            if disk_name == disk['disk_name']:
                disk_size = disk['disk_size']
                break
        if disk_size is None:
            raise CustomException("Error: disk name is not exist!")
            return
        
        extend_size = int(total_size) - int(disk_size)
        # 4 ��չ����
        try:
            self.storageManage.extend_lvm(disk_name,extend_size)
        except Exception , e:
            raise CustomException("Error: extend lvm failed!")
        
        
        # 5 �޸����ݿ�
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET diskSize = ? WHERE vmName = ? and diskName = ?'%DISKTABLE
        data = [(total_size, vm_name,disk_name)]
        sql_tools.update(update_sql,data)
    
    
    # �õ�vnc�˿�
    def get_vnc_port(self):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        vnc_port_range = virtual_conf['vnc_port_range']
        min_port,max_port = vnc_port_range.split('-')
        
        #��ѯ��ǰvnc�˿�
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        fetchall_sql = '''SELECT vncPort FROM %s order by vncPort'''%VMTABLE
        ports =  sql_tools.fetchall(fetchall_sql)
        
        treated_ports = []
        for port in ports:
            treated_ports.append(port[0])

        for i in range(int(min_port),int(max_port)+1):
            if i  not in treated_ports:
                vnc_port = i
                break
        
        if vnc_port is not None: 
            return vnc_port
        else:
            return None
    
    
    #�ж���Դ
    def vm_resource(self,vcpus=0,memary=0,disk=0):
        ""
        
        # 1 ��ѯ�ܵ���Դ
        virtual_conf = self.conf.get_virtual_conf()
        max_vcpus = virtual_conf['maxVcpus']
        max_memary = virtual_conf['maxMemary']
        max_disk = virtual_conf['maxDisk']
        
        # 2 ��ѯ��ǰʹ�õ���Դ����
        use_vcpus = 0
        use_memary = 0
        use_disk = 0
        infos = self.info_vms() 
        for info in infos:
            use_vcpus += info["vcpus"]
            use_memary += info["mem_size"]
            use_disk += info["vm_size"]
            #��ѯӲ��
            disks = self.info_disks(info["vm_name"])
            for d in disks:
                use_disk += int(d['disk_size'])
        
        # 3 �Ƚ�
        if (int(vcpus) < int(max_vcpus) - int(use_vcpus)) and (int(memary) < int(max_memary) - int(use_memary)) and  (int(disk) < int(max_disk) - int(use_disk)):
            return True
        else:
            return False

    # ����˿����
    def proxy_add(self,**kwargs):
        ""
        
        # ��ѡ
        vm_name = kwargs.pop('vm_name', None)
        port    = kwargs.pop('port', None)
        # ��ѡ
        ip = kwargs.pop('ip', None)
        proxy_ip    = kwargs.pop('proxy_ip', None)
        proxy_port    = kwargs.pop('proxy_port', None)
        
        proxy_type = kwargs.pop('proxy_type', None)
        
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ��ѯip
        if ip == None:
            info = self.info_vm(vm_name)
            ip = info['ip']
        
        # 3 ��Ӵ���
        if proxy_ip == None and proxy_port == None:
            proxy_info = self.net.portProxyRegister(ip,port,proxyType=proxy_type)
            proxy_ip = proxy_info['proxyIp']
            proxy_port = proxy_info['proxyPort'] 
        
        # 4 ������ݿ�
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        save_sql = '''INSERT INTO %s values (?, ?, ?, ?, ?, ?, ?)'''%VMPROXY
        data = [(vm_name,ip,port,proxy_ip,proxy_port, time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)
        
        return proxy_ip,proxy_port
    # ����˿�ɾ��
    def proxy_del(self,**kwargs):
        ""
        
        # ��ѡ
        vm_name = kwargs.pop('vm_name', None)
        port    = kwargs.pop('port', None)
        # ��ѡ
        ip = kwargs.pop('ip', None)
        proxy_ip    = kwargs.pop('proxy_ip', None)
        proxy_port    = kwargs.pop('proxy_port', None)
        
        proxy_type = kwargs.pop('proxy_type', None)
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ��ѯip
        if ip == None:
            info = self.info_vm(vm_name)
            ip = info['ip']
        
        # 3 ɾ������
        self.net.portProxyRemove(ip,port,proxyType=proxy_type)
        
        # 4 ɾ�����ݿ�
        delete_sql = 'DELETE FROM %s WHERE ip = ? and port = ? '%VMPROXY
        data = [(ip,port)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
    
    # ����˿ڲ�ѯ
    def proxy_list(self,**kwargs):
        ""
        
        vm_name = kwargs.pop('vm_name', None)
        port    = kwargs.pop('port', None)
        ip = kwargs.pop('ip', None)
        
        
        sql = "select * from %s where 1=1" % VMPROXY
        
        data = ()
        cond_conf = ''
        
        if vm_name is not None :
            cond_conf += ' and vmName=?'
            data += (vm_name,)
            
        if ip is not None :
            cond_conf += ' and ip=?'
            data += (ip,)
            
        if port is not None :
            cond_conf += ' and port=?'
            data += (port,)
            
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        if len(data) > 0 :
            sql += cond_conf
            infos = sql_tools.fetchall(sql,data)
        else :
            infos = sql_tools.fetchall(sql)
        
        proxys = []
        for item in infos:
            proxy = {}
            if item is not None:
                proxy['vmName']   = item[0]
                proxy['ip']        = item[1]
                proxy['port']      = item[2]
                proxy['proxyIp']   = item[3]
                proxy['proxyPort'] = item[4]
            proxys.append(proxy)
        
        return proxys
    
    
    # windowsע����޸�
    def win_reg_set(self,vm_name,reg_path,reg_key,reg_new_value):
        
        # 1 ���
        self.check(vm_name)
        
        # 2 ����Ƿ�ر�
        
        try:
            # 3 ��ʼ������
            regedit = WinRegedit(vm_name)
            # 4 �޸�
            regedit.reg_modify(reg_path,reg_key,reg_new_value)
            # 5 �ر�
            regedit.reg_close()
        except Exception , e:
            raise CustomException("Error: modify windows regedit failed!")
    
    # �õ�����ϵͳ����
    def get_os_type(self,vm_name):
        ""
        
        # 1 ���
        self.check(vm_name)
        # 2 vm��Ϣ
        vm_info = self.info_vm(vm_name)
        image_name = vm_info['image_name']
        # 3 image��Ϣ
        image_info = self.image.info_image(image_name)
        
        return image_info['system']
    
    #�������������ϵͳ������
    def set_os_hostname(self, vm_name, hostname):
        os_type = self.get_os_type(vm_name)
        if os_type == 'window' or os_type == 'window7' or os_type == 'window2000' or os_type == 'window2008' or os_type == 'windows':
            vgfs = VirtGuestfs(vm_name, None)
            vgfs.launch()
            vgfs.mount_os()
            vgfs.reg_open()
            vgfs.reg_modify('ControlSet001/services/Tcpip/Parameters',"NV Hostname", 1L, hostname)
            vgfs.reg_modify('ControlSet002/services/Tcpip/Parameters',"NV Hostname", 1L, hostname)
            vgfs.reg_commit()
            vgfs.close()
        else :
            pass
    
    #����������Ļ�������
    def set_os_env_var(self, vm_name, dict_envs) :
        os_type = self.get_os_type(vm_name)
        if os_type == 'window' or os_type == 'window7' or os_type == 'window2000' or os_type == 'window2008' or os_type == 'windows':
            vgfs = VirtGuestfs(vm_name, None)
            vgfs.launch()
            vgfs.mount_os()
            vgfs.reg_open()
            for key in dict_envs :                
                vgfs.reg_modify('ControlSet001/Control/Session Manager/Environment',key, 1L, dict_envs[key])
                vgfs.reg_modify('ControlSet002/Control/Session Manager/Environment',key, 1L, dict_envs[key])
            vgfs.reg_commit()
            vgfs.close()
        elif os_type == 'linux' or os_type.find('centos') != -1 or os_type.find('redhat') or os_type.find('fedora'):
            lines = ''
            for key in dict_envs :
                if dict_envs[key] :
                    val = dict_envs[key].replace('\"',"\\\"")
                    val = "\""+val+"\""
                    lines += '\nexport %s=%s'%(key, val)
                    lines += "\n"
            print lines
            if len(lines)>0 :
                vgfs = VirtGuestfs(vm_name, None)
                vgfs.launch()
                vgfs.mount_os()
                vgfs.append_file('/etc/profile', lines)
                vgfs.close()
        else:
            raise Exception('vm_name=%s, os_type=%s, set evn var can not support'%(vm_name, os_type))
    
    #��ʽ������
    def disk_mkfs(self, vm_name, imgfile, fs_type=None, label=None):
        os_type = self.get_os_type(vm_name)
        if fs_type is None:
            if os_type == 'window' or os_type == 'window7' or os_type == 'window2000' or os_type == 'window2008' or os_type == 'windows':
                fs_type = 'ntfs'
            elif os_type == 'linux' or os_type.find('centos') != -1 or os_type.find('redhat') or os_type.find('fedora'):
                fs_type = 'ext4'
            else:
                raise Exception('vm_name=%s, os_type=%s, mkfs can not support'%(vm_name, os_type))
        
        vgfs = VirtGuestfs(None, imgfile)
        flag = vgfs.disk_mkfs(fs_type,label=label)
        vgfs.close()
        return flag
    
    def _getDiskFile(self, vm_name, target):
        disks = self.info_disks(vm_name)
        #disk_target = None
        imgfile = None
        for disk in disks:
            if target == disk['disk_target']:
                imgfile =  disk['disk_file']
        return imgfile
    
    #�ϴ��ļ�    
    def upload(self, vm_name, target, filename, remotefilename):
        imgfile = self._getDiskFile(vm_name, target)
        
        if imgfile:
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.upload(filename, remotefilename)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
    
    #����Ŀ¼
    def mkdir(self, vm_name, target, path):
        imgfile = self._getDiskFile(vm_name, target)
        if imgfile :
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.make_path(path)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
    
    #ѹ������ѹ����
    def tgzin(self, vm_name, target, tarball, directory):        
        imgfile = self._getDiskFile(vm_name, target)
        
        if imgfile:
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.tgz_in(tarball, directory)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
            
    #���������ϵͳ�˺ŵ�����
    def set_os_user_passwd(self, vm_name, user, passwd):
        pass
    
    #����������
#    def add_os_mount(self, vm_name, dict_part):
#        '/dev/hda1              /data          auto      defaults                0      0'
#        os_type = self.get_os_type(vm_name)
#        if os_type == 'window' or os_type == 'window7' or os_type == 'window2000' or os_type == 'window2008' or os_type == 'window':
#            return
#        elif os_type == 'linux' or os_type.find('centos') != -1 or os_type.find('redhat') or os_type.find('fedora'):
#            vgfs = VirtGuestfs(vm_name, None)
#            vgfs.launch()
#            vgfs.mount_os()
#            filesystems = vgfs.list_filesystems()
#            keys = filesystems.keys()
#            keys.sort()
#            for key in dict_part : 
#                dev = keys[key]
#                dev_type = filesystems[dev]
#                path = dict_part[key]
#                mount = {"dev":dev,"dir":path,"type":dev_type,'options':'defaults','dump':0,'pass':0}
#                mount_str = '%(dev)s              %(dir)s          %(type)s      %(options)s      %(dump)d      %(pass)d\n'%mount
#                mount_file = '/etc/fstab'
#                vgfs.append_file(mount_file, mount_str)
#            vgfs.close()
#        else:
#            raise Exception('vm_name=%s, os_type=%s, mount can not support'%(vm_name, os_type))
    
    #����������
    def add_os_mount(self, vm_name, dict_part):
        '/dev/hda1              /data          auto      defaults                0      0'
        os_type = self.get_os_type(vm_name)
        if os_type == 'window' or os_type == 'window7' or os_type == 'window2000' or os_type == 'window2008' or os_type == 'windows':
            return
        elif os_type == 'linux' or os_type.find('centos') != -1 or os_type.find('redhat') or os_type.find('fedora'):
            vgfs = VirtGuestfs(vm_name, None)
            vgfs.launch()
            vgfs.mount_os()
            for key in dict_part : 
                dev = key
                dev_type = 'auto'
                path = dict_part[key]
                mount = {"dev":"/dev/%s"%dev,"dir":path,"type":dev_type,'options':'defaults','dump':0,'pass':0}
                mount_str = '%(dev)s              %(dir)s          %(type)s      %(options)s      %(dump)d      %(pass)d\n'%mount
                mount_file = '/etc/fstab'
                vgfs.append_file(mount_file, mount_str)
            vgfs.close()
        else:
            raise Exception('vm_name=%s, os_type=%s, mount can not support'%(vm_name, os_type))
    
    # �������
    def create_vm_table(self):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        # 1 �������
        create_vm_table_sql = '''CREATE TABLE `%s` (
                            `vmName`     varchar(128) NOT NULL,
                            `vmFile`     varchar(128) NOT NULL,
                            
                            `imageName`  varchar(128) NOT NULL,
                            `imageFile`  varchar(128) NOT NULL,
                            
                            `vmSize`     double(24)  NOT NULL,
                            `memSize`    int(10)  NOT NULL,
                            `vcpus`      int(2)  NOT NULL,

                            `vncPort`    int(4) NOT NULL,
                            `vncPasswd`  int(4) NOT NULL,
                            
                            `interfaces` varchar(256) NOT NULL,
                            `ip`         varchar(128) NOT NULL,
                            
                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark`     varchar(1024) DEFAULT NULL,
                             PRIMARY KEY (`vmName`)
                        )'''%VMTABLE
                        
        sql_tools.create_table(create_vm_table_sql)
        
        # 2 �����Ӳ�̱�
        create_vmdisk_table_sql = '''CREATE TABLE `%s` (
                            `vmName`     varchar(128) NOT NULL,
                            
                            `diskSize`   int(10)  NOT NULL,
                            `diskName`   varchar(128) NOT NULL,
                            `diskTarget` varchar(128) NOT NULL,
                            `diskFile`   varchar(128) NOT NULL,
                            `diskType`   varchar(128) NOT NULL,

                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark`     varchar(1024) DEFAULT NULL
                        )'''%DISKTABLE
        
        sql_tools.create_table(create_vmdisk_table_sql)

        # 3 ������˿ڱ�
        create_vmproxy_table_sql = '''CREATE TABLE `%s` (
                            `vmName`     varchar(128) NOT NULL,
                            
                            `ip`   varchar(128)  NOT NULL,
                            `port`   int(10) NOT NULL,
                            `proxyIp` varchar(128) NOT NULL,
                            `proxyPort`   int(10) NOT NULL,
                            
                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark`     varchar(1024) DEFAULT NULL
                        )'''%VMPROXY
        
        sql_tools.create_table(create_vmproxy_table_sql)

if __name__ == "__main__":
    aa = VmManage()
    print "start"
    #aa.create_vm(image_name="0F7620DDF32543A097372F11C5B8877F",vm_name="test_0001",mem_size=1024,vcpus=1,vm_size=5000)
    #print aa.info_vm('kvmtest_01')
    #print aa.state_vm('kvmtest_01')
    #print aa.start_vm('kvmtest_01')
    #print aa.pause_vm('kvmtest_01')
    #aa.resume_vm('kvmtest_01')
    #aa.destroy_vm('cattle_t3')
    #aa.delete_vm('test_kvm_002')
    #aa.create_vm_table()
    #aa.reboot_vm('testkvm1')
    #aa.create_vm_table()
    #print aa.exist_disk('disk01')
    
    #aa.attach_disk('de9252f47acd11e4b907fe5400e41488',"vdb",500)
    
    
    #aa.detach_disk('testkvm1',"disk10")
    #aa.extend_disk('kvmtest_01',"disk3","100")
    #aa.pause_vm("testkvm1")
    #aa.start_vm("kvmtest_01")
    #print aa.shutdown_vm('kvmtest_01')
    
    #aa.delete_vm("kvmtest_01")
    
    #print aa.vm_resource(vcpus='3',memary=1024,disk=10240)
    print aa.proxy_add(vm_name ="test_0003",ip='192.168.2.1',port=6900,proxy_type='tcp')
    #print aa.proxy_del(vm_name ="test_0003",ip='192.168.2.1',port=900,proxy_type=None)
    #print aa.proxy_list(vm_name = None,port=None,ip=None)
    #print aa.find_vm('kvmtest_001')
    #print aa.get_os_type('kvmtest_001')
#    tmp={}
#    tmp['IPAAS_ENV']= "[{'host':'aaa','ip':'2.2.3.3'}]"
#    aa.set_os_env_var('eca38e5479f011e48b22fe5400e41487',tmp)
    print "end"
    
