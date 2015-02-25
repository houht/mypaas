#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from django.db import connection
from cattle.utils import CustomException


class DbTool() :
    ""
    
    
    def __init__(self) :
        ""
        
        pass
    
    
    def get_connection(self): 
        ""
        
        #connection = Connection(host="localhost",user="root",passwd="",use_unicode=True,charset="utf8")   
        #connection.select_db(‘ppsea_main’)   
        return connection
       
    def get_cursor(self):   
        ""
        
        return self.get_connection().cursor()   
    
    
    # 根据SQL取一条指定数据
    def select_fetchone(self,sql):   
        cursor = self.get_cursor()   
        cursor.execute(sql)   
        print "select_fetchone sql: %s" %(sql)   
        object = cursor.fetchone()   
        desc = cursor.description   
           
        if object:   
            print object   
            d = {}
            i = 0   
            for item in desc:   
                d[item[0]] = object[i]   
                i=i+1   
            print "one %s" %(d)   
            return d   
        else:   
            return object   
   
   
    # 根据SQL取的数据列表   
    def select_fetchall(self,sql):   
        cursor = self.get_cursor()   
        cursor.execute(sql)   
           
        print "select_fetchall sql: %s" %(sql)   
        
        items = cursor.fetchall()   
        
        desc = cursor.description   
        li = []   
        if items:   
            for item in items:                   
                d = {}   
                i = 0   
                for de in desc:   
                    d[de[0]] = item[i]   
                    i=i+1   
                li.append(d);   
            return li   
        else:   
            return li   
       
           
    # 执行插入和更新
    def execute(self,sql):
        ""
        
        try:
            connection = self.get_connection()   
            cursor=connection.cursor()   
            cursor.execute(sql) 
            #cursor.execute("commit")         
            connection.commit()
            cursor.close()
        except Exception , e:
            raise CustomException("Error: execute sql [%s]!"%sql)
        
       