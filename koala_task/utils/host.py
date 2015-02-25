#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201410
#desc: sysmonitor util

import os
import platform
import time

class SystemStat :
    #cpu统计信息,processor：核序号，physical id物理cpu序号，cpu MHz主频，model name型号
    @staticmethod
    def cpuinfo_stat():
        cpu = []
        cpuinfo = {}
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        f.close()
        
        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2: continue
            name = line.split(':')[0].rstrip()
            var = line.split(':')[1]
            cpuinfo[name] = var
        return cpu

    #cpu负载统计
    @staticmethod
    def load_stat():
        loadavg = {}
        f = open("/proc/loadavg")
        con = f.read().split()
        f.close()
        #1、5、15分钟内的平均进程数
        loadavg['lavg_1']=con[0]
        loadavg['lavg_5']=con[1]
        loadavg['lavg_15']=con[2]
        #正在运行的进程/总进程数
        loadavg['nr']=con[3]
        #最后一次运行的进程ID
        loadavg['last_pid']=con[4]
        return loadavg

    #时间统计,运行时间day，hour，minute，second，空闲率freeRate
    @staticmethod
    def uptime_stat():
        uptime = {}
        f = open("/proc/uptime")
        con = f.read().split()
        f.close()

        all_sec = float(con[0])
        MINUTE,HOUR,DAY = 60,3600,86400
        uptime['day'] = int(all_sec / DAY )
        uptime['hour'] = int((all_sec % DAY) / HOUR)
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)
        uptime['second'] = int(all_sec % MINUTE)
        uptime['runTime'] = all_sec
        #uptime['Free rate'] = float(con[1]) / float(con[0])
        
        cpus = os.popen('cat /proc/cpuinfo |grep processor|wc -l','r').readlines()
        uptime['freeRate'] = float(con[1])*100 / ((float(con[0]))*float(cpus[0]))

        return uptime

    #网络流量统计
    @staticmethod
    def net_stat():
        net = []
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()

        for line in lines[2:]:
            con = line.split()
            con_ary=[]
            frist = con[0].split(':')
            if(len(con)==16):                
                con_ary=[frist[0],int(frist[1]),int(con[1]),
                      int(con[2]),int(con[3]),int(con[4]),
                      int(con[5]),int(con[6]),int(con[7]),
                      int(con[8]),int(con[9]),int(con[10]),
                      int(con[11]),int(con[12]),int(con[13]),
                      int(con[14]),int(con[15])]                      
            else:
                con_ary=[frist[0],int(con[1]),int(con[2]),
                      int(con[3]),int(con[4]),int(con[5]),
                      int(con[6]),int(con[7]),int(con[8]),
                      int(con[9]),int(con[10]),int(con[11]),
                      int(con[12]),int(con[13]),int(con[14]),
                      int(con[15]),int(con[16])]    
            
            """
            intf = {}
            intf['interface'] = con[0].lstrip(":")
            intf['ReceiveBytes'] = int(con[1])
            intf['ReceivePackets'] = int(con[2])
            intf['ReceiveErrs'] = int(con[3])
            intf['ReceiveDrop'] = int(con[4])
            intf['ReceiveFifo'] = int(con[5])
            intf['ReceiveFrames'] = int(con[6])
            intf['ReceiveCompressed'] = int(con[7])
            intf['ReceiveMulticast'] = int(con[8])
            intf['TransmitBytes'] = int(con[9])
            intf['TransmitPackets'] = int(con[10])
            intf['TransmitErrs'] = int(con[11])
            intf['TransmitDrop'] = int(con[12])
            intf['TransmitFifo'] = int(con[13])
            intf['TransmitFrames'] = int(con[14])
            intf['TransmitCompressed'] = int(con[15])
            intf['TransmitMulticast'] = int(con[16])
            """
            #ReceiveBytes表示收的字节数,ReceivePackets表示收的包数,ReceiveErrs表示接收的错误包数,ReceiveDrop表示收丢弃的包量
            intf = dict(
                zip(
                    ('interface','ReceiveBytes','ReceivePackets',
                     'ReceiveErrs','ReceiveDrop','ReceiveFifo',
                     'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',
                     'TransmitBytes','TransmitPackets','TransmitErrs',
                     'TransmitDrop', 'TransmitFifo','TransmitFrames',
                     'TransmitCompressed','TransmitMulticast' ),
                    con_ary
                )
            )
            net.append(intf)
        return net

    #磁盘使用情况
    @staticmethod
    def disk_stat(): 
    	lines = os.popen('df -h','r').readlines()
    	disks = []
        for line in lines[1:]:
            con = line.split()
            disk = {}
            """
            disk['name'] 盘符
            disk['totalSize'] 磁盘总容量
            disk['usedSize'] 已使用
            disk['unusedSize'] 未审批
            disk['usedRate'] 已使用百分比
            disk['mount'] 挂载点
            """
            disk = dict(
                zip(
                    ('name','totalSize','usedSize',
                     'unusedSize','usedRate','mount'),
                    ( con[0],con[1],con[2],con[3],con[4])
                )
            )
            disks.append(disk)
        return disks
        
    #内存使用统计
    @staticmethod
    def memory_stat():
        mem = {}
        f = open("/proc/meminfo")
        lines = f.readlines()
        f.close()
        
        for line in lines:
            if len(line) < 2: continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = long(var) * 1024.0
        mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
        mem['MemUsedPerc'] = (100 * mem['MemUsed'])/mem['MemTotal']
        return mem
    
    #cpu运行状态统计
    @staticmethod
    def cpu_stat(cpu_name=None):
        cpus = []
        f = open("/proc/stat")
        lines = f.readlines()
        f.close()
        
        for line in lines:
            if 'cpu' not in line:
                continue
            
            cpu = {}
            con = line.split()
            if len(con)==8:
                cpu = dict(
                    zip(
                        ('cpu','user','nice','sys','idle','iowait','irq','softirq','stealstolen','guest'),
                        ( con[0],long(con[1]),long(con[2]),long(con[3]),long(con[4]),long(con[5]),long(con[6]),long(con[7]),long(0),long(0))
                    )
                )
            else:
                cpu = dict(
                    zip(
                        ('cpu','user','nice','sys','idle','iowait','irq','softirq','stealstolen','guest'),
                        ( con[0],long(con[1]),long(con[2]),long(con[3]),long(con[4]),long(con[5]),long(con[6]),long(con[7]),long(con[8]),long(con[9]))
                    )
                )
            if cpu_name not in (None, '') and cpu_name == cpu['cpu']:
                return cpu
            cpus.append(cpu)
        return cpus

    #cpu使用率cpu1是第一次读取的cpu信息，cpu2是第二次读取的cpu信息
    @staticmethod
    def cpu_rate(cpu1, cpu2):
        if len(cpu1) != 10:
            return -1
        dlta_user_cpu = cpu2['user'] - cpu1['user']
        dlta_nice_cpu = cpu2['nice'] - cpu1['nice']
        dlta_sys_cpu = cpu2['sys'] - cpu1['sys']
        dlta_idle_cpu = cpu2['idle'] - cpu1['idle']
        dlta_iowait_cpu = cpu2['iowait'] - cpu1['iowait']
        dlta_irq_cpu = cpu2['irq'] - cpu1['irq']
        dlta_softirq_cpu = cpu2['softirq'] - cpu1['softirq']
        dlta_stealstolen_cpu = cpu2['stealstolen'] - cpu1['stealstolen']
        dlta_guest_cpu = cpu2['guest'] - cpu1['guest']
        sum = dlta_user_cpu + dlta_nice_cpu + dlta_sys_cpu + dlta_idle_cpu + dlta_iowait_cpu + dlta_irq_cpu + dlta_softirq_cpu + dlta_stealstolen_cpu + dlta_guest_cpu
        cpu_now_used = float(sum - dlta_idle_cpu)*100/float(sum)
        return cpu_now_used

    #网卡流量
    @classmethod 
    def net_rate(cls, ifname=None):
        net1 = cls.net_stat()
        time.sleep(1)
        net2 = cls.net_stat()
        size = len(net1)
        netsRate = []
        for i in range(0,size):
            netRate = {}
            netRate['interface'] = net2[i]['interface']
            netRate['rate'] = ((net2[i]['ReceiveBytes'] - net1[i]['ReceiveBytes']) + (net2[i]['TransmitBytes'] - net1[i]['TransmitBytes'])) * 8
            if ifname not in (None, '') and ifname == netRate['interface']:
                return netRate
            netsRate.append(netRate)
        return netsRate

    def __init__ (self):
        pass

class SystemInfo :
    def __init__ (self) :
        pass
    
    #读取主机信息
    @staticmethod
    def uname():
    	uname_ary = platform.uname()
    	uname = {}
    	uname = dict(
            zip(
                ('system','node','release',
                 'version','machine','processor'),
                uname_ary
            )
        )
        return uname
    
    #读取指定网口信息
    @staticmethod
    def networkinfo(ifname):
        network = {}
        cmd = "/sbin/ifconfig %s 2>&1" % ifname
        for line in os.popen(cmd,'r'):
            if 'inet addr:' in line:
                network['ip'] = line.split()[1].split(':')[1]
            elif 'UP BROADCAST' in line:
                network['status'] = line.split()[2]
            elif 'UP LOOPBACK' in line:
                network['status'] = line.split()[2]
            elif 'HWaddr' in line:
                network['mac'] = line.split()[4]
            elif 'BROADCAST MULTICAST' in line:
                network['status'] = 'STOPED'
            elif 'RX packets' in line:
                network['rxPackets'] = long(line.split()[1].split(':')[1])
            elif 'TX packets' in line:
                network['txPackets'] = long(line.split()[1].split(':')[1])
            elif 'RX bytes' in line:
                network['rxbytes'] = long(line.split()[1].split(':')[1])
                network['txbytes'] = long(line.split()[5].split(':')[1])
        return network
