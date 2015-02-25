#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201410
#desc: thread util

import Queue, threading, sys
from threading import Thread
import time,urllib
# working thread

class Worker(Thread):
    worker_count = 0
    def __init__( self, workQueue, resultQueue, timeout = None, daemon = False, **kwds):
        Thread.__init__( self, **kwds )
        self.id = Worker.worker_count
        Worker.worker_count += 1
        self.setDaemon( daemon )
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.timeout = timeout
        self.start()
    
    def run( self ):
        ''' the get-some-work, do-some-work main loop of worker threads '''
        while True:
            try:
                callable, excallable, rescallable, args, kwds = self.workQueue.get(timeout=self.timeout)
                res = callable(*args, **kwds)
                if rescallable != None:
                    rescallable(args, res)
                if self.resultQueue != None:
                    self.resultQueue.put((args, res))
            except Queue.Empty:
                break
            except Exception,e:
                print str(e)
                if excallable != None:
                    excallable(e, *args, **kwds)

#工作线程池 
class WorkerPool:
    def __init__( self, num_of_workers = 10, workMaxsize = 0, resultMaxsize = 0, timeout = None, daemon = False):
        ''' 
        num_of_workers表示线程数
        workMaxsize表示队列大小，0表示不限制大下
        resultMaxsize表示执行结果队列0表示不返回结果,需要写一个线程，调用get_result取出执行结果
        timeout表示线程从任务队列中去任务的超时长度
        daemon 表示是否后台执行，True表示后台，Flase表示前台执行
        '''
        self.workQueue = Queue.Queue(workMaxsize)
        if resultMaxsize > 0 :
            self.resultQueue = Queue.Queue(resultMaxsize)
        else :
            self.resultQueue = None
        self.workers = []
        self.timeout = timeout
        self.daemon = daemon
        self._recruitThreads( num_of_workers )
        
    def _recruitThreads( self, num_of_workers ):
        for i in range( num_of_workers ):
            worker = Worker( self.workQueue, self.resultQueue, self.timeout, self.daemon)
            self.workers.append(worker)
    
    def wait_for_complete( self):
        # ...then, wait for each of them to terminate:
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append( worker )
        #print "All jobs are are completed."
    
    def add_job( self, callable, excallable, rescallable, timeout, *args, **kwds ):
        ''' 
        callable 表示任务执行的回调函数,参数为(*args, **kwds)
        excallable 表示出异常是的回调函数，参数为(e,*args, **kwds)
        rescallable 表示执行结果的回调函数，参数为*args和callable的结果,即rescallable(args, callable(*args, **kwds))
        timeout 表示是否阻塞，None表示阻塞,否则为不阻塞等待时间，超时将抛出异常
        *args 表示参数，主要用来表示任务的唯一标识
        **kwds 表示key value参数
        '''
        self.workQueue.put( (callable, excallable, rescallable, args, kwds), timeout=timeout)
    
    def get_result( self, *args, **kwds ):
        if self.resultQueue == None:
            return None
        return self.resultQueue.get( *args, **kwds )
        
class Test:
    def __init__(self,num):
        self.num = num
    
    def test_job(self, id, sleep = 0.001 ):
        #try:        
        print "this is run.%s\n" % id
        raise Exception('----*******dddddd')
        #except: 
        #    print '[%4d]' % id, sys.exc_info()[:2]
    
        return id
    
    def test_excpetion(self, e, id, sleep = 0.001):
        print 'num=%d,call %s,ex=%s\n'%(self.num, id,str(e))
    
    def test_result(self, id, res):
        print "ddd",res
        
def test():
    import socket
    socket.setdefaulttimeout(10)
    print 'start testing' 
    wm = WorkerPool(5)
    #读消息
    #解析router key
    #根据 router key new 处理对象
    #调用wm.add_job
    for i in range(10):
        abc = Test(i+1)
        wm.add_job( abc.test_job, abc.test_excpetion, abc.test_result, None, "abc", i*0.001 ) 
    #wm.wait_for_complete()
    #id,res = wm.get_result();
    print 'end testing'
    
if __name__ == "__main__":
    test()