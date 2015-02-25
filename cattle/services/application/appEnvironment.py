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
    
    #���ù�����������
    def set_global_env(self, name, value):
        self.set('env.'+name, value)
    
    #�������⻯��������
    def set_vm_env(self, name, value):
        #DictBean.set(self, 'env.vm.'+name, value)
        self.set('env.vm.'+name, value)
        
    #���÷��񻷾�����
    def set_service_env(self, name, value):
        self.set('env.service.'+name, value)
        
    #����Ӧ�û�������
    def set_app_env(self, name, value):
        self.set('env.app.'+name, value)
    
    #���ø��ػ�������
    def set_router_env(self, name, value):
        self.set('env.router.'+name, value)
    
    #���ø��ػ�������
    def set_proxy_env(self, name, value):
        self.set('env.proxy.'+name, value)
    
    #��ȡ������������
    def get_global_env(self, name):
        return self.get('env.'+name)
        
    #��ȡ���⻯��������
    def get_service_env(self, name):
        return self.get('env.service.'+name)
        
    #��ȡ���⻯��������
    def get_vm_env(self, name):
        return self.get('env.vm.'+name)
    
    #��ȡӦ�û�������
    def get_app_env(self, name):
        return self.get('env.app.'+name)
    
    #��ȡ·�ɻ�������
    def get_router_env(self, name):
        return self.get('env.router.'+name)
    
    #��ȡ·�ɻ�������
    def get_proxy_env(self, name):
        return self.get('env.proxy.'+name)
        
    #�жϱ����Ƿ�Ϊ��������������ֻ�ж��Ƿ�Ϊenv.��ͷ
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
    