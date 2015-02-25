#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
from koala_task.utils import JsonParser
from koala_task.utils import ParserConf
from koala_task.utils import LoggerUtil
from koala_task.utils import UUIDUtils

from koala_task.services import VmUseStat

class MonitorAction:
    ""

    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
        self.vmUseStat = VmUseStat()
    
        
    def processMq(self, action, json_msg) :
        """
        @summary: mq��Ϣ����
        @param��action ��Ϣ����
        @param: json_msg ��Ϣ����
        """
        if action=='vm.monitor.stat' :
            self.__processVmMonitorStat(json_msg)
        
        else :
            print 'error'  
        pass
    
    
    def __processVmMonitorStat(self, json_msg) :
        """
        @summary: vm��Ӧ�õ���Դʹ�������
        @param: json_msg ��Ϣ����
        """
        for vmRunInfo in json_msg :
            try:
                self.vmUseStat.addVmRunInfo(vmRunInfo)                
            except:
                pass
    