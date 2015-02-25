from rest_framework import serializers
from app.models import Appinfo,instanceinfo



class AppinfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appinfo
        fields = ('appId', 'service', 'appName', 'cpu', 'mem', 'disk','appFileId','appEnv','userEnv','domain','tokenId','listenPort','user','status')


class InstanceinfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = instanceinfo
        fields = ('instanceId', 'app', 'engineId', 'ip', 'port', 'status','createTime','beginTime','endTime')
