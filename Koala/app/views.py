#!/usr/bin/python
# -*- coding: UTF-8 -*-


from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.models import Appinfo,instanceinfo
from app.serializers import AppinfoSerializer,InstanceinfoSerializer
from app.libs.action import Action
from app.libs.check import Check

from django.http import Http404


# app查询
class AppList(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    
    # 查询
    def get(self, request, format=None):
        
#        print request.session['_auth_user_id']
#        print request.session.session_key
#        print request.user
#        print request.COOKIES
#
#        print request.method 
#        
#        print permissions.SAFE_METHODS
#        
#        print request.user.is_authenticated()
        
        appinfo = Appinfo.objects.all()
        serializer = AppinfoSerializer(appinfo, many=True)
        return Response(serializer.data)
        
    # 增加
    def post(self, request, format=None):
        
        
        content =  request.DATA
        
        # 1 参数是否合法，任务是否已经提交
        Check(content)
        # 2 任务处理
        Action(content)
        # 3 返回
        message = {}
        message['status'] = "success"
        message['code'] = "200"
        message['data'] = content

        return Response(message)



class AppDetail(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    
    
    
    def get_object(self, appId):
        try:
            return Appinfo.objects.get(appId=appId)
        except Appinfo.DoesNotExist:
            raise Http404
    
    
    # 查询
    def get(self, request, appId, format=None):
        appInfo = self.get_object(appId)
        serializer = AppinfoSerializer(appInfo)
        return Response(serializer.data)
    
    
    # 更新 启动 关闭
    def put(self, request, appId, format=None):
        
        content =  request.DATA
        
        content['appId'] = appId
        # 1 参数是否合法，任务是否已经提交
        Check(content)
        # 2 任务处理
        Action(content)
        # 3 返回
        message = {}
        message['status'] = "success"
        message['code'] = "200"
        message['data'] = content

        return Response(message)
        
    
    # 删除
    def delete(self, request, appId, format=None):
        
        appInfo = self.get_object(appId)
        
        return Response({"action":"delete","appId":appId})
        


####################################################################


#实例查询
class InstanceList(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)
    
    
    def get_object(self, app):
        try:
            return instanceinfo.objects.filter(app=app)
        except Appinfo.DoesNotExist:
            raise Http404
    
    
    def get(self, request,appId, format=None):
        instanceinfo = self.get_object(appId)
        serializer = InstanceinfoSerializer(instanceinfo,many=True)
        return Response(serializer.data)


class InstanceDetail(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    
    def get_object(self,appId ,instanceId):
        try:
            return instanceinfo.objects.get(app=appId,instanceId=instanceId)
        except Appinfo.DoesNotExist:
            raise Http404
            
    
    def get(self, request,appId,instanceId, format=None):
        
        instanceinfo = self.get_object(appId,instanceId)
        serializer = InstanceinfoSerializer(instanceinfo)
        return Response(serializer.data)
    
    
#    def put(self, request,appId,instanceId, format=None):
#        
#        # 1 接收数据
#        content =  request.DATA
#        
#        # 2 处理 启动 停止
#        #Action(content)
#        
#        # 3 消息返回
#        message = {}
#        message['status'] = "success"
#        message['code'] = "200"
#        message['data'] = content
#        return Response(message)
        
    
    