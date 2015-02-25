#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************


import json

class JsonParser:
    "json type  decode & encode."

    def __init__(self,code='UTF-8'):
        self.code = code


    def decode(self,msg):
        "json type convert to others."
        try:
            return json.loads(msg,encoding=self.code)
        except (TypeError, ValueError):
            return -1
   
 
    def encode(self,msg):
        "others type convert to json."
        try:
            return json.dumps(msg,encoding=self.code)
        except (TypeError, ValueError):
            return -1

