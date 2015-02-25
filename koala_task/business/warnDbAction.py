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
from koala_task.services import VmWarnStat

class WarnDbAction:
    ""
    tableTime = None
        
    def __init__(self) :
        ""
        self.logger = LoggerUtil().getLogger()
        self.vmWarnStat = VmWarnStat()
        self.conf = ConfigManage()
    
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
        if WarnDbAction.tableTime != cur_tableTime :
            self.createTable(db, cur_tableTime)
            WarnDbAction.tableTime = cur_tableTime
            
        vmWarnInfos = self.vmWarnStat.getAllVmWarnInfo()
        vm_warn_param = []
        appinstance_warn_param = []
        
        warnKeys = vmWarnInfos.keys()
        for key in warnKeys:
            info = None
            try:
                info = vmWarnInfos[key]
            except:
                pass
            if info is None or info['in2db'] == False:
                continue
             
            logId = UUIDUtils.getId()
            keys = info.keys()
                        
            if 'instanceId' in keys and info['instanceId'] is not None and len(info['instanceId'])>0:
                #app 应用 监控
                appinstance_warn_param.append((logId,info['instanceId'],info['warnType'],info['vmState'],info['cpuRate'],info['memRate'],info['flow'],info['eventTime'],info['receiveTime'],info['duration'],info['times'],info['maxDuration']))
            else :
                #vm 监控
                vm_warn_param.append((logId,info['vmName'],info['warnType'],info['vmState'],info['cpuRate'],info['memRate'],info['flow'],info['eventTime'],info['receiveTime'],info['duration'],info['times'],info['maxDuration']))
        
        try:
            if len(vm_warn_param) != 0:
                sql = "insert into log_vm_warning"+WarnDbAction.tableTime+"(logId,vmName,warnType,status,cpuRate,memRate,flow,eventTime,receiveTime,createTime,duration,times,maxDuration)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s)"
                db.insertMany(sql,vm_warn_param) 
        except Exception,e:
            self.logger.error("insert vm warn info to db was error,msg:"+str(e))
        
        try:
            if len(appinstance_warn_param) !=0:
                sql = "insert into log_appinstance_warning"+WarnDbAction.tableTime+"(logId,instanceId,warnType,status,cpuRate,memRate,flow,eventTime,receiveTime,createTime,duration,times,maxDuration)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s)"
                db.insertMany(sql, appinstance_warn_param)
        except Exception,e:
            self.logger.error("insert app instance warn info to db was error,msg:"+str(e))
            self.logger.error("param:"+str(appinstance_warn_param))       
            
        
    def createTable(self, db, cur_tableTime):
        vm_warning_sql ="""create table If Not Exists log_vm_warning%s
                (
                   logId                varchar(32) not null,
                   vmName               varchar(128),
                   warnType             varchar(64),
                   status               varchar(20),
                   cpuRate              float,
                   memRate              float,
                   flow                 double,
                   eventTime            datetime,
                   receiveTime          datetime,
                   createTime           datetime,
                   duration             integer,
                   times                integer,
                   maxDuration          integer,
                   primary key (logId)
                )Engine MyISAM"""%cur_tableTime
        vm_warning_index_sql = """create index vm_createTimeIndex on log_vm_warning%s(createTime)"""%cur_tableTime
        
        appinstance_warning_sql = """create table log_appinstance_warning%s
                (
                   logId                varchar(32) not null comment '日志ID',
                   instanceId           varchar(32),
                   warnType             varchar(64),
                   status               varchar(20),
                   cpuRate              float,
                   memRate              float,
                   flow                 double,
                   eventTime            datetime,
                   receiveTime          datetime,
                   createTime           datetime,
                   duration             integer,
                   times                integer,
                   maxDuration          double,
                   primary key (logId)
                )Engine MyISAM"""%cur_tableTime
        appinstance_warning_index_sql = """create index inst_createTimeIndex on log_appinstance_warning%s(createTime)"""%cur_tableTime
        try:
            db.execute(vm_warning_sql)
        except:
            pass
        try:
            db.execute(vm_warning_index_sql)
        except:
            pass
        try:
            db.execute(appinstance_warning_sql)
        except:
            pass    
        try:
            db.execute(appinstance_warning_index_sql)
        except:
            pass        
               
if __name__ == "__main__" :   
    pass