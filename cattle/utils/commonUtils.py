#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zqs
#create:201410
#desc: 
#*************************************
import socket
import struct
import uuid
class IpUtils:
    
    def __init__(self) :
        pass

    @staticmethod
    def ip2int(ip) :
        return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0])
    
    @staticmethod
    def int2ip(int_ip) :
        return socket.inet_ntoa(struct.pack('I',socket.htonl(int_ip)))
    
    @staticmethod
    def ip_remove_point(ipAddress) :
        int_ip = socket.ntohl(struct.unpack("I",socket.inet_aton(str(ipAddress)))[0])
        return '%03d%03d%03d%03d'% ((int_ip>>24)&0xff, (int_ip>>16)&0xff, (int_ip>>8)&0xff, (int_ip>>0)&0xff)
        
class UUIDUtils:

    def __init__(self) :
        pass
    
    @staticmethod
    def getId() :
        return str(uuid.uuid1()).replace("-","")
