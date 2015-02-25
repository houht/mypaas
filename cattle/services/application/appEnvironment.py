#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201411
#desc: 
#*************************************
import os
import sys
from cattle.utils import DictBean

class AppEnv(DictBean) :
    "evn manage"    
        
    def __init__(self) :
        ""
        DictBean.__init__(self)
    
    #设置公共环境变量
    def set_global_env(self, name, value):
        self.set('env.'+name, value)
    
    #设置虚拟化环境变量
    def set_vm_env(self, name, value):
        #DictBean.set(self, 'env.vm.'+name, value)
        self.set('env.vm.'+name, value)
        
    #设置服务环境变量
    def set_service_env(self, name, value):
        self.set('env.service.'+name, value)
        
    #设置应用环境变量
    def set_app_env(self, name, value):
        self.set('env.app.'+name, value)
    
    #设置负载环境变量
    def set_router_env(self, name, value):
        self.set('env.router.'+name, value)
    
    #设置负载环境变量
    def set_proxy_env(self, name, value):
        self.set('env.proxy.'+name, value)
    
    #读取公共环境变量
    def get_global_env(self, name):
        return self.get('env.'+name)
        
    #读取虚拟化环境变量
    def get_service_env(self, name):
        return self.get('env.service.'+name)
        
    #读取虚拟化环境变量
    def get_vm_env(self, name):
        return self.get('env.vm.'+name)
    
    #读取应用环境变量
    def get_app_env(self, name):
        return self.get('env.app.'+name)
    
    #读取路由环境变量
    def get_router_env(self, name):
        return self.get('env.router.'+name)
    
    #读取路由环境变量
    def get_proxy_env(self, name):
        return self.get('env.proxy.'+name)
        
    #判断变量是否为环境变量，这里只判断是否为env.开头
    @staticmethod
    def is_env_var(name) :
        keys = name.split('.')
        if keys[0] != 'env' :
            return False
        else :
            return True            
        
if __name__ == "__main__":
    env = AppEnv()
    env.set_vm_env('domain',"domain_iiddd")
    env.set_global_env('glb','ddfadsf')
    env.set_app_env('app.file','esss')   
    print env.is_env_var('vm.domain')
    print env.is_env_var('env.vm.domain')
    print env.is_env_var('env.vm.domain')
    
    print env.get_vm_env('domain')
    