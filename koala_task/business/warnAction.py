#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import time

from koala_task.utils import JsonParser
from koala_task.utils import ParserConf
from koala_task.utils import LoggerUtil
from koala_task.utils import UUIDUtils
from koala_task.utils import MysqlTools

from koala_task.services import ConfigManage
from koala_task.services import InstanceInfoModule,VminfoModule,ResourceStat
from koala_task.services import VmUseStat,VmWarnStat

class WarnAction:
    ""
    tableTime = None
    appInstance = {}
    vmInstance = {}
    
    resourceLoadTime = None
    
    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
        self.vmUseStat = VmUseStat()
        self.vmWarnStat = VmWarnStat()
        self.resourceStat = ResourceStat()
        self.conf = ConfigManage()
        self.warn_resource_keep_max_time = self.conf.get_monitor_conf()['warn_resource_keep_max_time']
    
    def __getDb(self) :
        db_conf = self.conf.get_db_conf()
        db = MysqlTools(db_conf)
        return db  
            
    def processVmRunStat(self) :
        """
        @summary: 虚拟机和应用资源使用监控信息入库
        """
        _time = time.time()
        nowTime = time.localtime(_time)
        now = time.strftime('%Y-%m-%d %H:%M:%S',nowTime)
        cur_tableTime = time.strftime('%Y%m',nowTime)
        #获取数据操作对象
        db = self.__getDb()
        self.logger.debug("this is running 1......")
        #重新载入
        if WarnAction.resourceLoadTime is None or _time - WarnAction.resourceLoadTime > self.warn_resource_keep_max_time :
            self.logger.debug("this is running 2......")
            self.resourceStat.reloadVmInfo(db)
            self.logger.debug("this is running 3......")
            self.resourceStat.reloadAppInstanceInfo(db)
            self.logger.debug("this is running 4......")
            WarnAction.resourceLoadTime = _time
            
            
        vmRunInfos = self.vmUseStat.getAllVmRunInfo()
        
        rule = '''{
                   "highWarn":{"cpu":90,"mem":90,"flow":8388608,"duration":3},
                   "lowWarn":{"cpu":10,"mem":40,"flow":8000,"duration":240},
                   "overtime":300
                }'''
        jp = JsonParser()
        rule = jp.decode(rule)
        self.logger.debug("warn info:"+str(self.vmWarnStat.getAllVmWarnInfo()))
        #appInstanceKeys = WarnAction.appInstance.keys()
        #vmInstanceKeys = WarnAction.vmInstance.keys()
        instanceIds = []
        vmNames = []
        
        load_effective_time = 1800
        for info in vmRunInfos :
            keys = info.keys()
            self.logger.debug("this is running 5......")
            vmName = info['vmName']
            status = info['vmState']
            self.logger.debug("this is running 6......")
            flag = 'normal'
            cpuRate = float(0)
            memRate = float(0)
            flow = long(0)
            
            instanceId = ''
            
            eventTime = info['eventTime']
            receiveTime = info['receiveTime']
            
            if 'cpuRate' in keys:
                cpuRate = float(info['cpuRate'])
            if 'memRate' in keys:
                memRate = float(info['memRate'])
            if 'flow' in keys:
                flow = long(info['flow'])
            
            vmInfo = None
            instanceInfo = None

            if 'instanceId' in keys and info['instanceId'] :
                instanceInfo = self.resourceStat.getInstanceInfo(info['instanceId'])
            else:
                vmInfo = self.resourceStat.getVmInfo(vmName)
                
            if vmInfo is None and instanceInfo is None:
                continue
                        
            #规则信息
            ruleKeys = rule.keys()
            hightFlag = False
            lowFlag = False
            hightDuration = 0
            lowDuration = 0
            
            if 'overtime' in ruleKeys:
                maxDuration = float(rule['overtime'])                
                overtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(_time - maxDuration))
                #过期事件不处理
                if receiveTime < overtime :
                    continue
                    
            if 'lowWarn' in ruleKeys:
                lowWarn = rule['lowWarn']
                lowWarnKeys = lowWarn.keys()
                
                lowFlag = True
                if 'cpu' in lowWarnKeys:
                    if cpuRate >= float(lowWarn['cpu']):
                        lowFlag = False
                if 'mem' in lowWarnKeys:
                    if memRate >= float(lowWarn['mem']):
                        lowFlag = False
                if 'flow' in lowWarnKeys:
                    if flow >= long(lowWarn['flow']):
                        lowFlag = False
                if 'duration' in lowWarnKeys:
                    lowDuration = int(lowWarn['duration'])

            if 'highWarn' in ruleKeys:
                highWarn = rule['highWarn']
                highWarnKeys = highWarn.keys()
                hightFlag = True
                if 'cpu' in highWarnKeys:
                    if cpuRate < float(highWarn['cpu']):
                        hightFlag = False
                if 'mem' in highWarnKeys:
                    if memRate < float(highWarn['mem']):
                        hightFlag = False
                if 'flow' in highWarnKeys:
                    if flow < long(highWarn['flow']):
                        hightFlag = False
                if 'duration' in highWarnKeys:
                    hightDuration = int(highWarn['duration'])
                
            #根据运行状态，判断是否告警
            maxDuration = 0
            if "running" == status:
                if hightFlag:
                    flag = 'highWarn'
                    maxDuration = hightDuration
                if lowFlag:
                    flag = 'lowWarn'
                    maxDuration = lowDuration              
                
            elif "paused" == status:
                flag = 'paused'
                if instanceInfo is not None and instanceInfo['status'] != 'running':
                     flag = 'normal'
                elif vmInfo is not None and vmInfo['status'] != 'running':
                     flag = 'normal'
            elif "shutdown" == status:
                flag = 'shutdown'
                if instanceInfo is not None and instanceInfo['status'] != 'running':
                     flag = 'normal'
                elif vmInfo is not None and vmInfo['status'] != 'running':
                     flag = 'normal'
            elif "crashed" == status:
                flag = 'crashed'
            
            #处理过的应用实例和虚拟机
            if instanceInfo:
                instanceIds.append(instanceInfo['instanceId'])
            elif vmInfo:
                vmNames.append(vmInfo['vmName'])
                
                
            #告警处理
            if flag == 'normal':
                self.vmWarnStat.removeVmRunInfo('vmName')
                if instanceInfo:
                    #主要考虑warnType=overtime的应用，vmName设置的值为instanceId
                    self.vmWarnStat.removeVmRunInfo(instanceInfo['instanceId'])
            else :
                self.vmWarnStat.addVmRunInfo(info, flag, maxDuration) 
        self.logger.debug("this is running 7......")                         
        #没有监控信息的虚拟机告警
        vmInfoList = self.resourceStat.getAllVmInfoList()
        for info in vmInfoList:
            if info['vmName'] not in vmNames:
                ruleKeys = rule.keys()
                tmp = {}
                tmp['vmName'] = info['vmName']
                tmp['vmState'] = 'shutdown'
                tmp['eventTime'] = now
                tmp['receiveTime'] = now
                flag = 'overtime'
                maxDuration = -1
                if 'overtime' in ruleKeys:
                    maxDuration = float(rule['overtime'])
                
                self.vmWarnStat.addVmRunInfo(tmp, flag, maxDuration)
        self.logger.debug("this is running 8......")
        
        #没有监控信息的应用实例告警
        appInstanceInfoList = self.resourceStat.getAllAppInstanceInfoList()
        for info in appInstanceInfoList:
            if info['instanceId'] not in instanceIds:
                ruleKeys = rule.keys()
                tmp = {}
                tmp['instanceId'] = info['instanceId']
                tmp['vmName'] = info['instanceId']
                tmp['vmState'] = 'shutdown'
                tmp['eventTime'] = now
                tmp['receiveTime'] = now
                flag = 'overtime'
                maxDuration = -1
                if 'overtime' in ruleKeys:
                    maxDuration = float(rule['overtime'])
                self.vmWarnStat.addVmRunInfo(tmp, flag, maxDuration)
        self.logger.debug("this is running 9......")
                
if __name__ == "__main__" :   
    rule = '''{
                   "highWarn":{"cpu":90,"mem":90,"flow":8388608,"duration":3},
                   "lowWarn":{"cpu":10,"mem":40,"flow":8000,"duration":240}
                }'''
    jp = JsonParser()
    rule = jp.decode(rule)
    print rule['highWarn']['cpu'] 
        