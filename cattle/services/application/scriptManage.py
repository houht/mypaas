#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201411
#desc: 
#*************************************
import os
import sys
import copy

from cattle.services import ConfigManage

from cattle.utils import CustomException

from appService import AppService


class ScriptManage() :
    "script manage"
    
    __inst = None    
    @staticmethod
    def getInstance():
        if not ScriptManage.__inst:
            ScriptManage.__inst = ScriptManage()
        return ScriptManage.__inst
    
    def __init__(self) :
        ""
        self.conf = ConfigManage()
        self.cattle_conf = self.conf.get_cattle_conf()
        self.scriptPath = self.cattle_conf['scriptPath']
        self.services = {}
        self.loaded = False
        self.load()
    
    #���ط�������
    def load(self) :
        if self.loaded == True:
            return True
        for root, dirs, files in os.walk(self.scriptPath):
            for fn in files:
                filename = os.path.join(root,fn)
                self.loadone(filename)
        self.loaded = True
    
    
    #���¼��ط�������
    def reload(self) :
        self.loaded = False
        self.load()
    
    #����һ�����������ļ�
    def loadone(self, filename) :
        try:
            apps = AppService(filename)
        except Exception , e:
            raise CustomException("Load xml error: %s" % str(e) )
        self.services[apps.name] = apps
    
    
    #ͨ���������ƻ�ȡ�������
    def getService(self, name) :
        if self.hasService(name):
            service = self.services[name]
            return service
        else:
            None
            
    #�жϷ����Ƿ����
    def hasService(self, name) :
        if not self.loaded:
            self.load()
        return self.services.has_key(name) 


if __name__ == "__main__":
    a = ScriptManage.getInstance()
    a.load()
    bb = a.getService('tomcat7')
    print bb.target.actions.keys()
    
    
       