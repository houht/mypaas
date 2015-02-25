#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201411
#desc: 
#*************************************
import re
from cattle.utils import XmlDom


pattern = re.compile(r'(.*)\${(.*)}(.*)')


# ��������
class propertys:
    ""
    
    def __init__(self):
        ""
        
        self.name =  'property'
        self.parameter = {}
    
    
    def get_value(self):
        ""
   
        pass
        

# target����
class target:
    ""
    
    def __init__(self):
        ""
        
        self.name =  "target"
        self.actions = {}



# xml����
class AppService:
    "application service"


    def __init__(self,xml_file):
        ""
        
        self.doc = XmlDom.getDoc(xml_file)
        self.name = ''
        self.serviceType = ''
        
        self.propertys = propertys()
        self.target = target()
        
        #����
        self.parse()
    
    
    def parse(self):
        ""
        
        # ����xml
        root = XmlDom.getRoot(self.doc)  
        root_att = XmlDom.getAttributes(root)
        # �õ�xml������
        self.serviceType = root_att['serviceType']
        self.name = root_att['name']
        
        # ѭ��xml�ļ�
        xml_list = XmlDom.getChilds(root)
        for node in xml_list:
            
            # �����б�
            if node.nodeName == self.propertys.name:
                node_att = XmlDom.getAttributes(node)
                self.propertys.parameter[node_att['name']] = node_att['value']
            
            # target�б�
            if node.nodeName == self.target.name:
               
                # ��Ӧ
                action = XmlDom.getAttributes(node)['name']
                child_node = XmlDom.getChilds(node)
                # ����ÿ��ִ�ж��������ִ�к����Ͳ���
                lis = []
                for child in child_node:
                    tmp = {}
                    tmp['action'] = child.nodeName
                    tmp['param'] = XmlDom.getAttributes(child)
                    lis.append(tmp)
                self.target.actions[action] = lis
            
                
if __name__ == "__main__" :
    print "start"
    aa = AppService('/root/test/tomcat_service.xml')
    print "propertys"
    print aa.propertys.parameter
    print "target"
    print aa.target.actions
    print "end"

    
    
    
    
       
        