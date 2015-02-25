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
from monitorDbAction import MonitorDbAction

class MonitorDbBss(threading.Thread) :
    ""
    
    def __init__(self) :
        ""
        threading.Thread.__init__(self)
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.monitor_frequency = self.conf.get_monitor_conf()['monitor_frequency']
        self.monitorDbAction = MonitorDbAction()
    
    def process(self):
        try :
            self.logger.debug("start is runing")
            self.monitorDbAction.processVmRunStat()
        except Exception,e:
            log = str(e)
            self.logger.error(log)            
            time.sleep(300)   
        
    def run(self):
        while True :
            time.sleep(self.monitor_frequency)
            self.process()
            
                            
if __name__ == "__main__" :
    aa = MonitorDbBss()
    aa.start()
    aa.join()