#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************

from ConfigParser import ConfigParser
from customException import CustomException
import os
import codecs

class ParserConf(Exception):
    "parser config."

    def __init__(self,confFile):
        
        if not os.path.isfile(confFile):
            raise CustomException("The file %s does not exist!" % confFile )
        self.confFile = confFile
        self.config   = ConfigParser()
        #self.config.readfp(codecs.open(confFile, 'r',"utf_16"))
        self.config.read(confFile)

    def get_sections(self):
        "return all section."
          
        return self.config.sections()
    
    def add_section(self,section):
        "create a new section."
        
        self.config.add_section(section) 
        self.config.write(open(self.confFile, "w"))

    def remove_section(self,section):
        "remove a section."
        
        self.config.remove_section(section) 
        self.config.write(open(self.confFile, "w"))

    def get_items(self,section):
        "return section's items."
        
        try:
            return self.config.items(section) 
        except:  
            return None

    def get_item(self,section,key):
        "return a item value."

        try:
            return self.config.get(section,key) 
        except:  
            return None 
            
    def update_item(self,section,key,value):
        "update a item."

        self.config.set(section, key, value) 
        self.config.write(open(self.confFile, "w"))

    def create_item(self,section,key,value):
        "create a item."

        self.config.set(section, key, value) 
        self.config.write(open(self.confFile, "w"))

    def remove_item(self,section,key):
        "remove a item."

        self.config.remove_option(section, key) 
        self.config.write(open(self.confFile, "w"))



