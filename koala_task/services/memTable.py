#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201412
#desc: 
#*************************************
import time
import datetime

from koala_task.utils import LoggerUtil
from koala_task.services import InstanceInfoModule,VminfoModule

class VmUseStat() :
    infoList = []
    def __init__(self) :
        self.logger = LoggerUtil().getLogger()
        '''info =[{instanceId:"",vmName:"",vmState:"",cpuRate:"",memRate:"",flow:"",eventTime:"",receiveTime:""}] '''
        
        
    
    #增加监控的消息
    def addVmRunInfo(self, vmRunInfo) :
        tmp = {}
        tmp['vmName'] = vmRunInfo['vmName']
        tmp['vmState'] =  vmRunInfo['vmState']
        keys = vmRunInfo.keys()
        if 'instanceId' in keys:
            tmp['instanceId'] = vmRunInfo['instanceId']
        if 'cpuRate' in keys:
            tmp['cpuRate'] =  vmRunInfo['cpuRate']
        if 'memRate' in keys:
            tmp['memRate'] =  vmRunInfo['memRate']
        if 'netStats' in keys:
            if len(vmRunInfo['netStats'])>0:
                tmp['flow'] =  vmRunInfo['netStats'][0]['flow']
        tmp['eventTime'] =  vmRunInfo['eventTime']
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        tmp['receiveTime'] = now
        
        for i in range(0, len(VmUseStat.infoList)):
            if tmp['vmName'] == VmUseStat.infoList[i]['vmName']:
                del VmUseStat.infoList[i]
                break
        
        #增加       
        VmUseStat.infoList.append(tmp)
    
    #获取所有vm的运行信息    
    def cleanAllVmRunInfo(self, keepTime=None) :
        self.logger.debug("VmUseStat.infoList was clean")  
        if keepTime is None:
            keepTime = 2*60*60 #2小时
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time() - keepTime))      
        for info in VmUseStat.infoList:
            if info['receiveTime'] < now:
               del VmUseStat.infoList[0]
            else:
                break;            
        return VmUseStat.infoList
    
    def getAllVmRunInfo(self) :
        return VmUseStat.infoList
        
class VmWarnStat() :        
    info = {}
    def __init__(self) :
        self.logger = LoggerUtil().getLogger()
        '''info ={"vmName":{instanceId:"",vmName:"","warnType":"highWarn|lowWarn|paused|shutdown|crashed|overtime",vmState:"",cpuRate:"",memRate:"",flow:"",eventTime:"",receiveTime:"",duration:120,times:3,maxDuration:23}} '''
        
    def addVmRunInfo(self, vmWarnInfo, warnType, maxDuration) :
        """
        @summary: 增加告警信息
        @param vmWarnInfo 虚拟机告警信息
        """
        
        vmName = vmWarnInfo['vmName']
        eventTime = vmWarnInfo['eventTime']
        receiveTime = vmWarnInfo['receiveTime']
        vmState = vmWarnInfo['vmState']
        
        cpuRate = 0
        memRate = 0
        flow = 0
        instanceId = None
        
        vmWarnKeys  = vmWarnInfo.keys()
        if 'cpuRate' in vmWarnKeys:
            cpuRate = vmWarnInfo['cpuRate']
        if 'memRate' in vmWarnKeys:
            memRate = vmWarnInfo['memRate']
        if 'flow' in vmWarnKeys:
            flow = vmWarnInfo['flow']
        if 'instanceId' in vmWarnKeys:
            instanceId = vmWarnInfo['instanceId'] 
        
        duration = 0
        infoKeys = VmWarnStat.info.keys()
        if vmName in infoKeys:
            oldVmWarnInfo = VmWarnStat.info[vmName]
            oldWarnType = oldVmWarnInfo['warnType']
            oldEventTime = oldVmWarnInfo['eventTime']
            
            #判断是否为重复事件
            if eventTime == oldEventTime:
                return
            if oldWarnType == warnType:
                t = time.strptime(eventTime, '%Y-%m-%d %H:%M:%S')
                oldT = time.strptime(oldEventTime, '%Y-%m-%d %H:%M:%S')
                date1=datetime.datetime(oldT[0],oldT[1],oldT[2],oldT[3],oldT[4],oldT[5])
                date2=datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
                d = date2 - date1
                duration = d.seconds                 
                oldVmWarnInfo['times'] = oldVmWarnInfo['times']+1                
            else:
                oldVmWarnInfo['eventTime'] = eventTime                
                oldVmWarnInfo['times'] = 1
            
            oldVmWarnInfo['receiveTime'] = receiveTime
            oldVmWarnInfo['warnType'] = warnType
            oldVmWarnInfo['vmState'] = vmState
            
            oldVmWarnInfo['cpuRate'] = cpuRate
            oldVmWarnInfo['memRate'] = memRate
            oldVmWarnInfo['flow'] = flow
            oldVmWarnInfo['duration'] = duration
            oldVmWarnInfo['maxDuration'] = maxDuration
            oldVmWarnInfo['in2db'] = True
        else:
            #新增
            tmp = {}
            if instanceId is not None:
                tmp['instanceId'] = instanceId
            tmp['vmName'] = vmName
            tmp['receiveTime'] = receiveTime
            tmp['warnType'] = warnType
            tmp['eventTime'] = eventTime
            tmp['maxDuration'] = maxDuration
            
            tmp['vmState'] = vmState
            tmp['cpuRate'] = cpuRate
            tmp['memRate'] = memRate
            tmp['flow'] = flow
            tmp['duration'] = duration
            tmp['times'] = 1
            tmp['in2db'] = True
            
            VmWarnStat.info[vmName] = tmp
        
    def removeVmRunInfo(self, vmName) :
        """
        @summary: 删除告警信息
        @param vmName 虚拟机的名字
        """ 
        try:
            VmWarnStat.info.pop(vmName)
        except:
            pass
            
    def getAllVmWarnInfo(self) :
        """
        @summary: 获取所有警告信息
        """
        return VmWarnStat.info 

class ResourceStat() :
    vminfoList = []
    instanceInfoList = []
    def __init__(self) :
        self.logger = LoggerUtil().getLogger()
    
    def reloadVmInfo(self, db):
        """
        @summary: 重载虚拟机信息到内存
        """
        vminfoModule = VminfoModule(db)
        ResourceStat.vminfoList = vminfoModule.getEffectiveVmList()
    
    def getAllVmInfoList(self):
        """
        @summary: 获取虚拟机信列表
        """
        return ResourceStat.vminfoList
        
    def getVmInfo(self, vmName):
        """
        @summary: 通过虚拟机ID从缓存中获取虚拟机信息
        """
        for vmInfo in ResourceStat.vminfoList:
            if vmName == vmInfo['vmName']:
                return vmInfo;
        return None
    
    def reloadAppInstanceInfo(self, db):
        """
        @summary: 重载应用实例信息到内存
        """
        instanceInfoModule = InstanceInfoModule(db)
        ResourceStat.instanceInfoList = instanceInfoModule.getEffectiveInstanceList()
    
    def getAllAppInstanceInfoList(self):
        """
        @summary: 获取应用实例信息到内存
        """
        return ResourceStat.instanceInfoList
        
    def getInstanceInfo(self, instanceId):
        """
        @summary: 通过虚拟机ID从缓存中获取虚拟机信息
        """
        for instanceInfo in ResourceStat.instanceInfoList:
            if instanceId == instanceInfo['instanceId']:
                return instanceInfo;
        return None 
    