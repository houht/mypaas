#!/usr/bin/python
# -*- coding: UTF-8 -*-


from cattle.utils import RabbitMq




#测试一 发送 fanout
aa = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
aa.exchange_declare(exchange_name='bdct_exc',mq_type='fanout')

message = '''{
 "action":"bdct.vm.create.ask",
 "taskId":"1111111111111",
 "content":{
   "vmType":"kvm",
   "cpu":2,
   "mem":1024,
   "disk":1024}}'''
  

aa.mq_send(msg=message,exchange_name='bdct_exc',routing_key="bdct.vm.create.ask")
aa.mq_close()




## 测试一 发送 fanout
#aa = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
#aa.exchange_declare(exchange_name='task_exc',mq_type='topic')
#
#message = '''{
# "action":"bdct.app.deploy.ask",
# "taskId":"3333333",
# "content":{   
#   "cpu":2,
#   "mem":1024,
#   "disk":2000,
#   "serviceId":"tomcat7"   
#}
#}
#'''
#
#
#
#message = '''
#
#{"action": "app.deploy.ask", "content": {"mem": 1024, "serviceId": "iis2003", "disk": 500, "cpu": 1}, "taskId": "f29d1120873011e4aaa5fe5400e41488"}
#
#
#'''
#
#message = '''
#
#{"action": "app.deploy.ok", "content": {"instanceId": "0db731b4872411e4ac9cfe5400e41488", "serviceId": "iis2003", "engineId": "ASDFGFGGHHJKLIO", "param": {"ip": "10.16.123.253", "domain": "6f79010c874c11e48badfe5400e41488", "serviceType": "1", "port": "8016"}}, "taskId": "6f724b64874c11e4933ffe5400e41488"}
#
#'''
#
#
#aa.mq_send(msg=message,exchange_name='task_exc',routing_key="task_rst.app.deploy.ok")
#aa.mq_close()


#测试二 创建 topic
#message = """
#{
# "action":"vm.create.apply",
# "taskId":"2222222222222",
# "content":{
#   "vmType":"kvm",
#   "vmName":"test_0004",
#   "hostName":"test_0004",
#   "cpu":2,
#   "mem":1024,
#   "disk": 2000,
#   "attachDisks":[{ "hardpoints":"vdb","size":200}
#          ],
#   "imageId":"0F7620DDF32543A097372F11C5B8877F"
#  }
#}
#"""
#
#
#bb = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
#bb.exchange_declare(exchange_name='task_exc',mq_type='topic')
#bb.mq_send(msg=message,exchange_name='task_exc',routing_key="ASDFGFGGHHJKLIO.vm.create.apply")
#bb.mq_close()


# 测试三 启动
#message = """
#{
# "action":"vm.start.apply",
# "taskId":"123454321",
# "content":{
#   "vmName":"test_0002"
#}
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.start.apply"
##
## 测试四 关闭电源
#message = """
#{
# "action":"vm.destroy.apply",
# "taskId":"123454321",
# "content":{
#   "vmName":"kvmtest_0011"
#}
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.destroy.apply"
#

## 测试五 软关机
#message = """
#{
# "action":"vm.shutdown.apply",
# "taskId":"123454321",
# "content":{
#   "vmName":"test_0001"
#}
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.shutdown.apply"
#
## 测试六 暂停
#message = """
#{
# "action":"vm.suspend.apply",
# "taskId":"123454321",
# "content":{
#   "vmName":"test_0001"
#}
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.suspend.apply"
#
## 测试七 反暂停
#message = """
#{
# "action":"vm.resume.apply",
# "taskId":"123454321",
# "content":{
#   "vmName":"test_0001"
#}
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.resume.apply"
#
#
## 测试八 配置修改
#
#message = """
#
#{
# "action":"vm.conf.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"test_0001",
#       "hostName":"fffffff",
#       "cpu":3,
#       "mem":2024,
#       "attachDisks":[{ "hardpoints":"vde","size":500}]
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.conf.apply"
#
#
#
## 测试九 添加硬盘
#
#message = """
#
#{
# "action":"vm.disk.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"test_0001",
#       "hardpoints":"vdh",
#       "size":50
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.disk.apply"
#
#
## 测试十 删除
#
#message = """
#
#{
# "action":"vm.drop.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"test_0002"
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.drop.apply"


#
# 测试十一，代理端口
#message = """
#
#{
# "action":"network.portproxy.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"test_0003",
#       "port":8080,
#       "ip":"192.168.2.62"
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.network.portproxy.apply"
#


# 测试十二，代理端口删除
#message = """
#
#{
# "action":"network.dropportproxy.apply",
# "taskId":"45678321",
#      "content":{
#       "vmName":"test_0004",
#       "port":22,
#       "ip":"192.168.2.90"
#    
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.network.dropportproxy.apply"

## 测试十三，代理端口查询
#message = """
#
#{
# "action":"network.findportproxy.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"kvmtest_001"
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.network.findportproxy.apply"
#
##



# 测试十四，vm查询
#message = """
#
#{
# "action":"vm.find.apply",
# "taskId":"45678321",
#     "content":{
#       "vmName":"kvmtest_001"
#    }
#}
#
#"""
#router = "ASDFGFGGHHJKLIO.vm.find.apply"



#测试十五，应用安装

#message = """
#{
# "action":"bdct.app.deploy.apply",
# "taskId":"444444444",
# "content":{   
#   
#   "cpu":2,
#   "mem":2024,
#   "disk": 300,
#   
#   
#   "serviceId":"iis2003",
#   "instanceId":"1000000001",
#   "appName":"iis2003",
#   "listenPort":444,
#   "domain":"www.444.com",
#   "filename":"test.war",
#    
#    "param":{
#        "env":"[{'host':'aaa','ip':'1.1.1.1'}]",
#        "userEnv":"",
#        "instanceParam":{},
#        "preParam":{}
#        }
#}
#}
#"""
#router = "ASDFGFGGHHJKLIO.app.deploy.apply"
#
#
##测试十六，应用启动 start stop drop
#
#message = """
#{
# "action":"bdct.app.start.apply",
# "taskId":"11111111444",
# "content":{   
#   "instanceId":"1000000001"
# }
#}
#"""
#router = "ASDFGFGGHHJKLIO.app.start.apply"
#
#
#bb = RabbitMq('amqp://paas:paas_4R5T3E@10.16.123.136:5672/paas_vhost')
#bb.exchange_declare(exchange_name='task_exc',mq_type='topic')
#bb.mq_send(msg=message,exchange_name='task_exc',routing_key=router)
#bb.mq_close()

