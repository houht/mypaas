#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from cattle.utils import JsonParser
from cattle.utils import RabbitMq
from cattle.utils import WorkerPool
from cattle.utils import JsonParser
from cattle.utils import LoggerUtil


from cattle.services import ConfigManage
from cattle.business import BusinessAction


class TaskBss() :
    ""
    
    def __init__(self) :
        ""
        
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        # 线程池
        self.work = WorkerPool()
    

        
    
    # 收到请求处理函数
    def process_action(self,message):
        ""

        try:
            
            # 1 返回信息
            routing_key =  message.delivery_info['routing_key']
            exchange = message.delivery_info['exchange']
            msg =  message.body
            
            
            action = routing_key.split('.',1)[1]
            
            self.logger.info('action: %s ;message: %s'%(action,str(msg)))
            
            
            js = JsonParser()
            json_msg =js.decode(msg)
            
            # 2 json格式报错,日志记录
            if json_msg == -1:
                self.logger.error('josn format error!')
                return
            
            bs = BusinessAction(action,json_msg)
            self.work.add_job( bs.job,None,None, None, )
        
        except Exception,e:
            log = str(e)
            self.logger.error('process_action : ' + log)
    
    #循环读取数据包
    def process(self):
        ""
        
        mq_conf = self.conf.get_mq_conf()
        mq_addr = mq_conf['mq_addr']
        
        # 1 创建MQ对象
        rmq = RabbitMq(mq_addr)
    
        # 2 获取队列名字
        cattle_conf = self.conf.get_cattle_conf()
        mq_queue = cattle_conf['engineId']
        self.mq_queue = mq_queue
        # 3 创建队列
        rmq.queue_declare(queue_name=mq_queue)
        
        # 4 创建广播 exchange
        brodcast_exchange = mq_conf['brodcast_exchange']
        brodcast_type = mq_conf['brodcast_type']
        rmq.exchange_declare(exchange_name=brodcast_exchange,mq_type=brodcast_type)
        rmq.queue_bind(queue_name=mq_queue,exchange_name=brodcast_exchange,routing_key="")
    
        
        # 5 创建任务 exchange
        routing_key = mq_queue + ".#"
        task_exchange = mq_conf['task_exchange']
        task_type = mq_conf['task_type']
        rmq.exchange_declare(exchange_name=task_exchange,mq_type=task_type)
        rmq.queue_bind(queue_name=mq_queue,exchange_name=task_exchange,routing_key=routing_key)
        
        
        # 6 启动
        try :
            rmq.mq_receive(queue_name=self.mq_queue,callback=self.process_action)
        except Exception,e:
            log = str(e)
            self.logger.error(log)
        
if __name__ == "__main__" :
    aa = TaskBss()
    aa.process()