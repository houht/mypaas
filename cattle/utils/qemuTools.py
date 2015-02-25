#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from command import Command

class QemuTools:
    "qemu-img tools"
    
    
    def __init__(self):
        ""

        self.cmd = Command() 
        self.qemu_cmd = "qemu-img"
        

    def create_img(self,**kwargs):
        ""
        
        #����ģ��
        basefile   = kwargs.pop('basefile', None)
        filename   = kwargs.pop('filename', None)
        #����
        fmt        = kwargs.pop('fmt', 'qcow2')
        
        self.cmd.execute(self.qemu_cmd , 'create' ,'-b',basefile,'-f',fmt,filename)