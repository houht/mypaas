#!/usr/bin/python
# -*- coding: UTF-8 -*-


from cattle.utils import RabbitMq



# 接收
# 收到请求处理函数
def process_action(message):
    ""
    
    # 1 返回信息
    routing_key =  message.delivery_info['routing_key']
    exchange = message.delivery_info['exchange']
    msg =  message.body
    print msg,routing_key
    



aa = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
aa.queue_declare(queue_name='mon_rst')
aa.exchange_declare(exchange_name='mon_exc',mq_type='topic')
aa.queue_bind(queue_name='mon_rst',exchange_name='mon_exc',routing_key='mon_rst.#')
aa.mq_receive(queue_name='mon_rst',callback=process_action)

