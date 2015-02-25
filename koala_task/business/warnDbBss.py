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
from warnDbAction import WarnDbAction

class WarnDbBss(threading.Thread) :
    ""
    
    def __init__(self) :
        ""
        threading.Thread.__init__(self)
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.warn2db_frequency = self.conf.get_monitor_conf()['warn2db_frequency']
        
        self.warnDbAction = WarnDbAction()
    
    def process(self):
        self.warnDbAction.processVmRunStat()
        
    def run(self):
        while True :
            try :
                time.sleep(self.warn2db_frequency)
                self.logger.debug("warndb bss start is runing")
                self.process()
            except Exception,e:
                log = str(e)
                self.logger.error(log)
                
                
if __name__ == "__main__" :
    aa = WarnDbBss()
    aa.start()
    aa.join()