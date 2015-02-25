#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201411
#desc: 
#*************************************

import re


from cattle.services import VmManage



#Ӧ�û�������ִ������
class AppExecuter:
    ""
    
    
    def __init__(self):
        ""
        
        self.env = None
        self.properties = None
        
        self.pattern = re.compile(r'(.*)\${(.*)}(.*)')
        self.vm = VmManage()
    
    
    
    # �ж��Ƿ�Ϊ����
    def _isVar(self, key):
        ""
        
        ma = self.pattern.match(key)
        if ma :
            return True
        else :
            return False
    
     
    # �����������緵��None��ʾkey���Ǳ��������򷵻�[�ַ�,������,�ַ���]
    def parseVar(self, key):
        ""
        
        ma = self.pattern.match(key)
        if ma :
            return ma.groups()
        return None
    
    
    
    # ��ȡproperty����
    def getProperty(self, properties, key, env):
        ""
        
        if not properties.has_key(key):
            if not env.is_env_var(key):
                return None
            else :
                return env.get(key)
        else :
            value = properties[key]
            vars = self.parseVar(value)
            if vars :
                return vars[0] + self.getProperty(self.properties,vars[1],self.env) + vars[2]
            else :
                return value;
    
    # ��������
    def proces_param(self,params):
        
        temp = {}
        
        
        # 1 ��ȡ���� 
        for key in params.keys():
            if self._isVar(params[key]):
                value = self.parseVar(params[key])
                temp[key] = value[0] + str(self.getProperty(self.properties, value[1], self.env)) + value[2]
            else:
                temp[key] = params[key]
        
        return  temp

    
    
    # ����vm
    def createVm(self,params):
        ""
        
        
        value = self.proces_param(params)

        # ���ô�������
        self.vm.create_vm(image_name=value['imageId'],vm_name=value['domain'],mem_size=value['mem'],vcpus=value['cpu'],vm_size=value['disk'],host_name=value['hostName'])
        
        
        # ���û�������
        info = self.vm.info_vm(value['domain'])
        self.env.set_vm_env('ip',info['ip'])
        
    
    # vm��������
    def createDisk(self,params):
        ""

        value = self.proces_param(params)

        # ���ô������̺���
        self.vm.attach_disk(value['domain'],value['target'],value['size'])
    
    
    #vm���ش���
    def mountDisk(self,params):
        ""
        
        value = self.proces_param(params)
        
        # ���ô������̺���
        dict_part={}
        dict_part[value['target']] = value['path']
        
        self.vm.add_os_mount(value['domain'],dict_part)
    
    
    #vm����Ŀ¼
    def mkdir(self,params):
        ""
        
        value = self.proces_param(params)
        
        # ���ô���Ŀ¼����
        self.vm.mkdir(value['domain'],value['target'],value['dir'])
    
    
    #�ϴ������ļ�
    def upload(self,params):
        ""
    
        value = self.proces_param(params)
        
        # ��������������
        self.vm.upload(value['domain'],value['target'],value['src'],value['todir'])
    
    
    #�ϴ�ѹ���ļ�
    def tgzIn(self,params):
        ""
        
        value = self.proces_param(params)
        
        # ѹ���ļ��ϴ�
        self.vm.tgzin(value['domain'],value['target'],value['src'],value['todirectory'])
    

    #���û�������
    def setEvn(self,params):
        ""
        
        value = self.proces_param(params)
        
        # ���ô�����������
        dict_envs = {}
        dict_envs[value['name']] = value['message']
        self.vm.set_os_env_var(value['domain'],dict_envs)
        
        
    #����������
    def setHost(self,params):
        ""
        
        value = self.proces_param(params)

        # ��������������
        self.vm.set_os_hostname(value['domain'],value['name'])
    
        
    #ע����޸ģ�Windows
    def reg(self,params):
        ""
        
        value = self.proces_param(params)
    
         
    #�˿ڴ���
    def portProxyRegister(self,params):
        ""
        
        value = self.proces_param(params)
        
        proxy_ip,proxy_port = self.vm.proxy_add(vm_name = value['domain'],ip = value['ip'],port = value['port'])
        
        
        self.env.set_proxy_env("proxyIp",proxy_ip)
        self.env.set_proxy_env("proxyPort",proxy_port)
        
        self.env.set_proxy_env("ip",value['ip'])
        self.env.set_proxy_env("port",value['port'])
        
    
    #��������
    def returnParam(self,params):
        ""
        
        value = self.proces_param(params)
        
        self.env.set_global_env('returnParam',value)
        
       
    #����vm
    def startVm(self,params):
        ""
        
        value = self.proces_param(params)

        # ��������
        self.vm.start_vm(value['domain'])
    
        
        
    #�ر�vm
    def shutdown(self,params):
        ""
        
        value = self.proces_param(params)
        
        
        # ��������
        self.vm.shutdown_vm(value['domain'])
    
    
    #�ر�vm ǿ��
    def destroy(self,params):
        ""
        
        value = self.proces_param(params)
        # ��������
        self.vm.destroy_vm(value['domain'])

        
    #ɾ��vm
    def dropVm(self,params):
        ""
        
        value = self.proces_param(params)
                
        
        # ��������
        self.vm.delete_vm(value['domain'])


if __name__ == "__main__" :
    print "start"
    aa = AppExecuter()
    print "end"
