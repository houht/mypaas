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


# 参数对象
class propertys:
    ""
    
    def __init__(self):
        ""
        
        self.name =  'property'
        self.parameter = {}
    
    
    def get_value(self):
        ""
   
        pass
        

# target对象
class target:
    ""
    
    def __init__(self):
        ""
        
        self.name =  "target"
        self.actions = {}



# xml解析
class AppService:
    "application service"


    def __init__(self,xml_file):
        ""
        
        self.doc = XmlDom.getDoc(xml_file)
        self.name = ''
        self.serviceType = ''
        
        self.propertys = propertys()
        self.target = target()
        
        #解析
        self.parse()
    
    
    def parse(self):
        ""
        
        # 导入xml
        root = XmlDom.getRoot(self.doc)  
        root_att = XmlDom.getAttributes(root)
        # 得到xml的属性
        self.serviceType = root_att['serviceType']
        self.name = root_att['name']
        
        # 循环xml文件
        xml_list = XmlDom.getChilds(root)
        for node in xml_list:
            
            # 参数列表
            if node.nodeName == self.propertys.name:
                node_att = XmlDom.getAttributes(node)
                self.propertys.parameter[node_att['name']] = node_att['value']
            
            # target列表
            if node.nodeName == self.target.name:
               
                # 响应
                action = XmlDom.getAttributes(node)['name']
                child_node = XmlDom.getChilds(node)
                # 保存每个执行对象下面的执行函数和参数
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

    
    
    
    
       
        