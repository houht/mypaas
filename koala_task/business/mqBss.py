#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from koala_task.utils import JsonParser
from koala_task.utils import RabbitMq
from koala_task.utils import JsonParser
from koala_task.utils import LoggerUtil


from koala_task.services import ConfigManage
from businessAction import BusinessAction

class MqBss() :
    ""
    
    def __init__(self) :
        ""
        
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.bs = BusinessAction()
    
    # �յ���������
    def process_action(self,message):
        ""
        self.logger.debug("received mq message")
        # 1 ������Ϣ
        routing_key =  message.delivery_info['routing_key']
        exchange = message.delivery_info['exchange']
        msg =  message.body
        action = routing_key.split('.',1)[1]
        self.logger.debug(action+":"+msg)
        self.logger.info('action: %s ;message: %s'%(action,str(msg)))
        
        
        js = JsonParser()
        json_msg =js.decode(msg)
        
        # 2 json��ʽ����,��־��¼
        if json_msg == -1:
            self.logger.error('josn format error!')
            return
        
        # 3ҵ����
        try :
            self.bs.processMq(action,json_msg)
        except Exception,e:
            log = str(e)
            self.logger.error(log)
        
    
    #ѭ����ȡ���ݰ�
    def process(self):
        ""
        
        mq_conf = self.conf.get_mq_conf()
        mq_addr = mq_conf['mq_addr']
        
        # 1 ����MQ����
        rmq = RabbitMq(mq_addr)
    
        # 2 ��ȡ��������
        mq_queue = mq_conf['queue_name']
        self.mq_queue = mq_queue
        # 3 ��������
        rmq.queue_declare(queue_name=mq_queue)
        
        # 4 �������� exchange
        routing_key = mq_queue + ".#"
        task_exchange = mq_conf['task_exchange']
        task_type = mq_conf['task_type']
        rmq.exchange_declare(exchange_name=task_exchange,mq_type=task_type)
        rmq.queue_bind(queue_name=mq_queue,exchange_name=task_exchange,routing_key=routing_key)

        # 5 ����
        try :
            rmq.mq_receive(queue_name=self.mq_queue,callback=self.process_action)
        except Exception,e:
            log = str(e)
            self.logger.error(log)
    
    def start(self):
        while True :
            try :
                self.logger.debug("start is runing")
                self.process()
                time.sleep(180)
            except Exception,e:
                log = str(e)
                self.logger.error(log)
                    
if __name__ == "__main__" :
    aa = MqBss()
    aa.process()
    aa.start()
    aa.join()