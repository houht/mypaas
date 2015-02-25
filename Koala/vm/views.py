#!/usr/bin/python
# -*- coding: UTF-8 -*-

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from vm.libs.action import Action
from vm.libs.check import Check

from vm.models import vminfo,disk,net
from vm.serializers import VminfoSerializer,DiskSerializer,NetSerializer


from django.http import Http404



# vm查询
class VmList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    # 查询
    def get(self, request, format=None):
        
        
        info = vminfo.objects.all()
        serializer = VminfoSerializer(info, many=True)
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



#vm操作
class VmDetail(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return vminfo.objects.get(vmId=vmId)
        except vminfo.DoesNotExist:
            raise Http404
    
    
    
    # 查询
    def get(self, request, vmId, format=None):
        
        info = self.get_object(vmId)
        serializer = VminfoSerializer(info)
        return Response(serializer.data)

    
    # 更新 启动 关闭
    def put(self, request, vmId, format=None):
        
        content =  request.DATA

        content['vmId'] = vmId
        # 1 检测
        Check(content)
        # 2 响应
        Action(content)
        # 3 返回
        message = {}
        message['status'] = "success"
        message['code'] = "200"
        message['data'] = content

        return Response(message)


#net操作
class VmNetList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return net.objects.filter(vm=vmId)
        except vminfo.DoesNotExist:
            raise Http404
 
    # 查询
    def get(self, request, vmId, format=None):
        info = self.get_object(vmId)
        serializer = NetSerializer(info, many=True)
        return Response(serializer.data)


#disk操作
class VmDiskList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return disk.objects.filter(vm=vmId)
        except vminfo.DoesNotExist:
            raise Http404

    
    # 查询
    def get(self, request, vmId, format=None):
        info = self.get_object(vmId)
        serializer = DiskSerializer(info, many=True)
        return Response(serializer.data)


