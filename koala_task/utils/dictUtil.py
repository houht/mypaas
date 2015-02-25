#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201411
#desc: 
#*************************************
import os
import sys

class DictBean() :
    "evn manage"
    
        
    def __init__(self) :
        ""
        self.bean = {}
        pass
    
    def _check(self, dict_name, name):
        return dict_name.has_key(name)
    
    def _get(self, dict_name, name):
        return dict_name[name]
    
    #通过.的方式设置变量参数如，vm.domain,xxx等
    def set(self, name, value):
        keys = name.split('.')
        dict_name = self.bean
        length = len(keys)
        for i in range(0, length):
            var = keys[i]
            if i == length - 1:
                dict_name[var] = value
            else :
                if not self._check(dict_name, var):
                    dict_name[var] = {}
                dict_name = dict_name[var]
                        
         
    #通过.的方式读取环境变量如env.vm.domain,env.xxx等
    def get(self, name):
        keys = name.split('.')
            
        dict_name = self.bean
        length = len(keys)
        for i in range(0,length):
            var = keys[i]
            if not self._check(dict_name, var):
                return None
            if i == length - 1:
                return self._get(dict_name, var)
            else :
                dict_name = dict_name[var]
                
    def keys(self):
        return self.bean.keys()
            
if __name__ == "__main__":
    bean = DictBean()
    bean.set('en.vm.domain','domain_uuid')
    bean.set('en.vm.hostName','host1')
    bean.set('en.app.file','/data/appfile/weiiewe/aaa.tgz')
    
    bean.set('aa','/data/appfile/weiiewe/aaa.tgz')
    
    print bean.get('en')
    print bean.get('en.vm')
    print bean.get('en.vm.domain')
    print bean.keys()
    
       