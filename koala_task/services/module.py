#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201412
#desc: 
#*************************************

from koala_task.utils import MysqlTools

class TaskinfoModule():
    def __init__(self, db):
        self.table = "app_taskinfo"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过任务id查询任务信息
        @param id: 任务id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select taskId,taskType,content,taskStatus,dealwith,createTime,business_id,updateTime from "+self.table+" where taskId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('taskId','taskType','content','taskStatus','dealwith','createTime','businessId','updateTime'),
                        info
                    )
                )
            return res
        else :
            return info
    
    def getAll(self, dealwith='open'):
        """
        @summary: 读取任务列表
        @param id: 任务id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select taskId,taskType,content,taskStatus,dealwith,createTime,business_id,updateTime from "+self.table+" where dealwith=%s order by updateTime asc"        
        param = (dealwith,)
        res_list = self.db.getAll(sql, param)
        res = []
        for info in res_list:
            tmp = dict(
                zip(
                    ('taskId','taskType','content','taskStatus','dealwith','createTime','businessId','updateTime'),
                    info
                )
            )
            res.append(tmp)
        return res
        
    
    def update(self, param):
        """
        @summary: 更新任务信息
        @param id: 任务id
        @return: count 受影响的行数
        """
        sql = "update "+self.table+" set updateTime=now()"
        #taskType,content,taskStatus,dealwith,updateTime,taskId
        if param is None or len(param) < 2:
            return 0
            
        key = param.keys()
        
        v_param = ()
                
        sql_condi = ""
        if 'taskType' in key :
            sql_condi += ',taskType = %s'
            v_param += (param['taskType'],)
        if 'content' in key :
            sql_condi += ',content = %s'
            v_param += (param['content'],)
        if 'taskStatus' in key :
            sql_condi += ',taskStatus = %s'
            v_param += (param['taskStatus'],)
        if 'dealwith' in key :
            sql_condi += ',dealwith = %s'
            v_param += (param['dealwith'],)        
        
        if len(sql_condi)==0 or 'taskId' not in key:
            return 0
            
        sql += sql_condi + ' where taskId=%s'
        v_param += (param['taskId'],)
        
        return self.db.update(sql, v_param)
     
     
    def insert(self, param) :
        """
        @summary: 添加任务处理信息
        @param param: 任务信息
        @return: insertId 受影响的行数
        """
        sql = "insert into "+self.table+" VALUES (%s,%s,%s,%s,%s,now(),%s,now())" 
        
        taskId = None
        taskType = None
        content = None
        taskStatus = None
        dealwith = None
        businessId = None
        
        key = param.keys()
        
        if 'taskId' in key :
            taskId = param['taskId']
        if 'taskType' in key :
            taskType = param['taskType']
        if 'content' in key :
            content = param['content']
        if 'taskStatus' in key :
            taskStatus = param['taskStatus']
        if 'dealwith' in key :
            dealwith = param['dealwith']
        if 'businessId' in key :
            businessId = param['businessId']

        v_param = (taskId, taskType, content, taskStatus,dealwith,businessId)
        print sql
        print v_param
        res = self.db.insert(sql, v_param)
        print res
        return res
     
class DealwithInfoModule():
    def __init__(self, db):
        self.table = "app_dealwithinfo"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过任务处理id查询任务处理信息
        @param id: 任务处理id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select dealwithId,task_id,dealwithType,message,status,createTime from "+self.table+" where dealwithId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        print info
        if info :
            res = dict(
                    zip(
                        ('dealwithId','taskId','dealwithType','message','status','createTime'),
                        info
                    )
                )
            return res
        else :
            return info
    
    def getByTaskId(self, taskId, dealwithType=None):
        """
        @summary: 通过任务id查询任务处理信息
        @param taskId: 任务id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select dealwithId,task_id,dealwithType,message,status,createTime from "+self.table+" where task_id=%s" 
        param = (taskId,)
        if dealwithType is not None :
            sql +=" and dealwithType=%s"
            param +=(dealwithType,)
        res_list = self.db.getAll(sql, param)
        res = []
        for info in res_list:
            tmp = dict(
                zip(
                    ('dealwithId','taskId','dealwithType','message','status','createTime'),
                    info
                )
            )
            res.append(tmp)
        return res
    
    def insert(self, param) :
        """
        @summary: 添加任务处理信息
        @param param: 任务信息
        @return: insertId 受影响的行数
        """
        sql = "insert into "+self.table+"(dealwithId,task_id,dealwithType,message,status,createTime)values(%s,%s,%s,%s,%s,now())" 
        dealwithId = None
        taskId = None
        dealwithType = None
        message = None
        status = None
        
        key = param.keys()
        
        if 'dealwithId' in key :
            dealwithId = param['dealwithId']
        if 'taskId' in key :
            taskId = param['taskId']
        if 'dealwithType' in key :
            dealwithType = param['dealwithType']
        if 'message' in key :
            message = param['message']
        if 'status' in key :
            status = param['status']
        
        v_param = (dealwithId, taskId, dealwithType, message, status)
        print sql
        print v_param
        res = self.db.insert(sql, v_param)
        print res
        return res
        
        
class InstanceInfoModule():
    def __init__(self, db):
        self.table = "app_instanceinfo"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过应用实例id查询应用实例信息
        @param id: 应用实例id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select instanceId,app_id,engineId,ip,port,status,createTime,beginTime,endTime from "+self.table+" where instanceId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('instanceId','appId','engineId','ip','port','status','createTime','beginTime','endTime'),
                        info
                    )
                )
            return res 
        else :
            return info
    
    def update(self, param):
        """
        @summary: 更新应用实例信息
        @param id: 应用实例id
        @return: count 受影响的行数
        """
        sql = "update "+self.table+" set "
        #engineId, ip, port, status, beginTime, endTime, instanceId
        
        if param is None or len(param) < 2:
            return 0
            
        key = param.keys()
        
        v_param = ()
                
        sql_condi = ""
        if 'engineId' in key :
            sql_condi += ',engineId = %s'
            v_param += (param['engineId'],)
        if 'ip' in key :
            sql_condi += ',ip = %s'
            v_param += (param['ip'],)
        if 'port' in key :
            sql_condi += ',port = %s'
            v_param += (param['port'],)
        if 'status' in key :
            sql_condi += ',status = %s'
            v_param += (param['status'],)
        if 'beginTime' in key :
            if param['beginTime']=='now' :
                sql_condi += ',beginTime = now()'
            else:
                sql_condi += ',beginTime = %s'
                v_param += (param['beginTime'],)
        if 'endTime' in key :
            sql_condi += ',endTime = %s'
            v_param += (param['endTime'],)
        
        if len(sql_condi)==0 or 'instanceId' not in key:
            return 0
            
        sql += sql_condi[1:] + ' where instanceId=%s'
        v_param += (param['instanceId'],)
        
        return self.db.update(sql, v_param)
    
    def insert(self, param) :
        """
        @summary: 添加任务处理信息
        @param param: 任务信息
        @return: insertId 受影响的行数
        """
        sql = "insert into "+self.table+" (instanceId,app_id,status,createTime) VALUES (%s,%s,%s,now())" 

        instanceId = None
        appId = None
        status = None
        
        key = param.keys()
        
        if 'instanceId' in key :
            instanceId = param['instanceId']
        if 'appId' in key :
            appId = param['appId']
        if 'status' in key :
            status = param['status']
        
        v_param = (instanceId, appId, status)
        print sql
        print v_param
        res = self.db.insert(sql, v_param)
        print res
        return res
        
    def getEffectiveInstanceList(self):
        """
        @summary: 获取所有有效的应用实例信息列表
        @return: result list/boolean 查询到的结果集
        """
        sql = "select instanceId,app_id,engineId,ip,port,status,createTime,beginTime,endTime from "+self.table+" where status in ('deployed','starting','running','startFail','closeing','closed','closeFail')" 
            
        res_list = self.db.getAll(sql, None)
        res = []
        for info in res_list:
            tmp = dict(
                zip(
                    ('instanceId','appId','engineId','ip','port','status','createTime','beginTime','endTime'),
                    info
                )
            )
            res.append(tmp)
        return res
        
    
class AppInfoModule():
    def __init__(self, db):
        self.table = "app_appinfo"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过应用id查询任务处理信息
        @param id: 应用id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select appId,service_id,appName,cpu,mem,disk,appFileId,appEnv,userEnv,domain,tokenId,listenPort from "+self.table+" where appId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('appId','serviceId','appName','cpu','mem','disk','appFileId','appEnv','userEnv','domain','tokenId','listenPort'),
                        info
                    )
                )
            return res
        else :
            return info
    
class ServiceInfoModule():
    ""
    
    def __init__(self, db):
        self.table = "app_serviceinfo"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过服务id查询服务信息
        @param id: 服务id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select serviceId,serviceType,serviceName,status,protocol from "+self.table+" where serviceId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('serviceId','serviceType','serviceName','status','protocol'),
                        info
                    )
                )
            return res
        else :
            return res
     
     
   
        
        

class MonitorPolicy():
    def __init__(self, db):
        self.table = "conf_monitor_policy"
        self.db = db
    
    def getById(self,id):
        """
        @summary: 通过策略id查询策略信息
        @param id: 服务id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select policyId,name,rule,type,createTime from "+self.table+" where policyId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('policyId','name','rule','type','createTime'),
                        info
                    )
                )
            return res
        else :
            return res    
        
    

    

# vm表
class VminfoModule():
    def __init__(self, db):
        self.table = "vm_vminfo"
        self.db = db
    
    
    def getById(self,id):
        """
        @summary: 通过应用实例id查询应用实例信息
        @param id: 应用实例id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select vmId,vmName,vmAlias,cpu,mem,size,image_id,engineId,engineIp,ip,vncPasswd,vncPort,username,password,user,status ,createTime from "+self.table+" where vmId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('vmId','vmName','vmAlias','cpu','mem','size','imageId','engineId','engineIp','ip','vncPasswd','vncPort','username','password','user','status','createTime'),
                        info
                    )
                )
            return res 
        else :
            return info
    
    
    def update(self, param):
        """
        @summary: 更新应用实例信息
        @param id: 应用实例id
        @return: count 受影响的行数
        """
        sql = "update "+self.table+" set "
        #engineId,engineIp, ip, vncPasswd,vncPort, status, beginTime, endTime, vmId
        
        if param is None or len(param) < 2:
            return 0
            
        key = param.keys()
        
        v_param = ()
                
        sql_condi = ""
        if 'engineId' in key :
            sql_condi += ',engineId = %s'
            v_param += (param['engineId'],)
        if 'engineIp' in key :
            sql_condi += ',engineIp = %s'
            v_param += (param['engineIp'],)
        if 'ip' in key :
            sql_condi += ',ip = %s'
            v_param += (param['ip'],)
            
        if 'vncPasswd' in key :
            sql_condi += ',vncPasswd = %s'
            v_param += (param['vncPasswd'],)
        
        if 'vncPort' in key :
            sql_condi += ',vncPort = %s'
            v_param += (param['vncPort'],)
        if 'status' in key :
            sql_condi += ',status = %s'
            v_param += (param['status'],)
        if 'beginTime' in key :
            if param['beginTime']=='now' :
                sql_condi += ',beginTime = now()'
            else:
                sql_condi += ',beginTime = %s'
                v_param += (param['beginTime'],)
        if 'endTime' in key :
            sql_condi += ',endTime = %s'
            v_param += (param['endTime'],)
        
        if len(sql_condi)==0 or 'vmId' not in key:
            return 0
            
        sql += sql_condi[1:] + ' where vmId=%s'
        v_param += (param['vmId'],)
        
        return self.db.update(sql, v_param)
        
    def getEffectiveVmList(self):
        """
        @summary: 获取所有有效的虚拟机信息列表
        @return: result list/boolean 查询到的结果集
        """
        sql = "select vmId,vmName,cpu,mem,size,image_id,engineId,engineIp,ip,vncPasswd,vncPort,username,password,user,status ,createTime from "+self.table+" where status in ('created','starting','running','startFail','stopping','stopFail','stoped')" 
        
        res_list = self.db.getAll(sql, None)
        res = []
        for info in res_list:
            tmp = dict(
                zip(
                    ('vmId','vmName','cpu','mem','size','imageId','engineId','engineIp','ip','vncPasswd','vncPort','username','password','user','status','createTime'),
                    info
                )
            )
            res.append(tmp)
        return res

# vm镜像表       
class VmImageModule():
    def __init__(self, db):
        self.table = "vm_image"
        self.db = db
    
    
    def getByImageId(self,imageId):
        """
        @summary: 通过应用实例id查询应用实例信息
        @param id: 应用实例id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select imageName,system,version,arch,machine,size,username,password,status ,vtype ,remark,createTime  from "+self.table+" where imageId=%s" 
        param = (imageId,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('imageName','system','version','arch','machine','size','username','password','status','vtype','remark','createTime'),
                        info
                    )
                )
            return res 
        else :
            return info

# vm网络表
class VmnetModule():
    def __init__(self, db):
        self.table = "vm_net"
        self.db = db

    
    def getById(self,id):
        """
        @summary: 通过应用实例id查询应用实例信息
        @param id: 应用实例id
        @return: result list/boolean 查询到的结果集
        """
        sql = "select netId,proxyIP,proxyPort,proxyType,ip,port,vm_id,createTime from "+self.table+" where netId=%s" 
        param = (id,)
        info = self.db.getOne(sql, param)
        if info :
            res = dict(
                    zip(
                        ('netId','proxyIP','proxyPort','proxyType','ip','port','vmId','createTime'),
                        info
                    )
                )
            return res 
        else :
            return info

    
    def update(self, param):
        """
        @summary: 更新应用实例信息
        @param id: 应用实例id
        @return: count 受影响的行数
        """
        sql = "update "+self.table+" set "
        #engineId,engineIp, ip, vncPasswd,vncPort, status, beginTime, endTime, vmId
        
        if param is None or len(param) < 2:
            return 0
            
        key = param.keys()
        
        v_param = ()
                
        sql_condi = ""
        if 'proxyIP' in key :
            sql_condi += ',proxyIP = %s'
            v_param += (param['proxyIP'],)
        if 'proxyPort' in key :
            sql_condi += ',proxyPort = %s'
            v_param += (param['proxyPort'],)
        if 'proxyType' in key :
            sql_condi += ',proxyType = %s'
            v_param += (param['proxyType'],)
            
        
        if 'ip' in key :
            sql_condi += ',ip = %s'
            v_param += (param['ip'],)
        if 'port' in key :
            sql_condi += ',port = %s'
            v_param += (param['port'],)

        if len(sql_condi)==0 or 'netId' not in key:
            return 0
            
        sql += sql_condi[1:] + ' where netId=%s'
        v_param += (param['netId'],)
        
        return self.db.update(sql, v_param)

# vm硬盘表
class vmDiskModule():
    def __init__(self, db):
        self.table = "vm_disk"
        self.db = db
        