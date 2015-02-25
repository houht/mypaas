#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2014-2099 
#
# This file is part of cattle.
#
#*************************************
#author:zhengqs
#create:201410
#desc:  util

import os
import urllib2
import urllib
import socket
import time

from customException import CustomException, CustomReqTimeoutException

class Http :
    
    def __init__(self) :
        self.http_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",  
             "Accept": "text/html"}
        self.timeout = 30
        self.readTimeout = 50
        socket.setdefaulttimeout(10.0)
        
    #get方式提交
    def doGet(self, url, params, accept="text/html") :
        _url = ""        
        if params not in (None, ''):
            _params = urllib.urlencode(params)
            if '?' in url > 0 :
                _url = "%s&%s" % (url,_params)
            else :
                _url = "%s?%s" % (url,_params)
        else :
           _url = url
           
        try:
            #time.sleep(self.readTimeout)
            req = urllib2.Request(_url, headers=self.http_headers)
            req.add_header('Accept', accept)
            
            req.get_method = lambda: 'GET'
            page = urllib2.urlopen(req)#, timeout=self.timeout)
            code = page.getcode()
            ret_data = page.read()
            return ret_data
        except urllib2.HTTPError, e:
            raise CustomException(e)
        except urllib2.URLError, e:
            raise CustomException(e)
        except socket.timeout, e:
            raise CustomReqTimeoutException(e)  
        
    #post方式提交
    def doPost(self, url, params, accept="text/plain") :
        
        _params = {}
        if params not in (None, ''):
            _params = urllib.urlencode(params)
        
        try:
            req = urllib2.Request(url, data=_params, headers=self.http_headers) 
            req.add_header('Accept', accept)
            req.get_method = lambda: 'POST'
            
            page = urllib2.urlopen(req,timeout=self.timeout)
            code = page.getcode()
            ret_data = page.read()
            return ret_data
        except urllib2.HTTPError, e:
            raise CustomException(e)
        except urllib2.URLError, e:
            raise CustomException(e)
        except socket.timeout, e:
            raise CustomReqTimeoutException(e)

    def download(self, url, fileName, params=None) :
        try:
            _url = ""        
            if params not in (None, ''):
                _params = urllib.urlencode(params)
                if '?' in url > 0 :
                    _url = "%s&%s" % (url,_params)
                else :
                    _url = "%s?%s" % (url,_params)
            else :
                _url = url
            #print _url
            urllib.urlretrieve(_url, fileName,)
            return True
        except Exception , e:
            print e
            return False
    
