#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#example:
#
#    sqltest = sqliteHandle("/home/tools/test.db")
#    sqltest.drop_table("student")
#    create_table_sql = '''CREATE TABLE `student` (
#                          `id` int(11) NOT NULL,
#                          `name` varchar(20) NOT NULL,
#                          `gender` varchar(4) DEFAULT NULL,
#                          `age` int(11) DEFAULT NULL,
#                          `address` varchar(200) DEFAULT NULL,
#                          `phone` varchar(20) DEFAULT NULL,
#                           PRIMARY KEY (`id`)
#                        )'''
#    sqltest.create_table(create_table_sql)
#    
#    save_sql = '''INSERT INTO student values (?, ?, ?, ?, ?, ?)'''
#    data = [(1, 'Hongten', 'man', 20, 'guangzhou', '13423****62'),
#            (2, 'Tom', 'man', 22, 'guangdong', '15423****63'),
#            (3, 'Jake', 'woman', 18, 'beijing', '18823****87'),
#            (4, 'Cate', 'woman', 21, 'shanghai', '14323****32')]
#    sqltest.save(save_sql,data)
#
#    fetchall_sql = '''SELECT * FROM student'''
#    print sqltest.fetchall(fetchall_sql)
#    
#    fetchone_sql = 'SELECT name FROM student WHERE ID = ? '
#    data = 1
#    print sqltest.fetchone(fetchone_sql,data)
#
#    update_sql = 'UPDATE student SET name = ? WHERE ID = ? '
#    data = [('HongtenAA', 1),
#            ('HongtenBB', 2)]
#    sqltest.update(update_sql,data)
#
#    delete_sql = 'DELETE FROM student WHERE NAME = ? AND ID = ? '
#    data = [('HongtenAA', 1),
#            ('HongtenBB', 2)]
#    
#    sqltest.delete(delete_sql,data)
#    fetchall_sql = '''SELECT * FROM student'''
#    print sqltest.fetchall(fetchall_sql)
#    sqltest.close_all()
#*************************************


import sqlite3
import os

from customException import CustomException



'''SQLite数据库是一款非常小巧的嵌入式开源数据库软件，也就是说
没有独立的维护进程，所有的维护都来自于程序本身。
在python中，使用sqlite3创建数据库的连接，当我们指定的数据库文件不存在的时候
连接对象会自动创建数据库文件；如果数据库文件已经存在，则连接对象不会再创建
数据库文件，而是直接打开该数据库文件。
    连接对象可以是硬盘上面的数据库文件，也可以是建立在内存中的，在内存中的数据库
    执行完任何操作后，都不需要提交事务的(commit)

    创建在硬盘上面： conn = sqlite3.connect('c:\\test\\test.db')
    创建在内存上面： conn = sqlite3.connect('"memory:')

    下面我们一硬盘上面创建数据库文件为例来具体说明：
    conn = sqlite3.connect('c:\\test\\hongten.db')
    其中conn对象是数据库链接对象，而对于数据库链接对象来说，具有以下操作：

        commit()            --事务提交
        rollback()          --事务回滚
        close()             --关闭一个数据库链接
        cursor()            --创建一个游标

    cu = conn.cursor()
    这样我们就创建了一个游标对象：cu
    在sqlite3中，所有sql语句的执行都要在游标对象的参与下完成
    对于游标对象cu，具有以下具体操作：

        execute()           --执行一条sql语句
        executemany()       --执行多条sql语句
        close()             --游标关闭
        fetchone()          --从结果中取出一条记录
        fetchmany()         --从结果中取出多条记录
        fetchall()          --从结果中取出所有记录
        scroll()            --游标滚动

'''

#是否打印sql
SHOW_SQL = False


class SqliteTools:
    

    def __init__(self,dbFile):
        '''获取到数据库的连接对象，参数为数据库文件的绝对路径
        如果传递的参数是存在，并且是文件，那么就返回硬盘上面改
        路径下的数据库文件的连接对象；否则，返回内存中的数据接
        连接对象'''
        
        conn = sqlite3.connect(dbFile)
        if os.path.exists(dbFile) and os.path.isfile(dbFile):
            if SHOW_SQL:
                print('硬盘上面:[{0}]'.format(dbFile))
            self.conn = conn
            '''该方法是获取数据库的游标对象，参数为数据库的连接对象
            如果数据库的连接对象不为None，则返回数据库连接对象所创
            建的游标对象；否则返回一个游标对象，该对象是内存中数据
            库连接对象所创建的游标对象'''
            self.cu = conn.cursor()
        else:
            raise CustomException("The file %s create failed!" % dbFile ) 
    
    
    ###############################################################
    ####            创建|删除表操作     START
    ###############################################################
    def drop_table(self,table):
        '''如果表存在,则删除表，如果表中存在数据的时候，使用该
        方法的时候要慎用！'''
        if table is not None and table != '':
            sql = 'DROP TABLE IF EXISTS ' + table
            if SHOW_SQL:
                print('执行sql:[{0}]'.format(sql))
            self.cu.execute(sql)
            self.conn.commit()
            if SHOW_SQL:
                print('删除数据库表[{0}]成功!'.format(table))
            
        else:
            raise CustomException('table is empty or equal None!')
    
    
    def create_table(self,sql):
        '''创建数据库表：student'''
        if sql is not None and sql != '':
            if SHOW_SQL:
                print('执行sql:[{0}]'.format(sql))
            self.cu.execute(sql)
            self.conn.commit()
            if SHOW_SQL:
                print('创建数据库表[student]成功!')
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql))
    
    ###############################################################
    ####            创建|删除表操作     END
    ###############################################################
    
    def close_all(self):
        '''关闭数据库游标对象和数据库连接对象'''
        try:
            if self.cu is not None:
                self.cu.close()
        finally:
            if self.conn is not None:
                self.conn.close()
    
    
    ###############################################################
    ####            数据库操作CRUD     START
    ###############################################################
    
    def save(self,sql, data):
        '''插入数据'''
        if sql is not None and sql != '':
            if data is not None:
                for d in data:
                    if SHOW_SQL:
                        print('执行sql:[{0}],参数:[{1}]'.format(sql, d))
                    self.cu.execute(sql, d)
                    self.conn.commit()
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql))
    
    def fetchall(self,sql, data=None):
        '''查询所有数据'''
        reslut=[]
        if sql is not None and sql != '':
            if SHOW_SQL:
                print('执行sql:[{0}]'.format(sql))
            if data is None :
                self.cu.execute(sql)
            else :
                self.cu.execute(sql, data)
            r = self.cu.fetchall()
            if len(r) > 0:
                for e in range(len(r)):
                    reslut.append(r[e])
            return reslut
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql)) 
    
    def fetchone(self,sql,data):
        '''查询一条数据'''
        if sql is not None and sql != '':
            if data is not None:
                #Do this instead
                d = (data,) 
                if SHOW_SQL:
                    print('执行sql:[{0}],参数:[{1}]'.format(sql, data))
                self.cu.execute(sql, d)
                r = self.cu.fetchall()
                if len(r) > 0:
                    for e in range(len(r)):
                        return (r[e])
            else:
                print('the [{0}] equal None!'.format(data))
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql))
    
    
    def update(self,sql,data):
        '''更新数据'''
        if sql is not None and sql != '':
            if data is not None:
                
                for d in data:
                    if SHOW_SQL:
                        print('执行sql:[{0}],参数:[{1}]'.format(sql, d))
                    self.cu.execute(sql, d)
                    self.conn.commit()
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql))
    
    
    
    def delete(self,sql, data):
        '''删除数据'''
        if sql is not None and sql != '':
            if data is not None:
                for d in data:
                    if SHOW_SQL:
                        print('执行sql:[{0}],参数:[{1}]'.format(sql, d))
                    self.cu.execute(sql, d)
                    self.conn.commit()
            else :
               self.cu.execute(sql)
               self.conn.commit()
        else:
            raise CustomException('the [{0}] is empty or equal None!'.format(sql))

