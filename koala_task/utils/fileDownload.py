#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

import os
import urllib 

class FileDownload:
    "download  file."

    def __init__(self):
        pass


    def download(self,fileUrl, fileName=""):
        "download: 0,Success;-1,Failure" 

        if not os.path.exists(fileName):
            return -1

        filePath = os.path.join(fileDir,fileName) 
        
        try:
            urllib.urlretrieve(fileUrl, fileName,)
            return 0
        except Exception , e:
            return -1

