#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from cattle.utils import JsonParser
from cattle.utils import RabbitMq
from cattle.utils import LoggerUtil

from cattle.services import ConfigManage
from cattle.services import VmManage

class NetBusiness:
    ""
    
    def __init__(self):
        ""
        
        self.logger = LoggerUtil().getLogger()
        
        self.vm = VmManage()

        conf = ConfigManage()
        # mq配置
        mq_conf = conf.get_mq_conf()
        self.mq_addr = mq_conf['mq_addr']
        self.task_exchange = mq_conf['task_exchange']
        self.task_type = mq_conf['task_type']
        
        # 消息
        self.messages = {}
        res = 'task_rst'
        
        # 代理成功
        self.messages['network_portproxy_ok'] = 'network.portproxy.ok'
        self.messages['network_portproxy_ok_router'] = res + '.network.portproxy.ok'
        
        # 代理失败
        self.messages['network_portproxy_error'] = 'network.portproxy.error'
        self.messages['network_portproxy_error_router'] = res + '.network.portproxy.error'
        self.messages['network_portproxy_error_code'] = 2001
        
        
        # 删除代理成功
        self.messages['network_dropportproxy_ok'] = 'network.dropportproxy.ok'
        self.messages['network_dropportproxy_ok_router'] = res + '.network.dropportproxy.ok'
        
        # 删除代理失败
        self.messages['network_dropportproxy_error'] = 'network.dropportproxy.error'
        self.messages['network_dropportproxy_error_router'] = res + '.network.dropportproxy.error'
        self.messages['network_dropportproxy_error_code'] = 2002
        
        # 查询代理成功
        self.messages['network_findportproxy_ok'] = 'network.findportproxy.ok'
        self.messages['network_findportproxy_ok_router'] = res + '.network.findportproxy.ok'
        
        # 查询代理失败
        self.messages['network_findportproxy_error'] = 'network.findportproxy.error'
        self.messages['network_findportproxy_error_router'] = res + '.network.findportproxy.error'
        self.messages['network_findportproxy_error_code'] = 2003
        
        
    # 添加代理端口
    def port_proxy(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        port = json_msg['content']['port']
        ip = json_msg['content']['ip']
        proxyType = json_msg['content']['type']
        
        message_ok = json_msg
        
        try:
            proxy_ip,proxy_port= self.vm.proxy_add(vm_name=name,ip=ip,port=port,proxy_type=proxyType)
            message_ok['content']['proxyIp'] = proxy_ip
            message_ok['content']['proxyPort'] = proxy_port 
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['network_portproxy_error_code']
            message_error['content']['errorMessage'] = 'port proxy error: ' + str(e) 
            message_error['action'] = self.messages['network_portproxy_error']
            self.send_msg(self.messages['network_portproxy_error_router'],message_error)
            return
        
        
        message_ok['action'] = self.messages['network_portproxy_ok']
        self.send_msg(self.messages['network_portproxy_ok_router'],message_ok)
    
    
    # 删除代理端口
    def drop_proxy(self,json_msg):
        ""
        
        name = json_msg['content']['vmName']
        port = json_msg['content']['port']
        ip = json_msg['content']['ip']
        proxyType = json_msg['content']['type']
        
        message_ok = json_msg
        
        try:
            self.vm.proxy_del(vm_name=name,ip=ip,port=port,proxy_type=proxyType)
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['network_dropportproxy_error_code']
            message_error['content']['errorMessage'] = 'drop port proxy error: ' + str(e) 
            message_error['action'] = self.messages['network_dropportproxy_error']
            self.send_msg(self.messages['network_dropportproxy_error_router'],message_error)
            return
        
        
        message_ok['action'] = self.messages['network_dropportproxy_ok']
        self.send_msg(self.messages['network_dropportproxy_ok_router'],message_ok)
    
    # 查询代理
    def find_proxy(self,json_msg):
        ""
        
        name = None
        port = None
        ip = None
        # 名字
        if 'vmName' in json_msg['content']:
            name = json_msg['content']['vmName']
        # 端口
        if 'port' in json_msg['content']:
            port = json_msg['content']['port']
        # ip
        if 'ip' in json_msg['content']:
            ip = json_msg['content']['ip']

        message_ok = json_msg
        
        try:
            lis = self.vm.proxy_list(vm_name=name,ip=ip,port=port)
            message_ok['content']['list'] = lis
        except Exception , e:
            message_error = json_msg
            message_error['content']['errorCode'] = self.messages['network_findportproxy_error_code']
            message_error['content']['errorMessage'] = 'find port proxy error: ' + str(e) 
            message_error['action'] = self.messages['network_findportproxy_error']
            self.send_msg(self.messages['network_findportproxy_error_router'],message_error)
            return
        
        
        message_ok['action'] = self.messages['network_findportproxy_ok']
        self.send_msg(self.messages['network_findportproxy_ok_router'],message_ok)
        
    
    # 发送mq消息 
    def send_msg(self,routing_key,message):
        ""
        
        self.logger.info(str(message))
         
        js = JsonParser()
        message = js.encode(message)
        
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.task_exchange,mq_type=self.task_type)
        mq.mq_send(msg=message,exchange_name=self.task_exchange,routing_key=routing_key)
        mq.mq_close()