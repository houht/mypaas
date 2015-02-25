#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201410
#desc: sysmonitor util

import os

class Option :
    def __init__(self) :
        pass

    def prints(self,options) :
        content = ""
        if options in (None,"") :
            return ""
        for k in options :
            content += "%s %s;\r\n"%(k, options[k])
        return content

class Host(Option):
    def __init__(self):
        Option.__init__(self)

    def prints(self, hostname, options) :
        content = Option.prints(self, options)
        host = "host %s {\r\n%s\r\n}\r\n"%(hostname, content)
        return host

class Subnet(Option, Host):
    def __init__(self):
        Option.__init__(self)

    def prints(self,ip, mask, options, hosts=None) :
        content = Option.prints(self, options)
        str_hosts = ""
        if hosts not in [None, '']:
            for shost in hosts:
                str_hosts += Host.prints(self, shost["hostname"], shost["options"])
                str_hosts += "\r\n"
        
        subnet = "subnet %s netmask %s {\r\n%s\r\n%s\r\n}\r\n" % (ip, mask, content, str_hosts)
        return subnet

class Dhcp(Subnet, Host, Option) :
    #conf_file配置文件名全路径，service_name服务名称，如dhcpd
    def __init__(self, conf_file, service_name):
        self.conf = conf_file
        self.service_name = service_name
        Subnet.__init__(self)
        Host.__init__(self)
        Option.__init__(self)

    #重写dhcp配置文件
    def write_conf(self, subnets, options, hosts) :
        '''
        subnets = [{'ip':'192.168.0.0','mask':'255.255.255.0',
                    'options':{'option routers': '192.168.12.1','option subnet-mask':'255.255.255.0'},
                    'hosts':[{"hostname":'xxxx','options':{'option host-name':'dddd','hardware ethernet':'12:34:56:78:AB:CD','fixed-address':'207.175.42.254'}}]}
                  ]
        options = {'option routers': '192.168.12.1','option subnet-mask':'255.255.255.0'}
        hosts = [{"hostname":'xxxx','options':{'option host-name':'dddd','hardware ethernet':'12:34:56:78:AB:CD','fixed-address':'207.175.42.254'}}]}
        subnets中的options和hosts均可以不设置
        options 可以为None
        hosts 可以为None        
        '''
        str_options = Option.prints(self, options)
        
        str_subnets = ""
               
        for snet in subnets:
            snet_hosts = None
            snet_options = None
            if 'hosts' in snet :
                snet_hosts = snet["hosts"]
            if 'options' in snet :
                snet_options = snet["options"]
            str_subnets = str_subnets + Subnet.prints(self, snet["ip"], snet["mask"], snet_options, snet_hosts) + "\r\n"            
        
        str_hosts = ""
        if hosts not in [None, ''] :
            for shost in hosts:
                str_hosts += Host.prints(self, shost["hostname"], shost["options"])
                str_hosts += "\r\n"
        
        fileObject = open(self.conf,"w")
        fileObject.write(str_options)
        fileObject.write(str_subnets)
        fileObject.write(str_hosts)
        fileObject.close()

    #重新启动dhcp进程，启动成功，返回进程ID，失败返回None
    def restart(self) :
        cmd = 'service %s restart' % self.service_name
        lines = os.popen(cmd,'r').readlines()
        cmd = 'ps aux|grep dhcp |grep -v grep'
        lines = os.popen(cmd,'r').readlines()
        if lines != None and len(lines) > 0:
            con = lines[0].split()
            if len(con) > 5:
                return con[1]
        return None


