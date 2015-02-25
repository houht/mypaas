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
from koala_task.utils import MysqlTools


from koala_task.services import ConfigManage
from koala_task.services import TaskinfoModule
from businessAction import BusinessAction

class TaskBss(threading.Thread) :
    ""
    
    def __init__(self) :
        ""
        threading.Thread.__init__(self)
        
        self.logger = LoggerUtil().getLogger()
        self.conf = ConfigManage()
        self.bs = BusinessAction()
    
    # �յ���������
    def process_action(self, taskinfo):
        ""        
        #ҵ����
        try :
            self.bs.processTask(taskinfo)
        except Exception,e:
            print e
            log = str(e)
            self.logger.error(log)
        
    
    #ѭ����ȡ���ݰ�
    def process(self):
       try :
            db_conf = self.conf.get_db_conf()
            db = MysqlTools(db_conf)
            taskInfoModule = TaskinfoModule(db)
            # 1 ����
            try :
                taskList = taskInfoModule.getAll()
                for taskinfo in taskList:
                    self.process_action(taskinfo)
                time.sleep(30)
            except Exception,e:
                log = str(e)
                self.logger.error(log)
                time.sleep(30)
            if db :
                db.close()
       except Exception,e:
            log = str(e)
            self.logger.error(log)
            time.sleep(180)
    
    def run(self):        
        while True:            
            self.process()
        
            
if __name__ == "__main__" :
    aa = TaskBss()
    aa.process()