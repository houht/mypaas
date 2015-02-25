#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from kombu.connection import Connection
from kombu.entity import Exchange
#����
from kombu.messaging import Producer
#����
from kombu.entity import Queue
from kombu.messaging import Consumer

import amqp




class RabbitMq:
    "manage rabbitmq."
    
    
    def __init__(self,mq_server):
        ""

        self.connection = Connection(mq_server)
        self.chan = self.connection.channel()
    
    # �ر�
    def mq_close(self):
        ""
        
        self.connection.close()
        self.chan.close()
    
    # ����queue
    def queue_declare(self,**kwargs):
        ""
        
        queue_name = kwargs.pop('queue_name', None)
        durable_flag = kwargs.pop('durable_flag', True)
        exclusive_flag = kwargs.pop('exclusive_flag', False)
        auto_delete_flag   = kwargs.pop('auto_delete_flag', False)
        
        self.chan.queue_declare(queue=queue_name, durable=durable_flag, exclusive=exclusive_flag, auto_delete=auto_delete_flag)
        
        
    # ����exchange
    def exchange_declare(self,**kwargs):
        ""
  
        exchange_name = kwargs.pop('exchange_name', None)
        mq_type = kwargs.pop('mq_type', None)
        durable_flag = kwargs.pop('durable_flag', True)
        auto_delete_flag   = kwargs.pop('auto_delete_flag', False) 
       
        self.chan.exchange_declare(exchange=exchange_name, type=mq_type, durable=durable_flag, auto_delete=auto_delete_flag)
    
    
    # ��queue �� exchange
    def queue_bind(self,**kwargs):
        ""
        
        queue_name = kwargs.pop('queue_name', None)
        exchange_name = kwargs.pop('exchange_name', None)
        routing_key = kwargs.pop('routing_key', None)
        
        self.chan.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)

    
    # ������Ϣ
    def mq_send(self,**kwargs):
        ""
        
        msg = kwargs.pop('msg', None)
        exchange_name = kwargs.pop('exchange_name', None)
        routing_key = kwargs.pop('routing_key', None)
        
        message = amqp.Message(str(msg))
        self.chan.basic_publish(message,exchange=exchange_name,routing_key=routing_key)
        
    
    
    #������Ϣ
    def mq_receive(self,**kwargs):
        ""
        
        queue_name = kwargs.pop('queue_name', None)
        callback = kwargs.pop('callback', None)
        
        self.chan.basic_consume(callback=callback,queue=queue_name,no_ack=True)
        while True:
            self.chan.wait()

        
if __name__ == "__main__":
    print "start"
    
    # ����һ ���� fanout
#    aa = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.137:5672/paas_vhost')
#    aa.exchange_declare(exchange_name='abc12345',mq_type='fanout')
#    aa.mq_send(msg="fanout 12345678",exchange_name='abc12345',routing_key="key.123.456")
#    aa.mq_close()
    
    # ���Զ� ���� topic
#    bb = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.137:5672/paas_vhost')
#    bb.exchange_declare(exchange_name='abc1',mq_type='topic')
#    bb.mq_send(msg="topic aaaa",exchange_name='abc1',routing_key="aaaaaaaa.kj.qq.abc.77.ee abc")
#    bb.mq_close()
#    
    
    # ������ ����
    
    cc = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.137:5672/paas_vhost')
    # ����
    cc.queue_declare(queue_name="video2")
    
    
    # exchange 1
#    cc.exchange_declare(exchange_name='abc12345',mq_type='fanout')
#    cc.queue_bind(queue_name="video2",exchange_name='abc12345',routing_key="")
    
    # exchange 2
    cc.exchange_declare(exchange_name='abc1',mq_type='topic')
    cc.queue_bind(queue_name="video2",exchange_name='abc1',routing_key="aaaaaaaa.#")
    
    # �յ���������
    def process_media(message):
    
        print message.delivery_info['routing_key']
        print message.body
    
    cc.mq_receive(queue_name="video2",callback=process_media)
    
    print "end"
    
    