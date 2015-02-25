#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import time
import os
import sys
import fcntl 
import re

from cattle.utils import LvmDriver
from cattle.utils import Command
from cattle.utils import SqliteTools
from cattle.utils import CustomException


from cattle.services import ConfigManage

class StorageManage:
    "storage management"
    
    
    def __init__(self):
        ""
        
        self.conf = ConfigManage()
        
    
    def info_lvm(self,lvm_name):
        ""
        
        storage_conf = self.conf.get_storage_conf()
        storage_db = storage_conf['db_path']
        sql_tools = SqliteTools(storage_db)

        fetchone_sql = 'SELECT * FROM lvm WHERE lvmName = ? '
        data = lvm_name
        item = sql_tools.fetchone(fetchone_sql,data)
        infos = {}
        if item is not None:
            infos['lvm_name']     = item[0]
            infos['vg_name']      = item[1]
            infos['lvm_size']     = item[2]
            infos['lvm_dir']      = item[3]
            infos['mount_dir']    = item[4]
            infos['lvm_mkfs']     = item[5]
            infos['lvm_type']     = item[6]
            infos['createtime']   = item[7]
            infos['remark']       = item[8]
        else:
            return None
        
        return infos
    
    
    def get_lvm_path(self,lvm_name,vg_name=None):
        ""
        
        
        if vg_name is None:
            storage_conf = self.conf.get_storage_conf()
            vg_name = storage_conf['vg_name']
        
        
        lvm = LvmDriver(vg_name)
        
        return lvm.get_lvm_path(lvm_name)
        
        
    
    def create_lvm(self,**kwargs):
        ""
        
        lvm_name   = kwargs.pop('lvm_name', None)
        lvm_size   = kwargs.pop('lvm_size', None)
        vg_name    = kwargs.pop('vg_name', None)
        mount      = kwargs.pop('mount', False)
        # 1 判断vg name
        storage_conf = self.conf.get_storage_conf()
        if vg_name is None:
            vg_name = storage_conf['vg_name']
        
        # 2 创建lvm
        lvm = LvmDriver(vg_name)
        lvm.create_volume(lvm_name,str(lvm_size) + "M")
        
        
        # 3 格式化
        lvm_dir  = self.get_lvm_path(lvm_name,vg_name)
        self.format_dir(lvm_dir)
        lvm_mkfs = storage_conf['cmd_format']
        
        mount_dir= ""
        lvm_type = "disk"
        
        # 4 判断是否挂载
        if mount:
            lvm_type = "image"
            # 2 挂载
            mount_dir = os.path.join(storage_conf['path'],lvm_name)
            self.mount_dir(lvm_dir,mount_dir)
        
        # 5 保存数据库
        save_sql = '''INSERT INTO lvm values (?, ?, ?,?,?,?,?,?,?)'''
        data = [(lvm_name, vg_name, lvm_size,lvm_dir,mount_dir, lvm_mkfs,lvm_type,time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        storage_db = storage_conf['db_path']
        sql_tools = SqliteTools(storage_db)
        sql_tools.save(save_sql,data)
  
        return mount_dir
  
    
    def mount_dir(self,lvm_dir,mount_dir):
        ""
        
        storage_conf = self.conf.get_storage_conf()
        mount = storage_conf['cmd_mount']
        
        cmd = Command()
        if not os.path.exists(mount_dir):
            cmd.execute("mkdir -p %s"%mount_dir)
        
        mount_cmd = "%s %s %s"%(mount,lvm_dir,mount_dir)
        cmd.execute(mount_cmd)
    
        # 添加开机挂载
        self.set_sysinit("add",mount_cmd)
    
    
    def umount_dir(self,lvm_name):
        ""
        
        # 1 查询
        infos = self.info_lvm(lvm_name)
        lvm_dir = infos['lvm_dir']
        mount_dir = infos['mount_dir']
        
        storage_conf = self.conf.get_storage_conf()
        umount = storage_conf['cmd_umount']
        mount = storage_conf['cmd_mount']
        
        # 2 卸载
        cmd = Command()
        cmd.execute("fuser","-k",mount_dir)
        cmd.execute("%s %s"%(umount,mount_dir))
        
        # 3 删除目录
        cmd.execute("rm -rf %s"%mount_dir)
        
        
        # 4 删除开机挂载
        mount_cmd = "%s %s %s"%(mount,lvm_dir,mount_dir)
        self.set_sysinit("del",mount_cmd)
        
        
    def format_dir(self,lvm_dir):
        ""
        
        storage_conf = self.conf.get_storage_conf()
        cmd_format = storage_conf['cmd_format']

        cmd = Command()
        cmd.execute("%s %s"%(cmd_format,lvm_dir))
    
    
    def extend_lvm(self,lvm_name,extend_size):
        ""
        
        # 1 查询
        infos = self.info_lvm(lvm_name)
        if infos is None:
            raise CustomException("lvm is not exist.")
            
        vg_name = infos['vg_name']
        lvm_size = infos['lvm_size']
        
        # 2 扩展lvm
        lvm = LvmDriver(vg_name)
        lvm.extend_volume(lvm_name,"+" + str(lvm_size) + "M")
        
        cmd = Command()
        lvm_path = self.get_lvm_path(lvm_name,vg_name)

        # 3 扫描
        cmd.execute("e2fsck -f -y %s"%lvm_path)

        # 4 重置
        cmd.execute("resize2fs %s"%lvm_path)

        lvm_new_size = int(infos['lvm_size']) + int(extend_size)
        # 5 更新数据库
        update_sql = 'UPDATE lvm SET lvmSize = ? WHERE lvmName = ? '
        data = [(lvm_new_size, lvm_name)]
        
        storage_conf = self.conf.get_storage_conf()
        storage_db = storage_conf['db_path']
        sql_tools = SqliteTools(storage_db)
        sql_tools.update(update_sql,data)
        
        
    
    def remove_lvm(self,lvm_name,mount=False):
        ""
        
        # 1 查询信息
        infos = self.info_lvm(lvm_name)
        if infos is None:
            raise CustomException("lvm  is not exist.")
        
        vg_name = infos['vg_name']
        lvm_dir = infos['lvm_dir']
        mount_dir = infos['mount_dir']

        # 2 卸载挂载
        if mount:
            self.umount_dir(lvm_name)
        
        # 3 删除lvm
        lvm = LvmDriver(vg_name)
        lvm.remove_volume(lvm_dir)
        
        
        # 4 删除数据库
        delete_sql = 'DELETE FROM lvm WHERE lvmName = ? '
        data = [(lvm_name,)]
        storage_conf = self.conf.get_storage_conf()
        storage_db = storage_conf['db_path']
        sql_tools = SqliteTools(storage_db)
        sql_tools.delete(delete_sql,data)
        
    
    def set_sysinit(self ,op, cmd):
        ""
        
        sysinit_file = '/etc/rc.local'
        
        if op == 'add':
            with open(sysinit_file, mode = 'r') as a_file:
                for a_line in a_file:
                    a_line = a_line.rstrip('\r\n')
                    if  re.match("^#",a_line):
    		            continue
                    if a_line == cmd:
                        return 0
            with open(sysinit_file, mode = 'a') as a_file:
                fcntl.flock(a_file, fcntl.LOCK_EX)  
                a_file.write(cmd + '\n')
                fcntl.flock(a_file, fcntl.LOCK_UN) 
                return 0
        elif op == 'del':
            data = ''
            with open(sysinit_file, mode = 'r+') as a_file:
    	        fcntl.flock(a_file, fcntl.LOCK_EX)  
                for a_line in a_file:
                    if re.match("^#",a_line) or  a_line.rstrip('\n') != cmd:
                        data += a_line
                a_file.seek(0)
                a_file.truncate()
                a_file.write(data)
    	        fcntl.flock(a_file, fcntl.LOCK_UN) 
                return 0
                
    
    def create_lvm_table(self):
        ""
        
        create_table_sql = '''CREATE TABLE `lvm` (
                            `lvmName` varchar(64) NOT NULL,
                            `vgName` varchar(200) NOT NULL,
                            `lvmSize` double(24) NOT NULL,
                            `lvmDir`  varchar(128) DEFAULT NULL,
                            `mountDir`  varchar(128) DEFAULT NULL,
                            `lvmMkfs`  varchar(32) DEFAULT NULL,
                            `lvmType`  varchar(32) DEFAULT NULL,
                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark` varchar(1024) DEFAULT NULL,
                             PRIMARY KEY (`lvmName`)
                        )'''
        
        storage_conf = self.conf.get_storage_conf()
        storage_db = storage_conf['db_path']
        sql_tools = SqliteTools(storage_db)
        sql_tools.create_table(create_table_sql)
