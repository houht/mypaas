#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201411
#desc: xml util
# usage
#
#*************************************

import os
import sys
import time

from  xml.dom import  minidom

class XmlDom :	
    def __init__ (self) :
	pass

    @staticmethod
    def getDoc(filename):
        '''通过文件名获得dom文档对象'''
        doc = minidom.parse(filename)
        return doc

    @staticmethod
    def getRoot(doc):
        '''获取根节点'''
        return doc.documentElement

    @staticmethod
    def getEncoding(doc):
        '''获取文档的编码'''
        return doc.encoding
        
    @staticmethod
    def getAttrvalue(node, attrname):
        '''获取节点的指定属性值'''
        return node.getAttribute(attrname)

    @staticmethod
    def getAttributes(node):
        '''获取指定节点的属性字典'''
        attrs = node.attributes
        
        keys = attrs.keys()
        dict_attrs = {}
        for key in keys:
            dict_attrs[key] = attrs[key].nodeValue
        return dict_attrs
            
    @staticmethod
    def getNodeValue(node, index = 0):
        '''获取指定节点的值'''
        return node.childNodes[index].nodeValue
    
    @staticmethod
    def getElementsByTagName(node, name):
        '''获取指定节点下的所有子节点（含子子节点）名字为name的节点集合'''
        return node.getElementsByTagName(name)

    @staticmethod
    def getChilds(node):
        '''获取指定节点下的所有子节点'''
        list = node.childNodes
        for i in range(len(list)-1,-1,-1):
            nd = list[i]
            if nd.nodeType != nd.ELEMENT_NODE :
                del list[i]
        return list
    

        
if __name__ == "__main__" :
    doc = XmlDom.getDoc('/root/test/tomcat_service.xml')
    root = XmlDom.getRoot(doc)    
    list = XmlDom.getChilds(root)
    for node in list:
        print node.nodeName, node.nodeType, node.nodeValue, XmlDom.getAttributes(node)
        
