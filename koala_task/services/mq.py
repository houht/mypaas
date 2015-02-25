#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201412
#desc: 
#*************************************

from koala_task.utils import RabbitMq
from koala_task.utils import LoggerUtil

from koala_task.services import ConfigManage

class Mq():
    def __init__(self):
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.mq_conf = self.conf.get_mq_conf()
        
        self.mq_addr = self.mq_conf['mq_addr']
        self.brodcast_exchange = self.mq_conf['brodcast_exchange']
        self.brodcast_type = self.mq_conf['brodcast_type']
        self.task_exchange = self.mq_conf['task_exchange']
        self.task_type = self.mq_conf['task_type']
        self.queue_name = self.mq_conf['queue_name']
        
        
    def send_task_message(self, routing_key, message) :
        """
        @summary: mq发送task消息
        @param：router_key 路由key
        @param: message 消息内容
        """
        self.logger.debug("send task:routing_key:%s,message:%s"%(routing_key, message))
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.task_exchange, mq_type=self.task_type)
        mq.mq_send(msg=message, exchange_name=self.task_exchange, routing_key=routing_key)
        mq.mq_close()
        
    def send_bdct_message(self, routing_key, message) :
        """
        @summary: mq发送广播消息
        @param：router_key 路由key
        @param: message 消息内容
        """
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.brodcast_exchange, mq_type=self.brodcast_type)
        mq.mq_send(msg=message ,exchange_name=self.brodcast_exchange, routing_key=routing_key)
        mq.mq_close()
    
    