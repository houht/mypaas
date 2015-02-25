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
    
    # ע����
    def __init__(self,vm_name):
        ""
        
        # �������
        gfs = guestfs.GuestFS (python_return_dict=True)
        # ����������
        gfs.add_domain(vm_name)
        # �����
        gfs.launch ()
        # �õ�ϵͳ����
        roots = gfs.inspect_os ()
        # ��Ŀ¼
        root = roots[0]
        # ����
        gfs.mount_options ("", root, "/")
        # C��·��
        systemroot = gfs.inspect_get_windows_systemroot (root)
        # ע���·��
        path = "%s/system32/config/system" % systemroot
        path = gfs.case_sensitive_path (path)
        # ��ע�����д�ķ�ʽ
        gfs.hivex_open(path,write=True)
    
        self.gfs = gfs
        # ע������
        self.hive = gfs.hivex_root()

    
    # ע����޸�
    def reg_modify(self,reg_path,reg_key,reg_new_value):
        ""
    
        # 1 �õ���Ҫ�޸ĵĸ��ڵ�
        reg_path = reg_path.strip("/")
        nodes = reg_path.split("/")
        node = self.hive
        for i in nodes:
            node = self.gfs.hivex_node_get_child(node,i)
        
        # 2 ת��
        reg_new_value = reg_new_value.encode ('utf-16le')
        
        # 3 �õ��޸�ֵ������
        reg_type = self.gfs.hivex_value_type(self.gfs.hivex_node_get_value (node, reg_key))
        
        # 4 �޸�
        self.gfs.hivex_node_set_value(node,reg_key,reg_type,reg_new_value)   
        
    
    # ע���رգ��Ż���Ч
    def reg_close(self):
        ""

        self.gfs.hivex_commit(None)
        self.gfs.sync()
        self.gfs.close()  
        
        
if __name__ == "__main__":
    print "start"
    
    # �޸�������
    r = WinRegedit('wintest04')
    r.reg_modify('ControlSet001/services/Tcpip/Parameters',"NV Hostname","1234test")
    r.reg_close()
    
    print "end"