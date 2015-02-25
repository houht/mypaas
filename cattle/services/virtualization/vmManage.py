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
    
    
    # 查询数据库单个vm信息
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
    
    # 查询数据库所有vm信息
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
        
        
        
        
    
    # 查询vm的所有磁盘
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
        
    
    
    # 判断磁盘是否存在
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
        
    # vm检查是否存在
    def check(self,vm_name):
        ""
        
        if vm_name is None:
            raise CustomException("vm name is None.")
            return
        
        if self.info_vm(vm_name) is None:
            raise CustomException("vm is not exists.")
            return
    
    # 创建VM
    def create_vm(self,**kwargs):
        ""
        
        image_name = kwargs.pop('image_name', None)
        vm_name    = kwargs.pop('vm_name', None)
        # VM大小，单位M
        vm_size    = kwargs.pop('vm_size', None)
        # 内存大小，单位M
        mem_size   = kwargs.pop('mem_size', None)
        # cpu大小，单位核数
        vcpus      = kwargs.pop('vcpus', None)
        host_name  = kwargs.pop('host_name', "")
        
        
        infos = {}
        
        
        # 判断
        if vm_name is None:
            raise CustomException("vm name is None.")
            return
        
        if self.info_vm(vm_name) is not None:
            raise CustomException("vm is exists.")
            return
        
        # 1 判断镜像文件是否存在，判断是否下载
        try:
            image_file = self.image.download_image(image_name)
        except Exception , e:
            raise CustomException("Error: %s" % str(e) )
        img_infos = self.image.info_image(image_name)
        
        arch = img_infos['arch']
        machine = img_infos['machine']
        
        # 2 创建lvm
        lvm_mount_dir = self.storageManage.create_lvm(lvm_name=vm_name,lvm_size=vm_size,mount=True)
        
        # 3 基于父创建img
        vm_file = os.path.join(lvm_mount_dir,vm_name+'.img') 
        self.qemu.create_img(basefile=image_file,filename=vm_file)
       
        # 4 查询网络信息
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
        
        # 5 得到vnc port
        vnc_port = self.get_vnc_port()
        if vnc_port is None:
            raise CustomException("Error: vnc port is none.")
        
        # 6 创建vm
        
        # vnc密码，随机生成 
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
        
        
        # 7 保存数据库
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
    
    # 硬关机
    def destroy_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.destroy_vm(vm_name)
    
    # 软关机 
    def shutdown_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.stop_vm(vm_name)
    
    # virsh list --all
    def list_vm(self):
        ""
        
        return self.vm_tools.list_vm()
    
    
    # 启动虚拟机
    def start_vm(self,vm_name):
        ""
        
        self.check(vm_name)
        self.vm_tools.start_vm(vm_name)
    
    
    # 运行状态
    def state_vm(self,vm_name=None):
        ""
        
        self.check(vm_name)
        return self.vm_tools.vm_states(vm_name)
    
    
    #修改内存，单位M，关机修改(先设置最大内存？)
    def set_vm_mem(self,vm_name,size):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        # 2 设置内存
        self.vm_tools.set_mem(vm_name=vm_name,memory=size)
        
        # 3 修改数据库
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET memSize = ? WHERE vmName = ? '%VMTABLE
        data = [(size, vm_name)]
        sql_tools.update(update_sql,data)


    
    #修改cpu，单位核数，关机修改
    def set_vm_cpu(self,vm_name,vcpus):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        # 2 设置cpu
        self.vm_tools.set_vcpus(vm_name=vm_name,vcpus=vcpus)
        
        # 3 修改数据库
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET vcpus = ? WHERE vmName = ? '%VMTABLE
        data = [(vcpus, vm_name)]
        sql_tools.update(update_sql,data)

    
    # 暂停
    def pause_vm(self,vm_name):
        ""
        
        # 1 检测
        self.check(vm_name)

        # 2 暂停
        self.vm_tools.pause_vm(vm_name)
    
    # 暂停恢复
    def resume_vm(self,vm_name):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        # 2 反暂停
        self.vm_tools.resume_vm(vm_name)
    
    
    # 重启
    def reboot_vm(self,vm_name):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        # 2 重启
        self.vm_tools.reboot_vm(vm_name)
        

    # 删除虚拟机
    def delete_vm(self,vm_name=None):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        # 2 删除vm和取消定义
        self.vm_tools.vm_delete(vm_name)
        
        # 3 删除lvm
        try:
            self.storageManage.remove_lvm(vm_name,True)
        except Exception , e:
            raise CustomException("Error: remove lvm failed!")
        
        # 4 删除网络
        vm_info = self.info_vm(vm_name)
        js = JsonParser()
        if vm_info is not None:
            tmps = js.decode(vm_info['interfaces'].replace('\'','\"'))
            for tmp in tmps:
                ip = tmp['ip']
                br = tmp['br']
                self.net.fixedIpRemove(br, ip)
        
        # 5 删除代理端口
        proxy_infos = self.proxy_list(vm_name = vm_name)
        for proxy_info in proxy_infos:
            self.proxy_del(vm_name = proxy_info["vmName"],ip = proxy_info["ip"],port = proxy_info["port"])
        
        
        # 6 判断是否有外加的磁盘，删除
        disks = self.info_disks(vm_name)
        for disk in disks:
            self.detach_disk(vm_name,disk['disk_name'])
            
        
        # 7 删除数据库
        delete_sql = 'DELETE FROM %s WHERE vmName = ? '%VMTABLE
        data = [(vm_name,)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
        
    def control_vm(self):
        ""
        
        pass

    # 添加磁盘，disk_size 磁盘大小，单位M
    def attach_disk(self,vm_name,target,disk_size):
        ""

        # 1 检测
        self.check(vm_name)

        disk_name = vm_name+"_"+target
        # 2 判断磁盘是否存在
        if self.exist_disk(disk_name):
             raise CustomException("Error: disk name is exist!")
             return
        
        # 3 查询当前磁盘情况，得到未使用的磁盘那盘符
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
        
        # 4 创建lvm磁盘
        self.storageManage.create_lvm(lvm_name=disk_name,lvm_size=disk_size)
        disk_file = self.storageManage.get_lvm_path(disk_name)
        
        
        # 5 格式化系统格式
        self.disk_mkfs(vm_name,disk_file)
        
        
        # 6 硬盘挂载
        self.vm_tools.attach_disk(vm_name,disk_target,disk_file)
        
        
        # 7 保存数据库
        # 磁盘类型，ntfs or ext4
        disk_type =  self.get_os_type(vm_name)
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        save_sql = '''INSERT INTO %s values (?, ?, ?, ?, ?, ?, ?, ?)'''%DISKTABLE
        data = [(vm_name, disk_size,disk_name,disk_target,disk_file,disk_type,time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)

    
    # 删除磁盘
    def detach_disk(self,vm_name,disk_name):
        ""

        # 1 检测
        self.check(vm_name)
        
        
        # 2 查询
        disks = self.info_disks(vm_name)
        disk_target = None
        for disk in disks:
            if disk_name == disk['disk_name']:
                disk_target = disk['disk_target']
                break
        
        if disk_target is None:
            raise CustomException("Error: disk name is not exist!")
            return
        
        # 3 卸载磁盘
        self.vm_tools.detach_disk(vm_name,disk_target)
        
        # 4 删除lvm
        try:
            self.storageManage.remove_lvm(disk_name)
        except Exception , e:
            raise CustomException("Error: remove lvm failed!")
        
        # 5 删除数据库
        delete_sql = 'DELETE FROM %s WHERE vmName = ? and diskName = ? '%DISKTABLE
        data = [(vm_name,disk_name)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
        
    
    # 扩展磁盘
    def extend_disk(self,vm_name,target,total_size):
        ""
        
        # 1 检测
        self.check(vm_name)
        
        disk_name = vm_name+"_"+target
        # 2 判断是否运行
        state = self.vm_tools.vm_states(vm_name)
        if state[vm_name] == "running" :
            raise CustomException("vm name is running.")
        
        
        # 3 判断磁盘是否存在
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
        # 4 扩展磁盘
        try:
            self.storageManage.extend_lvm(disk_name,extend_size)
        except Exception , e:
            raise CustomException("Error: extend lvm failed!")
        
        
        # 5 修改数据库
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db) 
        update_sql = 'UPDATE %s SET diskSize = ? WHERE vmName = ? and diskName = ?'%DISKTABLE
        data = [(total_size, vm_name,disk_name)]
        sql_tools.update(update_sql,data)
    
    
    # 得到vnc端口
    def get_vnc_port(self):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        vnc_port_range = virtual_conf['vnc_port_range']
        min_port,max_port = vnc_port_range.split('-')
        
        #查询当前vnc端口
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
    
    
    #判断资源
    def vm_resource(self,vcpus=0,memary=0,disk=0):
        ""
        
        # 1 查询总的资源
        virtual_conf = self.conf.get_virtual_conf()
        max_vcpus = virtual_conf['maxVcpus']
        max_memary = virtual_conf['maxMemary']
        max_disk = virtual_conf['maxDisk']
        
        # 2 查询当前使用的资源总数
        use_vcpus = 0
        use_memary = 0
        use_disk = 0
        infos = self.info_vms() 
        for info in infos:
            use_vcpus += info["vcpus"]
            use_memary += info["mem_size"]
            use_disk += info["vm_size"]
            #查询硬盘
            disks = self.info_disks(info["vm_name"])
            for d in disks:
                use_disk += int(d['disk_size'])
        
        # 3 比较
        if (int(vcpus) < int(max_vcpus) - int(use_vcpus)) and (int(memary) < int(max_memary) - int(use_memary)) and  (int(disk) < int(max_disk) - int(use_disk)):
            return True
        else:
            return False

    # 代理端口添加
    def proxy_add(self,**kwargs):
        ""
        
        # 必选
        vm_name = kwargs.pop('vm_name', None)
        port    = kwargs.pop('port', None)
        # 可选
        ip = kwargs.pop('ip', None)
        proxy_ip    = kwargs.pop('proxy_ip', None)
        proxy_port    = kwargs.pop('proxy_port', None)
        
        proxy_type = kwargs.pop('proxy_type', None)
        
        
        # 1 检测
        self.check(vm_name)
        
        # 2 查询ip
        if ip == None:
            info = self.info_vm(vm_name)
            ip = info['ip']
        
        # 3 添加代理
        if proxy_ip == None and proxy_port == None:
            proxy_info = self.net.portProxyRegister(ip,port,proxyType=proxy_type)
            proxy_ip = proxy_info['proxyIp']
            proxy_port = proxy_info['proxyPort'] 
        
        # 4 添加数据库
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        save_sql = '''INSERT INTO %s values (?, ?, ?, ?, ?, ?, ?)'''%VMPROXY
        data = [(vm_name,ip,port,proxy_ip,proxy_port, time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)
        
        return proxy_ip,proxy_port
    # 代理端口删除
    def proxy_del(self,**kwargs):
        ""
        
        # 必选
        vm_name = kwargs.pop('vm_name', None)
        port    = kwargs.pop('port', None)
        # 可选
        ip = kwargs.pop('ip', None)
        proxy_ip    = kwargs.pop('proxy_ip', None)
        proxy_port    = kwargs.pop('proxy_port', None)
        
        proxy_type = kwargs.pop('proxy_type', None)
        
        # 1 检测
        self.check(vm_name)
        
        # 2 查询ip
        if ip == None:
            info = self.info_vm(vm_name)
            ip = info['ip']
        
        # 3 删除代理
        self.net.portProxyRemove(ip,port,proxyType=proxy_type)
        
        # 4 删除数据库
        delete_sql = 'DELETE FROM %s WHERE ip = ? and port = ? '%VMPROXY
        data = [(ip,port)]
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        sql_tools.delete(delete_sql,data)
        
    
    # 代理端口查询
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
    
    
    # windows注册表修改
    def win_reg_set(self,vm_name,reg_path,reg_key,reg_new_value):
        
        # 1 检测
        self.check(vm_name)
        
        # 2 检测是否关闭
        
        try:
            # 3 初始化对象
            regedit = WinRegedit(vm_name)
            # 4 修改
            regedit.reg_modify(reg_path,reg_key,reg_new_value)
            # 5 关闭
            regedit.reg_close()
        except Exception , e:
            raise CustomException("Error: modify windows regedit failed!")
    
    # 得到操作系统类型
    def get_os_type(self,vm_name):
        ""
        
        # 1 检测
        self.check(vm_name)
        # 2 vm信息
        vm_info = self.info_vm(vm_name)
        image_name = vm_info['image_name']
        # 3 image信息
        image_info = self.image.info_image(image_name)
        
        return image_info['system']
    
    #设置虚拟机操作系统主机名
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
    
    #设置虚拟机的环境变量
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
    
    #格式化磁盘
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
    
    #上传文件    
    def upload(self, vm_name, target, filename, remotefilename):
        imgfile = self._getDiskFile(vm_name, target)
        
        if imgfile:
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.upload(filename, remotefilename)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
    
    #创建目录
    def mkdir(self, vm_name, target, path):
        imgfile = self._getDiskFile(vm_name, target)
        if imgfile :
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.make_path(path)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
    
    #压缩包解压拷贝
    def tgzin(self, vm_name, target, tarball, directory):        
        imgfile = self._getDiskFile(vm_name, target)
        
        if imgfile:
            vgfs = VirtGuestfs(None, imgfile)
            vgfs.launch()
            vgfs.mount_static()
            vgfs.tgz_in(tarball, directory)
        else :
            raise Exception('The disk does not exist, vm_name=%s,target=%s'%(vm_name, target))
            
    #设置虚拟机系统账号的密码
    def set_os_user_passwd(self, vm_name, user, passwd):
        pass
    
    #挂载数据盘
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
    
    #挂载数据盘
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
    
    # 虚拟机表
    def create_vm_table(self):
        ""
        
        virtual_conf = self.conf.get_virtual_conf()
        virtual_db = virtual_conf['db_path']
        sql_tools = SqliteTools(virtual_db)
        
        # 1 虚拟机表
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
        
        # 2 虚拟机硬盘表
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

        # 3 虚拟机端口表
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
    
