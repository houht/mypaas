#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#example:
#   iptest = iptablesHandle()
#   iptest.add_nat("10.16.123.18","1122","192.168.100.125","2211")
#   iptest.del_nat("10.16.123.18","1122","192.168.100.125","2211")
#*************************************

import os
from command import Command


IPTABLES = "/sbin/iptables"
SERVICE  = "/sbin/service"

class IptablesTools:
    "iptables  tools."

    def __init__(self):
        
        self.type = ""
        self.operation = ""
        self.cmd = Command()
        
    def add_nat(self,sip,sport,dip,dport):
        "Add rule"
        
        self.operation = "-A"
        # 1 tcp
        self.type = "tcp"
        self.iptables(sip,sport,dip,dport)
        # 2 udp
        self.type = "udp"
        self.iptables(sip,sport,dip,dport)
        
        self.save()
        
    def del_nat(self,sip,sport,dip,dport):
        "Delete rules."
        
        self.operation = "-D"
        # 1 tcp
        self.type = "tcp"
        self.iptables(sip,sport,dip,dport)
        # 2 udp
        self.type = "udp"
        self.iptables(sip,sport,dip,dport)
        
        self.save()
    
    
    def iptables(self,sip,sport,dip,dport):
        "Execution."
        
        self.cmd.execute("%s -t nat %s  PREROUTING -p %s -d %s --dport %s -j DNAT --to-destination %s:%s"%(IPTABLES,self.operation,self.type,dip,dport,sip,sport))
        
    
    def save(self):
        "Save rule"
        
        self.cmd.execute("%s iptables save >/dev/null 2>&1  "%SERVICE)
