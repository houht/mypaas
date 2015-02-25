import os
import sys
import time

from cattle.utils import Daemon
from cattle.utils import LoggerUtil
from cattle.business import TaskBss


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
        while True :       
            try :
                task = TaskBss()
                task.process()
            except Exception,ex :
                self.logger.error('task process error,msg:%s' % str(ex))
            time.sleep(30)
        

    
if __name__ == "__main__" :
    
    config = {}
    config['pidfile'] = '/var/run/cattle/cattle.pid'
    config['stderr'] = '/var/log/cattle/error.log'
    config['stdout'] = '/var/log/cattle/out.log'
    config['stdin'] = '/dev/null'
    daemon = Server(config)
    if len(sys.argv) == 2 :
        if 'start' == sys.argv[1] :
            print 'start cattle'
            daemon.start()
        elif 'stop' == sys.argv[1] :
            print 'stop cattle'
            daemon.stop()
        elif 'restart' == sys.argv[1] :
            print 'restart cattle'
            daemon.restart()
        else :
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else :
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
    
     
