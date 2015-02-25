#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201411
#desc: guestfs util
# usage
#
# 
# 
#
#
#*************************************

import os
import sys
import time
import socket

import guestfs

class VirtGuestfs :
    def __init__ (self, domain, imgfile) :
		self.domain = domain
		self.imgfile = imgfile
		self.handle = None
		self.hivexRoot = None
		self.roots = None
		 
    #加载磁盘或系统
    def launch(self, readonly=False) :
        try:
            self.handle = guestfs.GuestFS (python_return_dict=True, close_on_exit=True)
        except TypeError as e:
            if 'close_on_exit' in six.text_type(e) or 'python_return_dict' in six.text_type(e):
                self.handle = guestfs.GuestFS()
            else:
                raise
        
        if self.domain is not None :
            if readonly :
                self.handle.add_domain(self.domain, readonly=readonly, readonlydisk='read')
            else :
                self.handle.add_domain(self.domain, readonly=readonly, readonlydisk='write')
        else :
             self.handle.add_drive(self.imgfile, readonly)        
        self.handle.launch()
    
    #挂载文件
    def mount_os(self, partition=None) :
        if partition is None :
            self.mount_os_inspect()
        else :
            self.mount_static(partition)
    
    #静态挂载
    def mount_static(self, partition=None):
        filesystems = self.handle.list_filesystems()
        keys = filesystems.keys()
        keys.sort()
        if partition:
            #self.handle.mount_options("", "/dev/sda%d" % partition, "/")
            part = filesystems[keys[partition]]
            self.handle.mount_options("", part, "/")
            self.roots = [part]
        else:
            self.handle.mount_options("", keys[0], "/")
            self.roots = [keys[0]]
    
    #挂载系统文件
    def mount_os_inspect(self):
        roots = self.handle.inspect_os()
        self.roots = roots
        if len(roots) == 0:
            raise Exception("No operating system found in %s,%s"
                                          % (self.domain,self.imgfile))
        if len(roots) != 1:
            raise Exception("Multi-boot operating system found in %s or %s" % (self.domain,self.imgfile))
        
        self.setup_os_root(roots[0])
    
    #挂载系统文件
    def setup_os_root(self, root):
        mounts = self.handle.inspect_get_mountpoints(root)
        #print mounts
        if len(mounts) == 0:
            raise Exception("No mount points found in %s of (%s or %s)" %
                (root, self.domain, self.imgfile))
        
        # the root directory must be mounted first
        #mounts.sort(key=lambda mount: mount[0])
        root_mounted = False
        keys = mounts.keys()
        keys.sort()
        for key in keys:
            mount = [key, mounts[key]]
            try:
                #print 'mount options=',mount[1], mount[0]
                self.handle.mount_options("", mount[1], mount[0])
                root_mounted = True
            except RuntimeError as e:
#                msg = "Error mounting %(device)s or %() to %(dir)s in image  %(imgfile)s or %(domain)s with libguestfs %(except)s" % \
#                      {'imgfile': self.imgfile, 'domain': self.domain, 'device': mount[1], 'dir': mount[0], 'except': str(e)}
                msg = str(e)
                if root_mounted == False :
                    raise Exception(msg)
            #print mount[1], mount[0], root_mounted
            
    #上传文件
    def upload(self, filename, remotefilename) :
        self.handle.upload(filename, remotefilename)
    
    #上传tgz文件，删除后自动解压到执行目标
    def tgz_in(self, tarball, directory):
        self.handle.tgz_in(tarball, directory)
    
    #建立文件夹
    def make_path(self, path):
        self.handle.mkdir_p(path)
    
    #向文件追加内容
    def append_file(self, path, content):
        self.handle.write_append(path, content)
    
    #替换文件内容
    def replace_file(self, path, content):
        self.handle.write(path, content)
    
    #读文件内容
    def read_file(self, path):
        return self.handle.read_file(path)
    
    #文件是否存在
    def has_file(self, path):
        try:
            self.handle.stat(path)
            return True
        except RuntimeError:
            return False
    
    #设置文件或文件夹属性
    def set_chmod(self, path, mode):
        self.handle.chmod(mode, path)
    
    #设置文件或文件夹所属组
    def set_ownership(self, path, user, group):
        uid = -1
        gid = -1
        if user is not None:
            uid = int(self.handle.aug_get("/files/etc/passwd/" + user + "/uid"))
        if group is not None:
            gid = int(self.handle.aug_get("/files/etc/group/" + group + "/gid"))
        self.handle.chown(uid, gid, path)
    
    def list_filesystems(self):
        filesystems = self.handle.list_filesystems()
        return filesystems
        
    #打开windows注册表
    def reg_open(self, write=True):
        # 得到系统参数
        if self.roots is None :
            self.roots = self.handle.inspect_os ()
            self.handle.mount_options("", roots[0], "/")
            
        # 根目录
        root = self.roots[0]
        # windows系统路径
        systemroot = self.handle.inspect_get_windows_systemroot (root)
        # 注册表路径
        path = "%s/system32/config/system" % systemroot
        path = self.handle.case_sensitive_path (path)
        # 打开注册表，以写的方式
        #print write
        self.handle.hivex_open(path, write=write)
        # 注册表对象
        self.hivexRoot = self.handle.hivex_root()
    
    # 注册表修改
    def reg_modify(self,reg_path, reg_key, reg_type, reg_new_value):
        ""
    
        # 1 得到需要修改的父节点
        reg_path = reg_path.strip("/")
        nodes = reg_path.split("/")
        node = self.hivexRoot
        for i in nodes:
            node = self.handle.hivex_node_get_child(node,i)
        
        # 2 转码
        reg_new_value = reg_new_value.encode ('utf-16le')
        
        # 3 得到修改值的类型
        #reg_type = self.handle.hivex_value_type(self.handle.hivex_node_get_value (node, reg_key))
        
        # 4 修改
        self.handle.hivex_node_set_value(node,reg_key,reg_type,reg_new_value)
        
    #同步注册表修改内容
    def reg_commit(self):
        self.handle.hivex_commit(None)
        self.handle.sync()
    
    #格式化盘
    def disk_mkfs(self, fs_type, label=None):
        if self.imgfile is None:
            raise Exception("imgfile can not is None")
        
        if label:
            cmd = 'mkfs -t %s -L %s %s' % (fs_type, label, self.imgfile)
        else:
            cmd = 'mkfs -t %s %s' % (fs_type, self.imgfile)
        lines = os.popen(cmd,'r').readlines()
        
        return True
        
    # 注册表关闭，才会生效
    def close(self):
        ""
        try:
            try:
                self.handle.aug_close()
            except Exception as e:
                pass

            try:
                self.handle.shutdown()
            except AttributeError:
                # Older libguestfs versions haven't an explicit shutdown
                pass
            except RuntimeError as e:
                # Failed to shutdown appliance
                pass

            try:
                self.handle.close()
            except AttributeError:
                # Older libguestfs versions haven't an explicit close
                pass
            except RuntimeError as e:
                # Failed to close guest handle
                pass
        finally:
            # dereference object and implicitly close()
            self.handle = None

if __name__ == "__main__":
    print "start"
    #写注册表
    #g = VirtGuestfs('wintest04',None)
    #g.launch()
    #g.mount_os()
    #g.reg_open()
    #g.reg_modify('ControlSet001/services/Tcpip/Parameters',"NV Hostname",1L,"1234test")
    #g.reg_commit()
    #g.close()
    
    #拷贝文件
    #g = VirtGuestfs(None,'/dev/testvg/windisk02')
    #g.launch()
    #g.mount_static()
    #g.tgz_in('/root/lockfile-0.8.tar.gz','/')
    #g.close()
    
    #查看文件
    #g = VirtGuestfs(None,'/dev/testvg/windisk02')
    #g.launch(readonly=True)
    #g.mount_static()
    #print g.read_file('/hello2')
    #g.close()
    
    #磁盘格式化
    g = VirtGuestfs(None,'/dev/testvg/test_05')
    flag = g.disk_mkfs('ntfs',label='data')
    g.close()
    print "end"