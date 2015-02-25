#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from koala_task.utils import ParserConf

CONFIG = "/etc/koala/koala.conf"

class ConfigManage:
    "Configuration management"

    def __init__(self):
        self.conf = ParserConf(CONFIG)
        
        # 1 全局
        self.koala_section = "KOALA"
        self.koala_conf = {
            "heartbeat" : "60"
        }
                
        # 2 数据
        self.db_section = "DB"
        self.db_conf = {
            "host"           : "localhost",
            "port"           : 30060,
            "db"             : "",
            "user"           : "root",
            "passwd"         : None,
            "charset"        : None
        }
        
        # 3 云盘
        self.store_section = "STORE"
        self.store_conf = {
            "download_addr"  : None
        }
        
        # 4 应用
        self.app_section = "APPLICATION"
        self.app_conf = {
            "heartbeat"  : 180,
            "rate"       : 180
        }
        
        # 5 MQ
        self.mq_section = "MQ"
        self.mq_conf = {
            "mq_addr"                 : None,
            "brodcast_exchange"       : "bdct_exc",
            "brodcast_type"           : "fanout",
            "task_exchange"           : "task_exc",
            "task_type"               : "topic",
            "queue_name"              : "task_rst",
            "monitor_exchange"        : "mon_exc", 
            "monitor_type"            : "topic",
            "monitor_queue_name"      : "mon_rst"
        }
        
        # 6 LOG
        self.log_section = "LOG"
        self.log_conf = {
            "level"                   : None
        }
        
        # 7 monitor
        self.monitor_section = "MONITOR"
        self.monitor_conf = {
            "monitor_frequency"          : 120,
            "monitor_keep_max_time"      : 7200,
            "warn_frequency"             : 60,
            "warn_resource_keep_max_time" : 600,
            "warn2db_frequency"          : 130
        }
    def get_value(self,section,key,defult_value=""):
        "get a item value."
        
        value = self.conf.get_item(section,key)
        if value is None:
            return defult_value
        return value
    
    def get_koala_conf(self):
        "Get koala configuration information."
        
        return self.get_info(self.koala_section,self.koala_conf)
        
    def get_db_conf(self):
        "Get virtual configuration information."
        
        return self.get_info(self.db_section,self.db_conf)
    
    def get_store_conf(self):
        "Get store configuration information."
        
        return self.get_info(self.store_section,self.store_conf)
        
    def get_app_conf(self):
        "Get app configuration information."
        
        return self.get_info(self.app_section,self.app_conf)
        
    def get_mq_conf(self):
        "Get mq configuration information."
        
        return self.get_info(self.mq_section,self.mq_conf)
        
    def get_log_conf(self):
        "Get log configuration information."
        
        return self.get_info(self.log_section,self.log_conf)
    
    def get_monitor_conf(self):
        "Get monitor configuration information."
        
        return self.get_info(self.monitor_section,self.monitor_conf)
        
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
        
