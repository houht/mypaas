#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:houht
#create:201410
#desc: 
#*************************************
from cattle.utils import LoggerUtil
from cattle.utils import UUIDUtils
from cattle.utils import JsonParser
from cattle.utils import RabbitMq


from cattle.services import VmManage
from cattle.services import AppManage, AppEnv
from cattle.services import ConfigManage

class AppBusiness:
    ""

    def __init__(self):
        ""
        self.vm = VmManage()
        self.logger = LoggerUtil().getLogger()
        
        conf = ConfigManage()
        # mq����
        mq_conf = conf.get_mq_conf()
        self.mq_addr = mq_conf['mq_addr']
        self.task_exchange = mq_conf['task_exchange']
        self.task_type = mq_conf['task_type']
        
        # ncΨһid
        cattle_conf = conf.get_cattle_conf()
        self.engine_id = cattle_conf['engineId']
        
        self.messages={}
        res = 'task_rst'
        
        # ��Դ��Ӧ
        self.messages['app_ask_can'] = 'app.deploy.can'
        self.messages['app_ask_router'] = res + '.app.deploy.can'
        
        # ����ʧ��
        self.messages['app_deploy_error'] = 'app.deploy.error'
        self.messages['app_deploy_error_router'] = res  + '.app.deploy.error'
        self.messages['app_deploy_error_code'] = 3001
        
        # ����ɹ�
        self.messages['app_deploy_ok'] = 'app.deploy.ok'
        self.messages['app_deploy_ok_router'] = res + '.app.deploy.ok'
        
        
        # ж��ʧ��
        self.messages['app_drop_error'] = 'app.drop.error'
        self.messages['app_drop_error_router'] = res  + '.app.drop.error'
        self.messages['app_drop_error_code'] = 3002
        
        # ж�سɹ�
        self.messages['app_drop_ok'] = 'app.drop.ok'
        self.messages['app_drop_ok_router'] = res + '.app.drop.ok'
        
        # ����ʧ��
        self.messages['app_start_error'] = 'app.start.error'
        self.messages['app_start_error_router'] = res  + '.app.start.error'
        self.messages['app_start_error_code'] = 3003
        
        # �����ɹ�
        self.messages['app_start_ok'] = 'app.start.ok'
        self.messages['app_start_ok_router'] = res + '.app.start.ok'
    
        # �ر�ʧ��
        self.messages['app_stop_error'] = 'app.stop.error'
        self.messages['app_stop_error_router'] = res  + '.app.stop.error'
        self.messages['app_stop_error_code'] = 3004
        
        # �رճɹ�
        self.messages['app_stop_ok'] = 'app.stop.ok'
        self.messages['app_stop_ok_router'] = res + '.app.stop.ok'
        
    
        # ����ʧ��
        self.messages['app_conf_error'] = 'app.conf.error'
        self.messages['app_conf_error_router'] = res  + '.app.conf.error'
        self.messages['app_conf_error_code'] = 3005
        
        # ���óɹ�
        self.messages['app_conf_ok'] = 'app.conf.ok'
        self.messages['app_conf_ok_router'] = res + '.app.conf.ok'
        
        
#        # ��������ʧ��
#        self.messages['app_appley_error'] = 'app.appley.error'
#        self.messages['app_appley_error_router'] = res  + '.app.appley.error'
#        self.messages['app_appley_error_code'] = 3006
#        
#        # ��������ɹ�
#        self.messages['app_appley_ok'] = 'app.deploy.ok'
#        self.messages['app_appley_ok_router'] = res + '.app.appley.ok'
#        
#        
#        # ����ж��ʧ��
#        self.messages['router_remove_error'] = 'router.app.error'
#        self.messages['router_remove_error_router'] = res  + '.router.app.error'
#        self.messages['router_remove_error_code'] = 3007
#        
#        # ����ж�سɹ�
#        self.messages['router_remove_ok'] = 'router.remove.ok'
#        self.messages['router_remove_ok_router'] = res + '.router.remove.ok'
#        
    
    # ��Դ��Ӧ����
    def app_ask(self,json_msg):
        ""
        
        
        
        
        # 1 ������Ϣ
        cpu = json_msg['content']['cpu']
        mem = json_msg['content']['mem']
        disk = json_msg['content']['disk']
        serviceId = json_msg['content']['serviceId']
       
        # 2 �жϷ����Ƿ�֧��
        appManage = AppManage()
        if not appManage.hasService(serviceId) :
            return
        
        # 3 �ж��Ƿ���Դ����
        if not self.vm.vm_resource(vcpus=cpu,memary=mem,disk=disk) :
            return
        
        
        # 3 ��Ӧ����
        response_msg = {}
        response_msg['action'] = self.messages['app_ask_can']
        response_msg['taskId'] = json_msg['taskId']
        content_msg = {}
        
        content_msg['engineId'] = self.engine_id
        response_msg['content'] = content_msg
              
        # ����
        self.send_msg(self.messages['app_ask_router'], response_msg)

    
    # Ӧ�ò���
    def app_deploy(self,json_msg):
        ""
        
        #��Ϣ����
        response_msg = {}
        response_msg['action'] = self.messages['app_deploy_ok']
        response_msg['taskId'] = json_msg['taskId']
        content_msg = {}        
        content_msg['engineId'] = self.engine_id        
        response_msg['content'] = content_msg
            
        # 1 �������
        env = AppEnv()
        try :
            #ʵ������
            serviceId = json_msg['content']['serviceId']
            instanceId = json_msg['content']['instanceId']
            
            content_msg['serviceId'] = json_msg['content']['serviceId']
            content_msg['instanceId'] = json_msg['content']['instanceId']
        
            env.set_service_env('serviceId', serviceId)
            env.set_service_env('instanceId', instanceId)
            
            #���⻯����
            cpu = json_msg['content']['cpu']
            mem = json_msg['content']['mem']
            disk = json_msg['content']['disk']
            
            env.set_vm_env('cpu', int(cpu))
            env.set_vm_env('mem', int(mem))
            env.set_vm_env('disk', int(disk))
            hostname = UUIDUtils.getId()
            env.set_vm_env('hostname', hostname)
            env.set_vm_env('name', instanceId)
            
            
            #ע�Ḻ�ؾ������
            if json_msg['content'].has_key('listenPort'):
                listenPort = json_msg['content']['listenPort']
                env.set_router_env('listenPort', listenPort)
            
            if json_msg['content'].has_key('domain'):
                domain = json_msg['content']['domain']
                env.set_router_env('domain', domain)
                            
            #Ӧ�ó������
            if json_msg['content'].has_key('appName') :
                appName = json_msg['content']['appName']
                env.set_app_env('appName', appName)
            
            if json_msg['content'].has_key('filename') :
                filename = json_msg['content']['filename']
                env.set_app_env('filename', filename)
            
            env.set_app_env('appfile', '/tmp/wwwroot.tar.gz')
            
            #��������
            system_env = None
            user_env = None
            pre_param = None
            if json_msg['content'].has_key('param') :
                param = json_msg['content']['param']
                
                env.set_app_env('param',str(param))
                
                if param.has_key('env') :
                    system_env = param['env']
                    env.set_app_env('system_env',system_env)
                    
                if param.has_key('userEnv') :
                    user_env = param['userEnv']
                    env.set_app_env('user_env',user_env)
                if param.has_key('preParam') :
                    pre_param = param['preParam']
                    env.set_app_env('pre_param',pre_param)
        
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_deploy_error']
            content_msg['errorCode'] = self.messages['app_deploy_error_code']
            content_msg['errorMessage'] = 'parse param error: '+ str(ex)
            self.send_msg(self.messages['app_deploy_error_router'], response_msg)
            return
            
        # 2 ����
        try :
            appManage = AppManage()
            
            appManage.app_deploy(env)
            res_param =  env.get_global_env('returnParam')
            if res_param :
                content_msg['param'] = res_param
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_deploy_error']
            content_msg['errorCode'] = self.messages['app_deploy_error_code']
            content_msg['errorMessage'] = 'app deploy error: ' + str(ex)
            self.send_msg(self.messages['app_deploy_error_router'], response_msg)
            return
            
            
        # 3 ���ͳɹ���Ϣ        
        self.send_msg(self.messages['app_deploy_ok_router'], response_msg)
   
    # ��������
    def app_router(self,json_msg):
        ""
        
        pass
    
    
    # ����ɾ��
    def app_router_remove(self,json_msg):
        ""
        
        pass
        
    
    # Ӧ��ɾ��
    def app_drop(self,json_msg):
        ""
        #��Ϣ����
        response_msg = {}
        response_msg['action'] = self.messages['app_drop_ok']
        response_msg['taskId'] = json_msg['taskId']
        content_msg = {}        
        content_msg['engineId'] = self.engine_id        
        response_msg['content'] = content_msg
        
            
        # 1 �������
        env = AppEnv()
        try :
            #���⻯����
            instanceId = json_msg['content']['instanceId']
            content_msg['instanceId'] = instanceId
            
            env.set_service_env('instanceId', instanceId)
            
            #ע�Ḻ�ؾ������
            if json_msg['content'].has_key('listenPort'):
                listenPort = json_msg['content']['listenPort']
                env.set_router_env('listenPort', listenPort)
            
            if json_msg['content'].has_key('domain'):
                domain = json_msg['content']['domain']
                env.set_router_env('domain', domain)           
            
            
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_drop_error']
            content_msg['errorCode'] = self.messages['app_drop_error_code']
            content_msg['errorMessage'] = 'parse param error: '+ str(ex)
            self.send_msg(self.messages['app_drop_error_router'], response_msg)
            return    
        #instanceId
        
        # 2 ж��
        try :
            appManage = AppManage()
            
            appManage.app_drop(env)
            res_param =  env.get_global_env('returnParam')
            if res_param :
                content_msg['param'] = res_param
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_drop_error']
            content_msg['errorCode'] = self.messages['app_drop_error_code']
            content_msg['errorMessage'] = 'app drop error: ' + str(ex)
            self.send_msg(self.messages['app_drop_error_router'], response_msg)
            return
                        
        # 3 ���ͳɹ���Ϣ        
        self.send_msg(self.messages['app_drop_ok_router'], response_msg)
    
    
    # Ӧ������
    def app_start(self,json_msg):
        ""
        
        #��Ϣ����
        response_msg = {}
        response_msg['action'] = self.messages['app_start_ok']
        response_msg['taskId'] = json_msg['taskId']
        content_msg = {}        
        content_msg['engineId'] = self.engine_id        
        response_msg['content'] = content_msg
        
            
        # 1 �������
        env = AppEnv()
        try :
            #���⻯����
            instanceId = json_msg['content']['instanceId']
            content_msg['instanceId'] = instanceId
            
            env.set_service_env('instanceId', instanceId)
            
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_start_error']
            content_msg['errorCode'] = self.messages['app_start_error_code']
            content_msg['errorMessage'] = 'parse param error: '+ str(ex)
            self.send_msg(self.messages['app_start_error_router'], response_msg)
            return    
        
        # 2 ����
        try :
            appManage = AppManage()
            
            appManage.app_start(env)
            res_param =  env.get_global_env('returnParam')
            if res_param :
                content_msg['param'] = res_param
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_start_error']
            content_msg['errorCode'] = self.messages['app_start_error_code']
            content_msg['errorMessage'] = 'app start error: ' + str(ex)
            self.send_msg(self.messages['app_start_error_router'], response_msg)
            return
                        
        # 3 ���ͳɹ���Ϣ        
        self.send_msg(self.messages['app_start_ok_router'], response_msg)
    
    
    # Ӧ��ֹͣ
    def app_stop(self,json_msg):
        ""
        #��Ϣ����
        response_msg = {}
        response_msg['action'] = self.messages['app_stop_ok']
        response_msg['taskId'] = json_msg['taskId']
        content_msg = {}        
        content_msg['engineId'] = self.engine_id        
        response_msg['content'] = content_msg
        
            
        # 1 �������
        env = AppEnv()
        try :
            #���⻯����
            instanceId = json_msg['content']['instanceId']
            content_msg['instanceId'] = instanceId
            
            env.set_service_env('instanceId', instanceId)
            
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_stop_error']
            content_msg['errorCode'] = self.messages['app_stop_error_code']
            content_msg['errorMessage'] = 'parse param error: '+ str(ex)
            self.send_msg(self.messages['app_stop_error_router'], response_msg)
            return    
        
        # 2 �ر�
        try :
            appManage = AppManage()
            
            appManage.app_stop(env)
            res_param =  env.get_global_env('returnParam')
            if res_param :
                content_msg['param'] = res_param
        except Exception ,ex:
            # ����
            response_msg['action'] = self.messages['app_stop_error']
            content_msg['errorCode'] = self.messages['app_stop_error_code']
            content_msg['errorMessage'] = 'app stop error: ' + str(ex)
            self.send_msg(self.messages['app_stop_error_router'], response_msg)
            return
                        
        # 3 ���ͳɹ���Ϣ
        self.send_msg(self.messages['app_stop_ok_router'], response_msg)
    
    
    
    # ����mq��Ϣ 
    def send_msg(self,routing_key,message):
        ""

        self.logger.info(str(message))
        js = JsonParser()
        message = js.encode(message)
        
        mq = RabbitMq(self.mq_addr)
        mq.exchange_declare(exchange_name=self.task_exchange,mq_type=self.task_type)
        mq.mq_send(msg=message,exchange_name=self.task_exchange,routing_key=routing_key)
        mq.mq_close()