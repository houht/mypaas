#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2014-2099 
#
# This file is part of cattle.
#
#*************************************
#author:zhengqs
#create:201410
#desc: network service

import os
import sys

from cattle.utils import SqliteTools,CustomException,CustomExecException,CustomNotFoundException,IpUtils,UUIDUtils,Dhcp,IptablesTools
from cattle.services import ConfigManage

TABLE_DHCP = "dhcp"
TABLE_PROXYPORT = "proxyPort"
TABLE_BUSINESSPORT="businessPort"
MAC_PREFIX = "FC:FB:FE"

class NetworkService:
    '''network service'''
    
    def __init__(self):
        self.conf = ConfigManage()
        self.network_conf = self.conf.get_network_conf()
        self.db_name = self.network_conf['db_path']
        self.net_type = self.network_conf['net_type']

    #将配置生成dchp的配置文件
    def _conf2dchp(self, bridge_list):
        hdcp_subnets = {}
        for (k,v) in  bridge_list.items() :
            options = {}
            for(x,y) in v.items() :
                if x not in ['subnet','subnet-mask','static-bootp'] :
                    options[x] = y
            hdcp_subnets[k] = {'ip':v['subnet'], 'mask':v['subnet-mask'], 'options':options, 'hosts':[]}
        return hdcp_subnets;
    
    #想dhcp net中添加host
    def _addHost2dhcp(self, hdcp_subnets, groupName, ipAddress, macAddress, hostname, ifName) :
        if groupName not in hdcp_subnets :
            return
        host = {}
        if hostname in [None, ''] :
            host = {'hostname':ifName, 'options':{'hardware ethernet':macAddress,'fixed-address':ipAddress}}
        else:
            host = {'hostname':ifName, 'options':{'option host-name':hostname,'hardware ethernet':macAddress,'fixed-address':ipAddress}}
        
        if 'hosts' not in hdcp_subnets[groupName] :
            hdcp_subnets[groupName]['hosts'] = []
        hosts = hdcp_subnets[groupName]['hosts'];
        hosts.append(host)
        return
        
    
    #注册虚拟机固定IP
    def fixedIpRegister(self, groupName=None, hostName=None, ifName=None, macAddress=None, ipAddress=None):
        '''
        groupName表示网桥的名称，非必填，默认读取配置文件中的default_bridge字段的值
        hostName表示虚拟机的主机名称，非必填
        ifName 虚拟机的网口名称，非必填
        macAddress 虚拟机的网口的mac地址，非必填
        ipAddress 虚拟机的静态IP，非必填
        ifName 网口名称
        '''
        hdcp_subnets = {}
        
        if groupName in [None, ''] :
            groupName = self.network_conf['default_bridge']
        bridge_list = self.network_conf['bridge']
        #根据配置文件初始化dhcp配置
        if self.net_type == "dhcp" :
            hdcp_subnets = self._conf2dchp(bridge_list);
        
        
        #已使用ip和已经使用mac
        used_ips = []
        used_mac = []
        #读取dhcp数据表
        sql = "select ipAddress, macAddress, groupName, hostname, ifName  from %s" % TABLE_DHCP
        sql_tools = SqliteTools(self.db_name)
        item = sql_tools.fetchall(sql)

        for it in item :
            used_ips.append(IpUtils.ip2int(it[0]))
            
            macs = it[1].split(':')
            mac_int = (int(macs[3],16)<<16) + (int(macs[4],16)<<8) + (int(macs[5],16))
            used_mac.append(mac_int)
            
            if self.net_type == "dhcp" :
                #添加host到subnet中
                self._addHost2dhcp(hdcp_subnets, it[2], it[0], it[1], it[3], it[4])
        
        used_ips.sort()
        used_mac.sort()
        
        #获取IP
        if ipAddress in [None, ''] :
            #开始和结束ip
            static_bootp = bridge_list[groupName]['static-bootp']
            range = static_bootp.split()
            begin_ip = IpUtils.ip2int(range[0])
            end_ip = IpUtils.ip2int(range[1])
            
            #获取ip
            if len(used_ips) == 0 :
                ipAddress = IpUtils.int2ip(begin_ip)
            elif used_ips[len(used_ips)-1] < end_ip :
                ipAddress = IpUtils.int2ip(used_ips[len(used_ips)-1] + 1)
            else :
                for num in range(begin_ip, end_ip + 1) :
                    if num not in used_ips :
                        ipAddress = IpUtils.int2ip(num)
                        break
        #验证ip是否获得
        if ipAddress in [None, ''] :
            raise CustomNotFoundException("unable to allocate ip,no available ip, please configure the file(cattle.conf) bridge:%s[static-bootp] "%groupName)
        #网口的名称
        if ifName in [None, ''] :
            ifName = "p%s"%IpUtils.ip_remove_point(ipAddress)
        #网口mac地址 
        if macAddress in [None, ''] :
            begin_mac = 0x010101
            end_mac = 0xffffff
            select_mac = begin_mac
            if len(used_mac) == 0 :
                select_mac = begin_mac
            elif used_mac[len(used_mac)-1] < end_mac :
                select_mac = used_mac[len(used_mac)-1] + 1
            else :
                for num in range(begin_mac, end_mac + 1) :
                    if num not in used_mac :
                        select_mac = num
                        break
            macAddress = "%s:%02x:%02x:%02x" % (MAC_PREFIX, (select_mac>>16) & 0xff, (select_mac>>8) & 0xff, (select_mac>>0) & 0xff)
        
        if self.net_type == "dhcp" :
            #将新生产的ip添加到subnet中
            self._addHost2dhcp(hdcp_subnets, groupName, ipAddress, macAddress, hostName, ifName)
            hdcp_subnet_list = []
            for (k,v) in  hdcp_subnets.items():
                hdcp_subnet_list.append(v)
                            
            #写dhcp文件        
            dhcp_obj = Dhcp(self.network_conf['dhcp_conf'], self.network_conf['dhcp_service'])
            dhcp_obj.write_conf(hdcp_subnet_list, None, None)
            dhcp_obj.restart()
        elif self.net_type == "libvirt" :
            #写libvert的network
            # groupName, macAddress, ipAddress, hostName
            try :
                add_host_dhcp(groupName, macAddress, ipAddress, hostName)
            except Exception,e:
                raise CustomExecException("add host ip to libvirt network Failure,Reason:%s"%str(e))
        else :
            raise CustomException("Configuration error,net_type=%s"%self.net_type)
               
        #插入数据表
        sql = "insert into %s(id, groupName, macAddress, ipAddress, hostname, ifName) values(?,?,?,?,?,?)" % TABLE_DHCP
        tmp_hostname  = hostName
        if hostName is None:
            tmp_hostname = ''
        data = [(UUIDUtils.getId(), groupName, macAddress, ipAddress, tmp_hostname, ifName)]
        sql_tools.save(sql,data)
        return {"groupName":groupName, "ipAddress":ipAddress, "macAddress":macAddress, "hostName":hostName, "ifName":ifName}

    #删除IP地址
    def fixedIpRemove(self, groupName, ipAddress) :
        hdcp_subnets = {}
        
        bridge_list = self.network_conf['bridge']
        
        if self.net_type == "dhcp" :
            #根据配置文件初始化dhcp配置        
            hdcp_subnets = self._conf2dchp(bridge_list);
            
        #读取dhcp数据表
        sql = "select ipAddress, macAddress, groupName, hostname, ifName,id  from %s" % TABLE_DHCP
        sql_tools = SqliteTools(self.db_name)
        item = sql_tools.fetchall(sql)
        
        removeId = None
        for it in item :
            #print it[5],it[2], groupName,it[0],ipAddress
            if it[2] == groupName and it[0] == ipAddress :
                removeId = it[5]
                continue
            if self.net_type == "dhcp" :
                #添加host到subnet中
                self._addHost2dhcp(hdcp_subnets, it[2], it[0], it[1], it[3], it[4])
        
        if removeId is None:
            message = "ip is not exists. param(%s,%s)"%(groupName,ipAddress)
            raise CustomNotFoundException(message)
        
        if self.net_type == "dhcp" :
            #将新生产的ip添加到subnet中
            hdcp_subnet_list = []
            for (k,v) in  hdcp_subnets.items():
                hdcp_subnet_list.append(v)
            #写dhcp文件        
            dhcp_obj = Dhcp(self.network_conf['dhcp_conf'], self.network_conf['dhcp_service'])
            dhcp_obj.write_conf(hdcp_subnet_list, None, None)
            dhcp_obj.restart()
        elif self.net_type == "libvirt" :
            #从libvirt的network中删除
            # groupName, macAddress, ipAddress, hostName
            try :
                del_host_dhcp(groupName, macAddress, ipAddress, hostName)
            except Exception,e:
                raise CustomExecException("add host ip to libvirt network Failure,Reason:%s"%str(e))
        else :
            raise CustomException("Configuration error,net_type=%s"%self.net_type)    
        #从表中删除记录
        sql = "delete from %s where id=?" % (TABLE_DHCP)
        data = [(removeId,)]
        sql_tools.delete(sql, data)
        
        return True

    #固定IP列表
    def fixedIpList(self, groupName=None, ipAddress=None) :
        sql = "select ipAddress, macAddress, groupName, hostname, ifName,id  from %s where 1=1" % TABLE_DHCP
        
        data = ()
        cond_conf = ''
        if groupName is not None :
            cond_conf += ' and groupName=?'
            data += (groupName,)
        if ipAddress is not None :
            cond_conf += ' and ipAddress=?'
            data += (ipAddress,)
        
        sql_tools = SqliteTools(self.db_name)
        item = None
        if len(data) > 0 :
            sql += cond_conf
            item = sql_tools.fetchall(sql,data)
        else :
            item = sql_tools.fetchall(sql)
        return item
            
    #注册代理端口
    def portProxyRegister(self, ip, port, proxyIp=None, proxyPort=None,proxyType=None):
        '''
        代理端口注册：
        ip表示被代理的内部ip地址
        port表示被代理的内容port
        proxyIp表示对外的IP地址，参数为None表示使用cattle.conf中配置的agent_ip
        proxyPort表示对外的端口，参数为None表示使用cattle.conf中配置的agent_port_range中的端口随机分配一个
        '''
        #判断IP和端口是否为空
        try:
            IpUtils.ip2int(ip)
            tmpPort = int(port)
            if tmpPort < 1 and tmpPort > 65535 :
                raise CustomException('port must greater than 1 and less than 65535')
        except Exception,e:
            raise CustomException("ip can not None, ip:(%s,%s)"%(ip, port))
        
        agent_ip = self.network_conf['agent_ip']
        agent_port_range = self.network_conf['agent_port_range']
        
        sql = "select dip,dPort,tIp,tPort,id from %s where 1=1" % TABLE_PROXYPORT
        sql_tools = SqliteTools(self.db_name)
        item = sql_tools.fetchall(sql)
        
        useProxyPortList = []        
        for it in item :
            #it[0]
            useProxyPortList.append(it[1])
        useProxyPortList.sort()
        
        if proxyIp in [None, ''] :
            proxyIp = agent_ip
        
        if proxyPort in [None, ''] :
            port_range = agent_port_range.split("-")
            begin_port = int(port_range[0])
            end_port = int(port_range[1])
            
            if len(useProxyPortList) == 0 :
                proxyPort = begin_port
            elif useProxyPortList[len(useProxyPortList)-1] < end_port :
                proxyPort = useProxyPortList[len(useProxyPortList)-1] + 1
            else :
                for num in range(begin_port, end_port + 1) :
                    if num not in useProxyPortList :
                        proxyPort = num
                        break
        if proxyPort in [None, ''] :
            raise CustomNotFoundException("unable to allocate port,no available port, please configure the file(cattle.conf) agent_port_range.")
        if proxyPort in useProxyPortList and proxyIp == agent_ip :
            raise CustomException("port is proxy, proxy:(%s,%d)"%(proxyIp,int(proxyPort)))
        #将端口代理加入到iptables
        iptablesTool = IptablesTools()
        #print ip, port, proxyIp, proxyPort
        iptablesTool.add_nat(ip, port, proxyIp, proxyPort,proxyType)
        
        sql = "insert into %s(id,dip,dPort,tIp,tPort,groupName)values(?,?,?,?,?,'')" % TABLE_PROXYPORT
        data = [(UUIDUtils.getId(), proxyIp, proxyPort, ip, port)]
        sql_tools.save(sql,data)
        return {"proxyIp":proxyIp, "proxyPort":proxyPort, "ip":ip, "port":port} 
    
    #代理端口注销
    def portProxyRemove(self, ip, port, proxyIp=None, proxyPort=None,proxyType=None):       
        agent_ip = self.network_conf['agent_ip']
        if proxyIp in [None,'']:
            proxyIp = agent_ip
        
        sql = "select dip,dPort,tIp,tPort,id from %s where "%TABLE_PROXYPORT
        cond_conf = ''
        cond_conf += "tIp=? and tPort=? and dip=?"
        data = (ip,port,proxyIp)
        
        if proxyPort not in [None]:
            cond_conf += " and dPort=?"
            data +=(proxyPort,)
        sql += cond_conf
        
        #执行查询
        sql_tools = SqliteTools(self.db_name)
        item = sql_tools.fetchall(sql,data)
        if len(item) != 1:
            raise CustomNotFoundException("Not found the proxy port (ip=%s,port=%s,proxyIp=%s,proxyPort=%s) find result num=%d"%(ip,port,proxyIp,proxyPort,len(item)))
        dip,dPort,tIp,tPort,id = item[0]
        
        #将端口代理从iptables中删除
        iptablesTool = IptablesTools()
        iptablesTool.del_nat(tIp, tPort, dip, dPort,proxyType)
        
        sql = "delete from %s where id=?" % TABLE_PROXYPORT
        data = [(id,)]
        sql_tools.delete(sql, data)        
        return True
    
    #代理端口查询
    def portProxyList(self, ip=None, port=None, proxyIp=None, proxyPort=None):
        '''
        参数：
        ip 表示被代理的ip
        port 表示被代理的端口
        proxyIp 表示代理ip
        proxyPort 表示代理端口
        返回值result[][]
        result[x][id,proxyIp,proxyPort,ip,port]
        '''
        sql = "select id,dip,dPort,tIp,tPort from %s where 1=1"%TABLE_PROXYPORT
        cond_conf = ""
        data = ()
        if ip not in[None,'']:
            cond_conf +=" and tIp=?"
            data +=(ip,)
        if port != None:
            cond_conf +=" and tPort=?"
            data +=(port,)
        if proxyIp != None:
            cond_conf +=" and dip=?"
            data +=(proxyIp,)
        if proxyPort != None:
            cond_conf +=" and dPort=?"
            data +=(proxyPort,)
        sql += cond_conf
        
        sql_tools = SqliteTools(self.db_name)
        item = None
        if len(data) > 0 :
            sql += cond_conf
            item = sql_tools.fetchall(sql,data)
        else :
            item = sql_tools.fetchall(sql)
        return item
    
    #创建业务表
    def create_network_table(self):
        '''
        create sqlite table
        '''
        
        '''
            id, 主键ID uuid
            groupName,  对应的桥名称
            macAddress, 虚拟的mack地址
            ipAddress,  虚拟的静态IP
            hostname,   虚拟机主机名
            ifName      虚拟机网口的名
        '''
        create_dhcp_table_sql = '''CREATE TABLE `dhcp` (
                            `id` varchar(64) PRIMARY KEY NOT NULL,
                            `groupName` varchar(64) NOT NULL,
                            `macAddress` varchar(64) NOT NULL,
                            `ipAddress` varchar(64) NOT NULL,
                            `hostname` varchar(256) NOT NULL,
                            `ifName` varchar(64) NOT NULL
                        )'''
        '''
            id,主键ID uuid
            groupName, 对应的桥名称
            dip, 通过groupName从配置中取得，外网IP 
            dPort, 对外端口
            tIp,  虚拟机IP
            tPort 虚拟机端口
        '''
        create_proxyPort_table_sql = '''CREATE TABLE `proxyPort` (
                            `id` varchar(64) PRIMARY KEY NOT NULL,
                            `groupName` varchar(64),
                            `dip` varchar(64) NOT NULL,
                            `dPort` int,
                            `tIp` varchar(64) NOT NULL,
                            `tPort` varchar(64) NOT NULL
                        )'''
        '''
            id,主键ID uuid
            pType, 1：vnc端口，2：其它业务端口
        '''
        create_businessPort_table_sql = '''CREATE TABLE `businessPort` (
                            `id` varchar(64) PRIMARY KEY NOT NULL,
                            `pType` varchar(5) NOT NULL,
                            `dPort` int
                        )'''
                        
        network_conf = self.conf.get_network_conf()
        network_db = network_conf['db_path']
        sql_tools = SqliteTools(network_db)
        sql_tools.create_table(create_dhcp_table_sql)
        sql_tools.create_table(create_proxyPort_table_sql)
        sql_tools.create_table(create_businessPort_table_sql)
    

if __name__ == "__main__":
    networksvc = NetworkService()
    
    #networksvc.create_network_table()
    #print 'ssss---------'
    #print networksvc.fixedIpRegister()
    #print networksvc.fixedIpRemove('br1','192.168.2.31')
    #print 'ssss---------'
    if len(sys.argv) < 3:
        raise CustomException("参数不正确。")
    ip = sys.argv[1]
    port = sys.argv[2]
    proxyIp=None
    proxyPort=None
    if len(sys.argv) > 3:
        proxyIp = sys.argv[3]
    if len(sys.argv) > 4:
        proxyPort = sys.argv[4]
        
    networksvc.portProxyRegister(ip,port,proxyIp,proxyPort)
#    networksvc.portProxyRemove(ip,port,proxyIp,proxyPort)
    list =  networksvc.portProxyList()
    for it in list :
        print it,"\n"
    
    fixedList = networksvc.fixedIpList()
    for it2 in fixedList:
        print it2,"\n"