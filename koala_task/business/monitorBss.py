#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import time
import threading

from koala_task.utils import JsonParser
from koala_task.utils import RabbitMq
from koala_task.utils import JsonParser
from koala_task.utils import LoggerUtil


from koala_task.services import ConfigManage
from monitorAction import MonitorAction
class MonitorBss(threading.Thread) :
    ""
    
    def __init__(self) :
        ""
        threading.Thread.__init__(self)
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.monitorAction = MonitorAction()
    # 收到请求处理函数
    def process_action(self,message):
        ""
        self.logger.debug("received monitor mq message")
        # 1 返回信息
        routing_key =  message.delivery_info['routing_key']
        exchange = message.delivery_info['exchange']
        msg =  message.body
        action = routing_key.split('.',1)[1]
        #self.logger.info('action: %s ;message: %s'%(action,str(msg)))       
        
        js = JsonParser()
        json_msg =js.decode(msg)
        
        # 2 json格式报错,日志记录
        if json_msg == -1:
            self.logger.error('josn format error!')
            return
        
        # 3业务处理
        try :
            self.monitorAction.processMq(action,json_msg)
        except Exception,e:
            log = str(e)
            self.logger.error(log)
        
    
    #循环读取数据包
    def process(self):
        ""
        
        mq_conf = self.conf.get_mq_conf()
        mq_addr = mq_conf['mq_addr']
        
        # 1 创建MQ对象
        rmq = RabbitMq(mq_addr)
    
        # 2 获取队列名字
        mq_queue = mq_conf['monitor_queue_name']
        self.mq_queue = mq_queue
        # 3 创建队列
        rmq.queue_declare(queue_name=mq_queue)
        
        # 4 创建任务 exchange
        routing_key = mq_queue + ".#"
        monitor_exchange = mq_conf['monitor_exchange']
        monitor_type = mq_conf['monitor_type']
        rmq.exchange_declare(exchange_name=monitor_exchange,mq_type=monitor_type)
        rmq.queue_bind(queue_name=mq_queue,exchange_name=monitor_exchange,routing_key=routing_key)

        # 5 启动
        try :
            rmq.mq_receive(queue_name=self.mq_queue,callback=self.process_action)
        except Exception,e:
            log = str(e)
            self.logger.error(log)
    
    def run(self):        
        while True :
            try :
                self.logger.debug("start is runing")
                self.process()
                time.sleep(180)
            except Exception,e:
                log = str(e)
                self.logger.error(log)
                            
if __name__ == "__main__" :
    aa = MonitorBss()
    aa.start()
    aa.join()