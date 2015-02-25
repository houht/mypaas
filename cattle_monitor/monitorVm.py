#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201412
#desc: 
#*************************************

import os
import time


from cattle.utils.libvirtVm import vm_netstats,vm_diskstats,vm_state,get_nics
from cattle.utils import JsonParser
from cattle.utils import LoggerUtil
from cattle.utils import RabbitMq
from cattle.utils import SystemStat

from cattle.services import ConfigManage
from cattle.services import VmManage
from cattle.services import AppManage



class MonitorVm() :
    "monitor vm"    
    
    
    def __init__(self) :
        ""
        
        # log
        self.logger = LoggerUtil().getLogger()
        
        
        # config
        conf = ConfigManage()
        mq_conf = conf.get_mq_conf()
        self.mq_addr = mq_conf['mq_addr']
        self.monitor_exchange = mq_conf['monitor_exchange']
        self.monitor_type = mq_conf['monitor_type']
        
        # �ɼ�ʱ��
        app_conf = conf.get_app_conf()
        self.collect = app_conf['collect']
        
        # vm
        self.vm = VmManage()
        
        # app
        self.app = AppManage()
        
        # infos ��Ϣ
        self.infos = []
    
    
    # ��ѯvm��Ϣ
    def vm_info(self,vms=None):
        ""
        
        infos = []
        
        # ���û��vm��Ĭ�ϲ�ѯ���е�vm��Ϣ
        if vms == None:
            vms = []
            vm_infos = self.vm.info_vms()
            for vm in vm_infos:
                vms.append(vm['vm_name'].encode('iso8859-1'))
        
        # ��ѯapp��Ϣ
        app_info = {}
        app_infos = self.app.app_info()
        for app in app_infos:
            app_info[app['vmName'].encode('iso8859-1')] = app['instanceId'].encode('iso8859-1')
        
        
        # ��ѯ����vm top ��Ϣ
        tops = {} 
        vm_info = os.popen("virt-top -b -n 2 -d 0.5 --stream  2>/dev/null").read()
        num = 0
        for tmp in vm_info.split("\n"):
            if tmp == "":
                continue
            top = tmp.split()
            if top[0] == "virt-top":
                num += 1
            if top[0] == "virt-top" or top[0] == "ID":
                continue
            if num == 2:
                temp = {}
                cpu = top[6]
                mem = top[7]
                temp['cpuRate'] = cpu
                temp['memRate'] = mem
                tops[top[9]] = temp
        
        # ��������
        net_tmp = SystemStat.net_rate()
        net_rate = {}
        for rate in net_tmp:
            net_rate[rate['interface']] = rate['rate']
        
        
        # ѭ����ѯvm��Ϣ
        for vmName in vms:
            
            info = {}
            
            # 1 vm name
            info['vmName'] = vmName
        
            # 2 vm stat
            state = vm_state(vmName)[vmName]
            info['vmState'] = state
            
            # 8 time
            info['eventTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            
            # 3 instanceId
            if vmName in  app_info:
                info['instanceId'] = app_info[vmName]
            
            
            # �ݲ�����
            # 4 disk info
#            disk_info = os.popen('virt-df  -d  %s 2>/dev/null'%vmName).read()
#            diskInfo = []
#            for tmp in disk_info.split("\n"):
#                lis = {}
#                if(tmp != ""):
#                    disk = tmp.split()
#                    if(disk[0] == "Filesystem"):
#                        continue
#                content = {}
#    
#                content['used'] = disk[2]
#                content['available'] = disk[3]
#                content['rate'] = disk[4]
#                diskName = disk[0].split(":")[1]
#                lis[diskName] = content
#                diskInfo.append(lis) 
#            info['diskInfo'] = diskInfo

            # �ж��Ƿ�����
            if state != 'running':
               infos.append(info)
               continue
            
            # 5 net stat 
            
            # ��һ�ַ���
            #info['netStats'] = vm_netstats(vmName)[vmName]
            # �ڶ��ַ���
            netStats = []
            # ���á� virsh  domiflist test ������ ��virsh domifstat  test   port22106����ȡ 
            nics = get_nics(vmName)
            for mac, attrs in nics.items():
                tmp = {}
                if 'target' in attrs:
                    dev = attrs['target']
                    if dev in net_rate:
                        tmp['interface'] = dev.encode('iso8859-1')
                        tmp['flow'] = net_rate[dev]
                        netStats.append(tmp)
            info['netStats'] = netStats
             
            # 6 disk stat
            info['diskStats'] = vm_diskstats(vmName)[vmName]
            
            
            # 7 cpu  mem
            if vmName in tops:
                info['cpuRate'] = tops[vmName]['cpuRate']
                info['memRate'] = tops[vmName]['memRate']
            

            
            infos.append(info)
            
        
        self.infos = infos
 
    
    # ���е�����
    def monitor(self):
        ""
        
        # ��ʱ����
        while True :       
            try :
                self.vm_info()  
            except Exception,ex :
                self.logger.error('MonitorVm error,msg:%s' % str(ex))
            
            time.sleep(int(self.collect))
        
    
    
    # ������Ϣ
    def send_msg(self):
        ""
        
        routing_key = 'mon_rst.vm.monitor.stat'
        
        message = self.infos
        
        self.logger.debug(str(message))
        js = JsonParser()
        message = js.encode(message)
        
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.monitor_exchange,mq_type=self.monitor_type)
        mq.mq_send(msg=message,exchange_name=self.monitor_exchange,routing_key=routing_key)
        mq.mq_close()

        

if __name__ == "__main__":
    
    print "start"
    
    aa = MonitorVm()
    
    bb = ['test_0004','test_0003','wintest03']

#    aa.monitor()
    
#    aa.vm_info()
#    print aa.infos
    
    #aa.send_msg()
    
    
    print "end"
