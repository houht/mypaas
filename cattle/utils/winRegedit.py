#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201411
#desc: 
#*************************************
import guestfs


class WinRegedit:
    ""
    
    # 注册表打开
    def __init__(self,vm_name):
        ""
        
        # 导入对象
        gfs = guestfs.GuestFS (python_return_dict=True)
        # 导入主机名
        gfs.add_domain(vm_name)
        # 命令交互
        gfs.launch ()
        # 得到系统参数
        roots = gfs.inspect_os ()
        # 根目录
        root = roots[0]
        # 挂载
        gfs.mount_options ("", root, "/")
        # C盘路径
        systemroot = gfs.inspect_get_windows_systemroot (root)
        # 注册表路径
        path = "%s/system32/config/system" % systemroot
        path = gfs.case_sensitive_path (path)
        # 打开注册表，以写的方式
        gfs.hivex_open(path,write=True)
    
        self.gfs = gfs
        # 注册表对象
        self.hive = gfs.hivex_root()

    
    # 注册表修改
    def reg_modify(self,reg_path,reg_key,reg_new_value):
        ""
    
        # 1 得到需要修改的父节点
        reg_path = reg_path.strip("/")
        nodes = reg_path.split("/")
        node = self.hive
        for i in nodes:
            node = self.gfs.hivex_node_get_child(node,i)
        
        # 2 转码
        reg_new_value = reg_new_value.encode ('utf-16le')
        
        # 3 得到修改值的类型
        reg_type = self.gfs.hivex_value_type(self.gfs.hivex_node_get_value (node, reg_key))
        
        # 4 修改
        self.gfs.hivex_node_set_value(node,reg_key,reg_type,reg_new_value)   
        
    
    # 注册表关闭，才会生效
    def reg_close(self):
        ""

        self.gfs.hivex_commit(None)
        self.gfs.sync()
        self.gfs.close()  
        
        
if __name__ == "__main__":
    print "start"
    
    # 修改主机名
    r = WinRegedit('wintest04')
    r.reg_modify('ControlSet001/services/Tcpip/Parameters',"NV Hostname","1234test")
    r.reg_close()
    
    print "end"