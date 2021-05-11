from rest_framework import serializers
from management import models
import datetime


# 需要交互（接口增删改）用ModelSerializer,不需要交互用Serializer
# Create your models here.
class AppGroupSerializer(serializers.Serializer):
    name=serializers.CharField(required=False)

# 网段
class VlaninfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    vlan_net = serializers.CharField(required=False)
    vlan_area = serializers.CharField(required=False)


# 机房
class IdcSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    name = serializers.CharField(required=False)


# 机柜
class CabinetSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    name = serializers.CharField(required=False)
    idc = IdcSerializer()


# 设备类型
class HostTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    name = serializers.CharField(required=False)


# 机器表
class HostinfoSerializer(serializers.ModelSerializer):
    # required=False 前端可以传空 只序列化，不走校验，source=表模型字段名
    # read_only 表明该字段仅用于序列化输出，默认False, 如果设置成True，postman中可以看到该字段，修改时，不需要传该字段，传了也不生效
    # write_only 表明该字段仅用于反序列化输入，默认False，如果设置成True，postman中看不到该字段，修改时，该字段需要传
    id = serializers.IntegerField(required=False, read_only=True)
    ctime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    mtime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    ip = serializers.CharField(required=False)
    hostname = serializers.CharField(required=False)
    idc = IdcSerializer(required=False)
    app = AppGroupSerializer(required=False)
    vlan = VlaninfoSerializer(required=False)
    cabinet = CabinetSerializer(required=False)
    type = HostTypeSerializer(required=False)
    u = serializers.CharField(required=False)
    oobip = serializers.CharField(required=False)
    mac = serializers.CharField(required=False)
    sn = serializers.CharField(required=False)

    system = serializers.CharField(required=False)
    kernel = serializers.CharField(required=False)
    cpu = serializers.CharField(required=False)
    vcpu = serializers.CharField(required=False)
    mem = serializers.CharField(required=False)
    disk = serializers.CharField(required=False)
    exceedtime = serializers.DateField(required=False, format="%Y-%m-%d", input_formats=['%Y-%m-%d'])
    notes = serializers.CharField(required=False)

    class Meta:
        model = models.Hostinfo
        fields = '__all__'
