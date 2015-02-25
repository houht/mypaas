#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

APPTABLE = "app"

import time

from scriptManage import ScriptManage
from appExecuter import AppExecuter

from cattle.utils import CustomException
from cattle.utils import SqliteTools

from cattle.services import ConfigManage
from cattle.services import VmManage



class AppManage:
    "application management"
    
    
    def __init__(self):
        ""
        
        # xml ����
        self.script = ScriptManage.getInstance()
        self.script.load()
    
        # ִ�ж���
        self.executer = AppExecuter()
    
        # ����
        self.conf = ConfigManage()
        # vm
        self.vm = VmManage()
        
    
    # ��ѯapp��Ϣ
    def app_info(self,instanceId=None):
        ""

        sql = "select * from %s where 1=1" % APPTABLE
        data = ()
        cond_conf = ''
        
        if instanceId is not None :
            cond_conf += ' and instanceId=?'
            data += (instanceId,)
            
            
        app_conf = self.conf.get_app_conf()
        app_db = app_conf['db_path']
        sql_tools = SqliteTools(app_db)
        
        if len(data) > 0 :
            sql += cond_conf
            infos = sql_tools.fetchall(sql,data)
        else :
            infos = sql_tools.fetchall(sql)
        
        apps = []
        for item in infos:
            app = {}
            if item is not None:
                app['instanceId'] = item[0]
                app['appName']    = item[1]
                app['appType']    = item[2]
                app['serviceId']  = item[3]
                app['vmName']     = item[4]
                app['domain']     = item[5]
                app['listenPort'] = item[6]
                
                app['param']      = item[7]
                app['status']     = item[8]
                
                app['createtime'] = item[9]
                app['remark']     = item[10]
            apps.append(app)
        
        
        return apps
        
    
    #�жϷ����Ƿ����
    def hasService(self, name):
        return self.script.hasService(name)
    
    
    def app_deploy(self, env):
        ""
  
        # ������ȡ
        serviceId = env.get_service_env('serviceId')
        
        instanceId = env.get_service_env('instanceId')
        
        appName = env.get_app_env('appName')
        if appName is None:
            appName = ""
            
        param = env.get_app_env('param')
        
        listenPort = env.get_router_env('listenPort')
        if listenPort is None:
            listenPort = 0
            
        domain = env.get_router_env('domain')
        if domain is None:
            domain = ""
        
        
        name = serviceId
        # 1 �жϷ���ʵ���Ƿ��Ѿ���װ
        app_info =  self.app_info(instanceId)
        if len(app_info)  == 1:
            raise CustomException("the service [%s]  already exists" % instanceId )
            return
        
        # 2 �жϷ����Ƿ����
        if not self.script.hasService(name):
            raise CustomException("Could not find the service %s" % str(name) )
            return
        
        # 3 �õ��ķ������
        service = self.script.getService(name)
        
        # 4 �õ�������б�
        actions =  service.target.actions['deploy']
        
        
        # 5 �������ݿ�
        appType = service.serviceType
        vmName = env.get_vm_env('name')
        status = 'creating'
        
        app_conf = self.conf.get_app_conf()
        app_db = app_conf['db_path']
        sql_tools = SqliteTools(app_db)
        
        save_sql = '''INSERT INTO %s values (?, ?, ?,?, ?,?,?,?,?,?,?)'''%APPTABLE
        data = [(instanceId, appName,appType,serviceId,vmName, domain,listenPort,param,status,time.strftime("%Y-%m-%d %H:%M:%S"),"")]
        sql_tools.save(save_sql,data)
    

        # 6 ѭ��������Ӧ�б��������
        
        # ������ֵ
        self.executer.env = env
        self.executer.properties = service.propertys.parameter
        
        # ����
        for action in actions:
            try:
                getattr(self.executer,action['action'])(action['param'])
            except Exception , e:
                # ɾ�����ݿ�
                delete_sql = 'DELETE FROM %s WHERE instanceId = ? '%APPTABLE
                data = [(instanceId,)]
                sql_tools.delete(delete_sql,data)
                # ɾ��VM
                self.vm.delete_vm(vmName)
                # �쳣
                raise CustomException("Error executing method %s !,%s"%(action['action'],str(e)))
                return 
        
        # 7 ���ݿ����
        status = 'created'
        update_sql = 'UPDATE %s SET status = ? WHERE instanceId = ? '%APPTABLE
        data = [(status, instanceId)]
        sql_tools.update(update_sql,data)
        
    
    
    # ��������
    def app_start(self, env):
        ""
        
        # ������ȡ
        instanceId = env.get_service_env('instanceId')
        
        # 1 ���ҷ���
        app_info =  self.app_info(instanceId)
        if len(app_info)  == 0:
            raise CustomException("the service [%s] not exists." % instanceId )
            return
        
        # 2 ���û�������
        env.set_vm_env('name', app_info[0]['vmName'])
        
        
        
        # 3 �õ��ķ������
        service = self.script.getService(app_info[0]['serviceId'])
        
        # 4 �õ�������б�
        actions =  service.target.actions['start']
        
        # 5 ִ��
        # ������ֵ
        self.executer.env = env
        self.executer.properties = service.propertys.parameter

        # 6 ����
        for action in actions:
            try:
                getattr(self.executer,action['action'])(action['param'])
            except Exception , e:
                raise CustomException("Error executing method %s !,%s"%(action['action'],str(e)))
                return
        
        # 7 �޸����ݿ�
        
    # ����ر�
    def app_stop(self, env):
        ""
        
        # ������ȡ
        instanceId = env.get_service_env('instanceId')
        
        # 1 ���ҷ���
        app_info =  self.app_info(instanceId)
        if len(app_info)  == 0:
            raise CustomException("the service [%s] not exists." % instanceId )
            return
        
        # 2 ���û�������
        env.set_vm_env('name', app_info[0]['vmName'])
        
        
        
        # 3 �õ��ķ������
        service = self.script.getService(app_info[0]['serviceId'])
        
        # 4 �õ�������б�
        actions =  service.target.actions['stop']
       
        # 5 ִ��
        # ������ֵ
        self.executer.env = env
        self.executer.properties = service.propertys.parameter
        
        # 6 �ر�
        for action in actions:
            try:
                getattr(self.executer,action['action'])(action['param'])
            except Exception , e:
                raise CustomException("Error executing method %s !,%s"%(action['action'],str(e)))
                return
        
        
    
    # ����ɾ��
    def app_drop(self, env):
        ""
        
        # ������ȡ
        instanceId = env.get_service_env('instanceId')
        
        # 1 ���ҷ���
        app_info =  self.app_info(instanceId)
        if len(app_info)  == 0:
            raise CustomException("the service [%s] not exists." % instanceId )
            return
        
        # 2 ���û�������
        env.set_vm_env('name', app_info[0]['vmName'])
        
        # 3 �õ��ķ������
        service = self.script.getService(app_info[0]['serviceId'])
        
        # 4 �õ�������б�
        actions =  service.target.actions['drop']
        
        
        # 5 ִ��
        # ������ֵ
        self.executer.env = env
        self.executer.properties = service.propertys.parameter
        
        # 6 ɾ��
        for action in actions:
            try:
                getattr(self.executer,action['action'])(action['param'])
            except Exception , e:
                raise CustomException("Error executing method %s !,%s"%(action['action'],str(e)))
                return
        
        # 7 ɾ�����ݿ�
        app_conf = self.conf.get_app_conf()
        app_db = app_conf['db_path']
        sql_tools = SqliteTools(app_db)
        
        delete_sql = 'DELETE FROM %s WHERE instanceId = ? '%APPTABLE
        data = [(instanceId,)]
        sql_tools.delete(delete_sql,data)
    
    
    # ������
    def app_balance(self):
        ""
        
        pass
    
    
    # ��������
    def app_conf(self):
        ""
        
        pass
    
    
    
    
    
    # ���������
    def create_app_table(self):
        ""
        
        app_conf = self.conf.get_app_conf()
        app_db = app_conf['db_path']
        sql_tools = SqliteTools(app_db)
        
        
        # 1 �����
        create_app_table_sql = '''CREATE TABLE `%s` (
                            `instanceId`     varchar(128) NOT NULL,
                            `appName`        varchar(128) default NULL,
                            `appType`        varchar(128) NOT NULL,
                            `serviceId`      varchar(128) NOT NULL,
                            
                            `vmName`         varchar(128) NOT NULL,
                            `domain`         varchar(128) default NULL,
                            `listenPort`     int(10) default 0,
                            `param`          text  default NULL,
                             
                            `status`     varchar(12) NOT NULL, 
                            
                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark`     varchar(1024) DEFAULT NULL,
                             PRIMARY KEY (`instanceId`)
                        )'''%APPTABLE
                        
        sql_tools.create_table(create_app_table_sql)


if __name__ == "__main__":
    
    
    
    print "start"
    
    aa = AppManage()
    
    #aa.create_app_table()
    bb =  aa.app_info('5555555')
    print  len(bb)  
    
    print "end"