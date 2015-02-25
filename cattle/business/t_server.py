#!/usr/bin/python
# -*- coding: UTF-8 -*-


from cattle.utils import RabbitMq



# ����
# �յ���������
def process_action(message):
    ""
    
    # 1 ������Ϣ
    routing_key =  message.delivery_info['routing_key']
    exchange = message.delivery_info['exchange']
    msg =  message.body
    print msg,routing_key
    



aa = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
aa.queue_declare(queue_name='task_rst')
aa.exchange_declare(exchange_name='task_exc',mq_type='topic')
aa.queue_bind(queue_name='task_rst',exchange_name='task_exc',routing_key='task_rst.#')
aa.mq_receive(queue_name='task_rst',callback=process_action)

