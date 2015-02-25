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



# vm��ѯ
class VmList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    # ��ѯ
    def get(self, request, format=None):
        
        
        info = vminfo.objects.all()
        serializer = VminfoSerializer(info, many=True)
        return Response(serializer.data)
        
        
    # ����
    def post(self, request, format=None):
        
        
        content =  request.DATA
        
        # 1 �����Ƿ�Ϸ��������Ƿ��Ѿ��ύ
        Check(content)
        # 2 ������
        Action(content)
        # 3 ����
        message = {}
        message['status'] = "success"
        message['code'] = "200"
        message['data'] = content
        
        return Response(message)



#vm����
class VmDetail(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return vminfo.objects.get(vmId=vmId)
        except vminfo.DoesNotExist:
            raise Http404
    
    
    
    # ��ѯ
    def get(self, request, vmId, format=None):
        
        info = self.get_object(vmId)
        serializer = VminfoSerializer(info)
        return Response(serializer.data)

    
    # ���� ���� �ر�
    def put(self, request, vmId, format=None):
        
        content =  request.DATA

        content['vmId'] = vmId
        # 1 ���
        Check(content)
        # 2 ��Ӧ
        Action(content)
        # 3 ����
        message = {}
        message['status'] = "success"
        message['code'] = "200"
        message['data'] = content

        return Response(message)


#net����
class VmNetList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return net.objects.filter(vm=vmId)
        except vminfo.DoesNotExist:
            raise Http404
 
    # ��ѯ
    def get(self, request, vmId, format=None):
        info = self.get_object(vmId)
        serializer = NetSerializer(info, many=True)
        return Response(serializer.data)


#disk����
class VmDiskList(APIView):
    
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self, vmId):
        try:
            return disk.objects.filter(vm=vmId)
        except vminfo.DoesNotExist:
            raise Http404

    
    # ��ѯ
    def get(self, request, vmId, format=None):
        info = self.get_object(vmId)
        serializer = DiskSerializer(info, many=True)
        return Response(serializer.data)


