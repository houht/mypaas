#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2014-2099 
#
# This file is part of cattle.
#
#*************************************
#author:zhengqs
#create:201410
#desc: icloud storage util

import os

from http import Http
from jsonParser import JsonParser
from customException import CustomException, CustomReqTimeoutException

class iCloudStorage :
    def __init__(self, url, account=None, passwd=None, encoding='utf-8') :
        self.url = url.rstrip("/")
        self.account = account
        self.passwd = passwd
        self.encoding=encoding
        self.token = None
        self.uttpUtil = Http()

    #认证
    def auth(self):
        auth_url = self.url + '/auth'
        if self.account == None:
            _params = None
            return False
        else :
            _params = {'account' : self.account, 'password' : self.passwd}
            reponse = self.uttpUtil.doPost(auth_url, params=_params, accept='application/json')
            jsonUtil = JsonParser(code=self.encoding)
            result = jsonUtil.decode(reponse)
            if 'result' in result :
                if result['result'] != "OK":
                    raise CustomAuthException('认证失败')
            else :
                raise CustomAuthException('认证失败')
            
            self.token = result['content']['token']
            return True

    #通过共享名称获取文件
    def downloadShare(self,shareFile, fileName, params=None) :
        dowload_url = self.url + '/files/get/s/' + shareFile
        bFlag = self.uttpUtil.download(dowload_url, fileName, params)
        return bFlag

    #通过文件ID获取文件
    def download(self,fileId, fileName, params=None) :
        dowload_url = self.url + '/files/get/file/'+fileId+"?token="+self.token
        bFlag = self.uttpUtil.download(dowload_url, fileName, params)
        return bFlag

    #通过文件ID获取文件属性
    def getFileAttribute(self,fileId, params=None) :
        _url = self.url + '/files/get/fileMetadata/'+fileId +"?token="+self.token
        reponse = self.uttpUtil.doGet(_url, params, accept='application/json')
        jsonUtil = JsonParser(code=self.encoding)
        result = jsonUtil.decode(reponse)
        if 'result' in result :
            if result['result'] != "OK":
                raise CustomAuthException('获取文件失败')
        else :
            raise CustomAuthException('获取文件失败')
        
        return result['content']

    #通过共享名称获取文件属性
    def getShareFileAttribute(self,shareFile, params=None) :
        _url = self.url + '/files/get/s/fileMetadata/'+shareFile
        reponse = self.uttpUtil.doGet(_url, params, accept='application/json')
        jsonUtil = JsonParser(code=self.encoding)
        result = jsonUtil.decode(reponse)
        if 'result' in result :
            if result['result'] != "OK":
                raise CustomAuthException('获取文件失败')
        else :
            raise CustomAuthException('获取文件失败')
        result['content']['imageid']=shareFile
        return result['content']
