#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201411
#desc: 
#*************************************

import re


from cattle.services import VmManage



#应用基础操作执行容器
class AppExecuter:
    ""
    
    
    def __init__(self):
        ""
        
        self.env = None
        self.properties = None
        
        self.pattern = re.compile(r'(.*)\${(.*)}(.*)')
        self.vm = VmManage()
    
    
    
    # 判断是否为变量
    def _isVar(self, key):
        ""
        
        ma = self.pattern.match(key)
        if ma :
            return True
        else :
            return False
    
     
    # 解析变量，如返回None表示key不是变量，否则返回[字符,变量名,字符串]
    def parseVar(self, key):
        ""
        
        ma = self.pattern.match(key)
        if ma :
            return ma.groups()
        return None
    
    
    
    # 获取property参数
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
    
    # 参数处理
    def proces_param(self,params):
        
        temp = {}
        
        
        # 1 获取参数 
        for key in params.keys():
            if self._isVar(params[key]):
                value = self.parseVar(params[key])
                temp[key] = value[0] + str(self.getProperty(self.properties, value[1], self.env)) + value[2]
            else:
                temp[key] = params[key]
        
        return  temp

    
    
    # 创建vm
    def createVm(self,params):
        ""
        
        
        value = self.proces_param(params)

        # 调用创建函数
        self.vm.create_vm(image_name=value['imageId'],vm_name=value['domain'],mem_size=value['mem'],vcpus=value['cpu'],vm_size=value['disk'],host_name=value['hostName'])
        
        
        # 设置环境变量
        info = self.vm.info_vm(value['domain'])
        self.env.set_vm_env('ip',info['ip'])
        
    
    # vm创建磁盘
    def createDisk(self,params):
        ""

        value = self.proces_param(params)

        # 调用创建磁盘函数
        self.vm.attach_disk(value['domain'],value['target'],value['size'])
    
    
    #vm挂载磁盘
    def mountDisk(self,params):
        ""
        
        value = self.proces_param(params)
        
        # 调用创建磁盘函数
        dict_part={}
        dict_part[value['target']] = value['path']
        
        self.vm.add_os_mount(value['domain'],dict_part)
    
    
    #vm创建目录
    def mkdir(self,params):
        ""
        
        value = self.proces_param(params)
        
        # 调用创建目录函数
        self.vm.mkdir(value['domain'],value['target'],value['dir'])
    
    
    #上传单个文件
    def upload(self,params):
        ""
    
        value = self.proces_param(params)
        
        # 调用设置主机名
        self.vm.upload(value['domain'],value['target'],value['src'],value['todir'])
    
    
    #上传压缩文件
    def tgzIn(self,params):
        ""
        
        value = self.proces_param(params)
        
        # 压缩文件上传
        self.vm.tgzin(value['domain'],value['target'],value['src'],value['todirectory'])
    

    #设置环境变量
    def setEvn(self,params):
        ""
        
        value = self.proces_param(params)
        
        # 调用创建环境变量
        dict_envs = {}
        dict_envs[value['name']] = value['message']
        self.vm.set_os_env_var(value['domain'],dict_envs)
        
        
    #设置主机名
    def setHost(self,params):
        ""
        
        value = self.proces_param(params)

        # 调用设置主机名
        self.vm.set_os_hostname(value['domain'],value['name'])
    
        
    #注册表修改，Windows
    def reg(self,params):
        ""
        
        value = self.proces_param(params)
    
         
    #端口代理
    def portProxyRegister(self,params):
        ""
        
        value = self.proces_param(params)
        
        proxy_ip,proxy_port = self.vm.proxy_add(vm_name = value['domain'],ip = value['ip'],port = value['port'])
        
        
        self.env.set_proxy_env("proxyIp",proxy_ip)
        self.env.set_proxy_env("proxyPort",proxy_port)
        
        self.env.set_proxy_env("ip",value['ip'])
        self.env.set_proxy_env("port",value['port'])
        
    
    #参数返回
    def returnParam(self,params):
        ""
        
        value = self.proces_param(params)
        
        self.env.set_global_env('returnParam',value)
        
       
    #启动vm
    def startVm(self,params):
        ""
        
        value = self.proces_param(params)

        # 调用启动
        self.vm.start_vm(value['domain'])
    
        
        
    #关闭vm
    def shutdown(self,params):
        ""
        
        value = self.proces_param(params)
        
        
        # 调用启动
        self.vm.shutdown_vm(value['domain'])
    
    
    #关闭vm 强制
    def destroy(self,params):
        ""
        
        value = self.proces_param(params)
        # 调用启动
        self.vm.destroy_vm(value['domain'])

        
    #删除vm
    def dropVm(self,params):
        ""
        
        value = self.proces_param(params)
                
        
        # 调用启动
        self.vm.delete_vm(value['domain'])


if __name__ == "__main__" :
    print "start"
    aa = AppExecuter()
    print "end"
