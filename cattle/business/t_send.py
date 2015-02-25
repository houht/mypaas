#!/usr/bin/python
# -*- coding: UTF-8 -*-


from cattle.utils import RabbitMq




mq = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
mq.exchange_declare(exchange_name='mon_exc',mq_type='topic')
mq.mq_send(msg='{}',exchange_name='mon_exc',routing_key='mon_rst.vm.monitor.stat')
mq.mq_close()



