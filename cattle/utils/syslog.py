#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201410
#desc: syslog util
# usage
#
# syslogUtil = syslogHandle([('192.168.0.1',514)], 20, 'cattle')
# syslogUtil.sendmsg('this is test log',7)
#
# syslog severity define:
#0       Emergency: system is unusable 
#1       Alert: action must be taken immediately 
#2       Critical: critical conditions 
#3       Error: error conditions 
#4       Warning: warning conditions 
#5       Notice: normal but significant condition 
#6       Informational: informational messages 
#7       Debug: debug-level messages 
#*************************************

import os
import sys
import time
import socket

class Syslog :
	#Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
	def __init__ (self, addr, facility=20, productName='cattle') :
		self.addrs = addr
		self.productName = productName
		self.facility = facility * 8

	def sendmsg(self, msg, severity=6) :
		if len(self.addrs) == 0 :
			return
		nowTime = time.strftime('%b %d %H:%M:%S %Y')
		pri = self.facility + severity
		
		#<30>Oct 10 10:33:20 2014 cattle: this is msg.
		msgs = '<%d>%s %s: %s' % (pri, nowTime, self.productName, msg)
		sck = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		for addr in self.addrs :
			try :
				sck.sendto( msgs, addr )
			except :
				pass
		sck.close()

