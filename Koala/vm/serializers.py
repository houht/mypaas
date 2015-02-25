from rest_framework import serializers
from vm.models import image,vminfo,disk,net


class VminfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = vminfo
        fields = ('vmId', 'vmName','vmAlias', 'cpu', 'mem', 'size','image','engineId','engineIp','ip','vncPasswd','vncPort','username','password','user','status','remark','createTime','beginTime','endTime')
        
        
class DiskSerializer(serializers.ModelSerializer):

    class Meta:
        model = disk
        fields = ('diskId', 'diskName', 'diskType', 'vm', 'target','size','remark','createTime')
        

   
class NetSerializer(serializers.ModelSerializer):

    class Meta:
        model = net
        fields = ('netId', 'proxyIP', 'proxyPort','proxyType', 'ip', 'port','vm','remark','createTime')
        
        
             
        





