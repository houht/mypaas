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
from koala_task.services import VmUseStat

class MonitorDbAction:
    ""
    tableTime = None
    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
        self.vmUseStat = VmUseStat()
        self.conf = ConfigManage()
        self.monitor_keep_max_time = self.conf.get_monitor_conf()['monitor_keep_max_time']
    
    def __getDb(self) :
        db_conf = self.conf.get_db_conf()
        db = MysqlTools(db_conf)
        return db  
            
    def processVmRunStat(self) :
        """
        @summary: 虚拟机和应用资源使用监控信息入库
        """
        nowTime = time.localtime(time.time())
        now = time.strftime('%Y-%m-%d %H:%M:%S',nowTime)
        cur_tableTime = time.strftime('%Y%m',nowTime)
        #获取数据操作对象
        db = self.__getDb()
        
        if MonitorDbAction.tableTime != cur_tableTime :
            self.createTable(db, cur_tableTime)
            MonitorDbAction.tableTime = cur_tableTime
       
        
        vmRunInfos = self.vmUseStat.cleanAllVmRunInfo(keepTime=self.monitor_keep_max_time)
        vm_running_param = []
        appinstance_running_param = []
        
        for info in vmRunInfos :
            keys = info.keys()
            logId = UUIDUtils.getId()
            vmName = info['vmName']
            status = info['vmState']
            
            cpuRate = float(0)
            memRate = float(0)
            flow = long(0)
            
            eventTime = info['eventTime']
            receiveTime = info['receiveTime']
            
            if 'cpuRate' in keys:
                cpuRate = float(info['cpuRate'])
            if 'memRate' in keys:
                memRate = float(info['memRate'])
            if 'flow' in keys:
                flow = long(info['flow'])
            
            if 'instanceId' in keys and info['instanceId'] is not None and len(info['instanceId'])>0:
                #app 应用 监控
                appinstance_running_param.append((logId,info['instanceId'],status,cpuRate,memRate,flow,eventTime,receiveTime))
            else :
                #vm 监控
                vm_running_param.append((logId,vmName,status,cpuRate,memRate,flow,eventTime,receiveTime))                
         
        try:
            if len(vm_running_param) != 0:
                sql = "insert into log_vm_running"+MonitorDbAction.tableTime+"(logId,vmName,status,cpuRate,memRate,flow,eventTime,receiveTime,createTime)values(%s,%s,%s,%s,%s,%s,%s,%s,now())"
                db.insertMany(sql,vm_running_param) 
        except Exception,e:
            self.logger.error("insert vm running info to db was error,msg:"+str(e))
        try:
            if len(appinstance_running_param) !=0:
                sql = "insert into log_appinstance_running"+MonitorDbAction.tableTime+"(logId,instanceId,status,cpuRate,memRate,flow,eventTime,receiveTime,createTime)values(%s,%s,%s,%s,%s,%s,%s,%s,now())"
                db.insertMany(sql, appinstance_running_param)    
        except Exception,e:
            self.logger.error("insert vm app instance running info to db was error,msg:"+str(e))   
        #self.logger.debug("write db monitor:"+str(vmRunInfos))
        try:
            db.close()
        except:
            pass
        
    def createTable(self, db, cur_tableTime):
        vm_running_sql ="""create table If Not Exists log_vm_running%s
                (
                   logId                varchar(32) not null,
                   vmName               varchar(128),
                   status               varchar(20),
                   cpuRate              float,
                   memRate              float,
                   flow                 double,
                   eventTime            datetime,
                   receiveTime          datetime,
                   createTime            datetime,
                   primary key (logId)
                )Engine MyISAM"""%cur_tableTime
        vm_runing_index_sql = """create index vm_createTimeIndex on log_vm_running%s(createTime)"""%cur_tableTime
        
        appinstance_running_sql = """create table log_appinstance_running%s
                (
                   logId                varchar(32) not null comment '日志ID',
                   instanceId           varchar(32),
                   status               varchar(20),
                   cpuRate              float,
                   memRate              float,
                   flow                 double,
                   eventTime            datetime,
                   receiveTime          datetime,
                   createTime            datetime,
                   primary key (logId)
                )Engine MyISAM"""%cur_tableTime
        appinstance_running_index_sql = """create index inst_createTimeIndex on log_appinstance_running%s(createTime)"""%cur_tableTime
        try:
            db.execute(vm_running_sql)
        except:
            pass
        try:
            db.execute(vm_runing_index_sql)
        except:
            pass
        try:
            db.execute(appinstance_running_sql)
        except:
            pass    
        try:
            db.execute(appinstance_running_index_sql)
        except:
            pass
        