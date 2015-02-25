#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
import time
import os

from cattle.utils import iCloudStorage
from cattle.utils import SqliteTools
from cattle.utils import CustomException

from cattle.services import ConfigManage


class ImageManage:
    "images management"
    
    
    def __init__(self):
        ""
        
        self.conf = ConfigManage()


    def info_image(self,image_name):
        ""
        
        image_conf = self.conf.get_image_conf()
        images_db = image_conf['db_path']
        sql_tools = SqliteTools(images_db)
        
        fetchone_sql = 'SELECT * FROM images WHERE name = ? '
        data = image_name
        item = sql_tools.fetchone(fetchone_sql,data)
        infos = {}
        if item is not None:
            infos['imageid']   = item[0]
            infos['name']      = item[1]
            infos['system']    = item[2]
            infos['version']   = item[3]
            infos['arch']      = item[4]
            infos['machine']   = item[5]
            infos['size']      = item[6]
            infos['savepath']  = item[7]
            infos['ext']       = item[8]
            infos['status']    = item[9]
            infos['vtype']     = item[10]
            infos['createtime']= item[11]
            infos['remark']    = item[12]
        
        
        return infos
    
    def drop_image(self,image_name):
        ""
        
        image_conf = self.conf.get_image_conf()
        image_path = image_conf['path']
        
        image_file = os.path.join(image_path,image_name)
        if os.path.isfile(image_file): 
            os.remove(image_file)
        
        update_sql = 'UPDATE images SET status = ? WHERE name = ? '
        data = [(9, image_name)]
        
        images_db = image_conf['db_path']
        sql_tools = SqliteTools(images_db)
        sql_tools.update(update_sql,data)


    def download_image(self,image_name):
        ""
        
        if image_name is None :
            raise CustomException("image name is None.")
        
        image_conf = self.conf.get_image_conf()
        image_path = image_conf['path']
        image_file = os.path.join(image_path,image_name)
        
        if not os.path.exists(image_file):
            url = image_conf['download_addr']
            ics = iCloudStorage(url)
            result = ics.downloadShare(image_name,image_file)

            if result:
                infos = ics.getShareFileAttribute(image_name)
                save_sql = '''INSERT INTO images values (?, ?, ?,?, ?,?,?,?,?,?,?,?,?)'''
                data = [(infos['imageid'], image_name, infos['system'],infos['version'],infos['arch'], infos['machine'],infos['size'],image_file,infos['ext'],0,infos['vtype'],time.strftime("%Y-%m-%d %H:%M:%S"),infos['remark'])]
                
                images_db = image_conf['db_path']
                sql_tools = SqliteTools(images_db)
                sql_tools.save(save_sql,data)
            else:
                raise CustomException("download image Failure.")
        
        return image_file
        
    def create_images_table(self):
        ""
        
        create_table_sql = '''CREATE TABLE `images` (
                            `imageId` varchar(64) NOT NULL,
                            `name` varchar(200) DEFAULT NULL,
                            `system` varchar(64) DEFAULT NULL,
                            `version` varchar(64) DEFAULT NULL,
                            `arch` varchar(64) DEFAULT NULL,
                            `machine`  varchar(64) DEFAULT NULL,
                            `size` double(24) DEFAULT NULL,
                            `savepath` varchar(64) DEFAULT NULL,
                            `ext` varchar(64) DEFAULT NULL,
                            `status` int(1) DEFAULT 0,
                            `vtype` varchar(64) DEFAULT NULL,
                            `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            `remark` varchar(1024) DEFAULT NULL,
                             PRIMARY KEY (`imageId`)
                        )'''
        
        image_conf = self.conf.get_image_conf()
        images_db = image_conf['db_path']
        sql_tools = SqliteTools(images_db)
        sql_tools.create_table(create_table_sql)
