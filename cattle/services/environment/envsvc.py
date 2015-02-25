#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2014-2099 
#
# This file is part of cattle.
#
#*************************************
#author:zhengqs
#create:201410
#desc: environment service
from cattle.utils import SystemStat, SystemInfo
import time

class SystemService:
    def __init__(self):
        self.cpu = {}
        self.cpu['stat'] = None
        self.cpu['time'] = None
        self.cpu['interval'] = 5

    #获取系统信息
    def systemInfo(self):
        '''
        system:系统名称,node:主机名,release:系统发行版本,version：版本,machine:系统架构,processor:cpu架构,runTime:开机时长(float),freeRate:空置率
        '''
        info = SystemInfo.uname()
        runInfo = SystemStat.uptime_stat()
        info['runTime']= runInfo['runTime']
        info['freeRate'] = runInfo['freeRate']
        return info

    #获取物理cpu信息列表
    def cpuinfoList(self):
        '''
        processor：核序号，physical id物理cpu序号，cpu MHz主频，model name型号
        '''
        cpuList = SystemStat.cpuinfo_stat()
        return cpuList

    #获取系统的性能，cpu使用率，内存使用率
    def systemPerformance(self):
        '''
        MemTotal:内存总数,MemUsed:已使用,MemUsedPerc:已使用百分比,CpuUsedPerc:cpu使用百分比
        '''
        mem = SystemStat.memory_stat()
        if self.cpu['stat'] == None :
            self.cpu['stat'] = SystemStat.cpu_stat()
            self.cpu['time'] = time.time()
            time.sleep(0.2)
        if time.time() - self.cpu['time'] > self.cpu['interval'] :
            self.cpu['stat'] = SystemStat.cpu_stat()
            self.cpu['time'] = time.time()
        
        cpu2 = SystemStat.cpu_stat()
        cpuUsedPerc = SystemStat.cpu_rate(self.cpu['stat'], cpu2)
        
        info = {}
        info['MemTotal'] = mem['MemTotal']
        info['MemUsed'] = mem['MemUsed']
        info['MemUsedPerc'] = mem['MemUsedPerc']
        info['CpuUsedPerc'] = cpuUsedPerc
        return info

    #获取cpu的负载
    def systemCpuLoadavg(self):
        '''
        lavg_1:1分钟内的平均进程数、lavg_5:5、lavg_15:15,nr:正在运行的进程/总进程数, last_pid:分钟内的平均进程数,
        '''
        return SystemStat.load_stat()

    #获取磁盘信息
    def systemDiskList(self):
        '''
        df -h出来的内容
        disk['name'] 盘符
        disk['totalSize'] 磁盘总容量
        disk['usedSize'] 已使用
        disk['unusedSize'] 未审批
        disk['usedRate'] 已使用百分比
        disk['mount'] 挂载点
        '''
        return SystemStat.disk_stat()

    #获取内存信息
    def systemMem(self):
        '''
        mem['MemTotal'] 内存总数 kB 
        mem['MemUsed'] 已使用总数 kB
        mem['MemFree'] 空闲
        mem['Buffers'] 缓存
        mem['Cached'] cache
        mem['MemUsedPerc'] 已使用百分比
        '''
        return SystemStat.memory_stat()

    #获取网络信息
    def systemNetList(self):
        '''
        interface表示网口,ReceiveBytes表示收的字节数,ReceivePackets表示收的包数,ReceiveErrs表示接收的错误包数,ReceiveDrop表示收丢弃的包量
        '''
        return SystemStat.net_stat()

    #获取网网卡流量
    def systemNetInterface(self,ifname=None):
        '''
        每秒流量位pbs(每秒比特数),此函数会耗时一秒钟
        '''
        return SystemStat.net_rate(ifname);
