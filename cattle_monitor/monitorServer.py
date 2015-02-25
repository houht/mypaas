#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201412
#desc: 
#*************************************

import os
import sys
import time
import thread


from cattle.utils import Daemon
from cattle.utils import LoggerUtil
from monitorVm import MonitorVm

from cattle.services import ConfigManage

class MonitorServer(Daemon) :
    ""
    
    
    #ϵͳ��ʼ��
    def __init__(self, config) :
        
        # ��ȡ���Ƶ��
        conf = ConfigManage()
        app_conf = conf.get_app_conf()
        self.rate = app_conf['rate']
        
        self.logger = LoggerUtil().getLogger()
        
        self.config = config
        self.running = False
        
        pidfile = self.config['pidfile']
        stderr = self.config['stderr']
        stdout = self.config['stdout']
        stdin = self.config['stdin']
        Daemon.__init__(self, pidfile, stderr, stdout, stdin)
        
   
    #��������
    def _run(self) : 
        
        mointor = MonitorVm()
        
        # ���
        thread.start_new_thread(mointor.monitor, ())  
        
        # ��ʱ����
        while True :       
            try :
                mointor.send_msg()  
            except Exception,ex :
                self.logger.error('task process error,msg:%s' % str(ex))
            
            time.sleep(int(self.rate))
            

if __name__ == "__main__" :
    
    config = {}
    config['pidfile'] = '/var/run/cattle/monitor.pid'
    config['stderr'] = '/var/log/cattle/monitor.log'
    config['stdout'] = '/var/log/cattle/monitor.log'
    config['stdin'] = '/dev/null'
    daemon = MonitorServer(config)
    daemon.start()
    
