import os
import sys
import time


from koala_task.utils import Daemon
from koala_task.utils import LoggerUtil
from koala_task.business import TaskBss
from koala_task.business import MqBss
from koala_task.business import MonitorBss,MonitorDbBss,WarnBss,WarnDbBss

class Server(Daemon) :
    ""
    
    #系统初始化
    def __init__(self, config) :
        self.logger = LoggerUtil().getLogger()
        
        self.config = config
        self.running = False
        
        pidfile = self.config['pidfile']
        stderr = self.config['stderr']
        stdout = self.config['stdout']
        stdin = self.config['stdin']
        Daemon.__init__(self, pidfile, stderr, stdout, stdin)
        
    
    #启动任务
    def _run(self) : 
        task = TaskBss()
        mq   = MqBss()        
        mb = MonitorBss()
        mdb = MonitorDbBss()
        wb = WarnBss()
        wdb = WarnDbBss()
        
        task.start()
        mb.start()
        mdb.start()
        wb.start()
        wdb.start()
        
        self.logger.debug("_run is start")
        mq.start()
    
if __name__ == "__main__" :
    
    config = {}
    config['pidfile'] = '/var/run/koala/koala.pid'
    config['stderr'] = '/var/log/koala/error.log'
    config['stdout'] = '/var/log/koala/out.log'
    config['stdin'] = '/dev/null'
    daemon = Server(config)
    
    if len(sys.argv) == 2 :
        if 'start' == sys.argv[1] :
            print 'start daemon'
            daemon.start()
        elif 'stop' == sys.argv[1] :
            print 'stop daemon'
            daemon.stop()
        elif 'restart' == sys.argv[1] :
            print 'restart daemon'
            daemon.restart()
        else :
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else :
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
     
