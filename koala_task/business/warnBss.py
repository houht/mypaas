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
from warnAction import WarnAction

class WarnBss(threading.Thread) :
    ""
    
    def __init__(self) :
        ""
        threading.Thread.__init__(self)
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.warn_frequency = self.conf.get_monitor_conf()['warn_frequency']
        
        self.warnAction = WarnAction()
    
    def process(self):
        self.warnAction.processVmRunStat()
        
    def run(self):
        while True :
            try :
                time.sleep(self.warn_frequency)
                self.logger.debug("warn bss start is runing")
                self.process()
            except Exception,e:
                print e
                log = str(e)
                self.logger.error(log)
                
                
if __name__ == "__main__" :
    aa = WarnBss()
    aa.start()
    aa.join()