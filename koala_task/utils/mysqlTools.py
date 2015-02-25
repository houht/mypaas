#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201412
#desc: 
#
#*************************************


import MySQLdb
from MySQLdb.cursors import DictCursor
import os

from customException import CustomException


class MysqlTools:
    def __init__(self, conf) :
        
        self.host = conf['host']
        self.db = conf['db']
        self.user = conf['user']
        self.passwd = conf['passwd']
        
        self.port = None
        self.charset = None
        
        k = conf.keys()
        if 'port' in k :
            self.port = int(conf['port'])
        if 'charset' in k:
            self.charset = conf['charset']
        
        self._conn = self.__connect()
        self._cursor = self.__getCursors(self._conn)
        self._conn.autocommit(1)
          
    def __connect(self):
        """
        @summary: 获取数据库连接
        """
        conn = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db,charset=self.charset)
        return conn
    
    def __getCursors(self, conn=None):
        """
        @summary: 获取数据库连接游标
        @conn：数据连接，如果None表示新建立一个数据库连接
        """
        if conn is None :
            conn = self.connect()
        return conn.cursor()
    
    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']
        
    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count
            
    def getAll(self, sql, param=None) :
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count>0:
            result = self._cursor.fetchall()
        else:
            result = []
        return result
    
    def getOne(self, sql, param=None) :
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result
    
    def getMany(self, sql, num, param=None) :
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchmany(num)
        else:
            result = {}
        return result 
    
    def insertOne(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql, value)
        return self.__getInsertId()
    
    def insertMany(self, sql, value):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list        
        """
        self._cursor.executemany(sql, value)
        
    def insert(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: count 受影响的行数
        """
        return self._cursor.execute(sql, value)
     
    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @cursor: 数据库游标
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)
    
    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)
    
    def execute(self, sql, param=None):
        """
        @summary: 执行sql，主要用来创建表，创建索引等操作
        @param sql: ＳＱＬ格式及条件
        @param param: 参数
        """
        return self.__query(sql, param)
        
    def begin(self):
        """
        @summary: 开启事务
        @conn: 数据库链接
        """
        self._conn.autocommit(0)
    
    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.autocommit(1)
        
    def close(self, isEnd=1):
        """
        @summary: 释放连接池资源
        @isEnd：1表示提交，其它值表示回滚
        """
        if isEnd==1:
            self.end('commit')
        else:
            self.end('rollback')
        
        self._cursor.close()
        self._conn.close()
        