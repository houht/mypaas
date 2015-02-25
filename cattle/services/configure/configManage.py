#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from cattle.utils import ParserConf

CONFIG = "/etc/cattle.conf"

class ConfigManage:
    "Configuration management"

    def __init__(self):
        self.conf = ParserConf(CONFIG)
        
        # 1 全局
        self.cattle_section = "CATTLE"
        self.cattle_conf = {
            "heartbeat" : "60",
            "engineId"  : "",
            "scriptPath": "/etc/cattle/script/"
        }
        
        # 2 虚拟化
        self.virtual_section = "VIRTUALIZATION"
        self.virtual_conf = {
            "vcpus"         : "",
            "path"          : "",
            "type"          : "kvm",
            "maxVcpus"      : "",
            "maxMemary"     : "",
            "maxDisk"       : "",
            "heartbeat"     : "60",
            "rate"          : "30",
            "db_path"       : "/etc/vm.db",
            "vnc_port_range":"5900-6999"
        }
        
        # 3 网络
        self.network_section = "NETWORK"
        self.network_conf = {
            "db_path"       : "/etc/network.db",
            "bridge"        : "br0",
            "default_bridge"  : "br0",
            "agent_ip": "",
            "agent_port_range" : "8000-9000",
            "business_port_range" : "12000-13000",
            "net_type" : "",
            "dhcp_conf" : "/etc/dhcp/dhcpd.conf",
            "dhcp_service" : "dhcpd"
        }
        
        # 4 存储
        self.storage_section = "STORAGE"
        self.storage_conf = {
            "path"       : "",
            "vg_name"    : "",
            "cmd_format" : "mkfs.ext4",
            "cmd_mount"  : "mount",
            "db_path"    : "/etc/storage.db",
            "cmd_umount": "umount" 
        }
        
        # 5 镜像
        self.image_section = "IMAGE"
        self.image_conf = {
            "path"         : "",
            "download_addr": "",
            "db_path"      : "/etc/images.db"
        }
        
        # 5 应用
        self.app_section = "APPLICATION"
        self.app_conf = {
            "db_path"      : "/etc/app.db",
            "ip_addr"      : "",
            "heartbeat"    : "60",
            "rate"         : "30",
            "collect"      : "10"
            
        }
        
        
        # 6 消息
        self.mq_section = "MQ"
        self.mq_conf = {
            "mq_addr"           : "",
            "brodcast_exchange" : "bdct_exc",
            "brodcast_type"     : "fanout",
            "task_exchange"     : "task_exc",
            "task_type"         : "topic",
            "monitor_exchange"  : "mon_exc",
            "monitor_type"      : "topic"
        }
    
    
    def get_value(self,section,key,defult_value=""):
        "get a item value."
        
        value = self.conf.get_item(section,key)
        if value is None:
            return defult_value
        return value
    
    
    def get_cattle_conf(self):
        "Get cattle configuration information."
        
        return self.get_info(self.cattle_section,self.cattle_conf)
        
    def get_virtual_conf(self):
        "Get virtual configuration information."
        
        return self.get_info(self.virtual_section,self.virtual_conf)
    
    #获取网络配置
    def get_network_conf(self):
        "Get network configuration information."
        network = self.get_info(self.network_section,self.network_conf)
        bridge_list = {}
        bridges = network['bridge']
        lines = bridges.split()
        for bridge in lines:
            section = "bridge:"+bridge
            properties = self.conf.get_items(section)
            #deal properties
            item_arr = {}
            for v in properties :
                item_arr[v[0]] = v[1]
            bridge_list[bridge] = item_arr         
        network['bridge'] = bridge_list
        return network

    def get_storage_conf(self):
        "Get storage configuration information."
        
        return self.get_info(self.storage_section,self.storage_conf)
        
    def get_image_conf(self):
        "Get image configuration information."
        
        return self.get_info(self.image_section,self.image_conf)
        
    def get_app_conf(self):
        "Get application configuration information."
        
        return self.get_info(self.app_section,self.app_conf)
        
    def get_mq_conf(self):
        "Get mq configuration information."
        
        return self.get_info(self.mq_section,self.mq_conf)
     
    
    def get_info(self,section,conf):
        "Get configuration information."

        item_arr = {}
        value = self.conf.get_items(section)
        
        if value is None:
            item_arr = conf
        else:
            for key in conf:
                item_arr[key] = self.get_value(section,key,conf[key])
        return item_arr
        
