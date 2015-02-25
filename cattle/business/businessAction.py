#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from cattle.utils import ParserConf
CONFIG = "/etc/businessAction.conf"


class BusinessAction:
    ""

    def __init__(self, action, msg):
        ""
        
        self.action=action
        self.msg=msg
        self.conf = ParserConf(CONFIG)
    
    
    
    def job(self):
        ""

        # 1 ��ȡ��Ӧ������ͺ���
        class_name = self.conf.get_item(self.action,"class_name")
        action_name = self.conf.get_item(self.action,"action_name")
        
        
        # �쳣����
        if class_name is None or action_name is None:
            pass
  
        # 2 ��������
        # �����
        exec "from cattle.business import " + class_name
        # ��ʼ����
        instance  = eval(class_name)()
        # ������ķ���
        getattr(instance,action_name)(self.msg)
    
    def excpetion(self):
        ""
        
        pass
    
    def result(self):
        ""
        
        pass
    
    