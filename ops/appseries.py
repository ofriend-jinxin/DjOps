from rest_framework import serializers
from ops import models
from django_celery_results.models import TaskResult
import datetime


# 需要交互（接口增删改）用ModelSerializer,不需要交互用Serializer
# Create your models here.
class AppSerializer(serializers.Serializer):
    aname = serializers.CharField(required=False)


# 网段
class VlanSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    vnet = serializers.CharField(required=False)
    varea = serializers.CharField(required=False)


# 机房
class IdcSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    iname = serializers.CharField(required=False)


# 机柜
class CabinetSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    cname = serializers.CharField(required=False)


# 机器表
class HostinfoSerializer(serializers.ModelSerializer):
    # required=False 前端可以传空 只序列化，不走校验，source=表模型字段名
    # read_only 表明该字段仅用于序列化输出，默认False, 如果设置成True，postman中可以看到该字段，修改时，不需要传该字段，传了也不生效
    # write_only 表明该字段仅用于反序列化输入，默认False，如果设置成True，postman中看不到该字段，修改时，该字段需要传
    id = serializers.IntegerField(required=False, read_only=True)
    hctime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    hhmtime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    hip = serializers.CharField(required=False)
    hhostname = serializers.CharField(required=False)
    hcabinet = CabinetSerializer(required=False)
    hidc = IdcSerializer(required=False)
    happ = AppSerializer(required=False)
    hvlan = VlanSerializer(required=False)
    htype = serializers.IntegerField(required=False)
    hu = serializers.CharField(required=False)
    hoobip = serializers.CharField(required=False)
    hmac = serializers.CharField(required=False)
    hsn = serializers.CharField(required=False)
    hsystem = serializers.CharField(required=False)
    hsystem_vendor = serializers.CharField(required=False)
    hkernel = serializers.CharField(required=False)
    hproduct_name = serializers.CharField(required=False)
    hcpu = serializers.CharField(required=False)
    hvcpu = serializers.CharField(required=False)
    hmem = serializers.CharField(required=False)
    hdisk = serializers.CharField(required=False)
    hexceedtime = serializers.DateField(required=False, format="%Y-%m-%d", input_formats=['%Y-%m-%d'])
    hnotes = serializers.CharField(required=False)

    class Meta:
        model = models.Hostinfo
        fields = '__all__'


# class RunResultSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(required=False, read_only=True)
#     rnum = serializers.IntegerField(required=False, read_only=True)
#     rctime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
#     riplist = serializers.CharField(required=False, read_only=True)
#     rctype = serializers.CharField(required=False, read_only=True)
#     rargs = serializers.CharField(required=False, read_only=True)
#     ris_sudo = serializers.CharField(required=False, read_only=True)
#     rstate = serializers.IntegerField(required=False, read_only=True)
#     rresult_txt = serializers.CharField(required=False, read_only=True)
#
#     class Meta:
#         model = models.RunResult
#         fields = '__all__'
#

class TaskResultSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=True)
    task_id = serializers.CharField(required=False, read_only=True)
    task_name = serializers.CharField(required=False, read_only=True)
    task_args = serializers.CharField(required=False, read_only=True)
    task_kwargs = serializers.CharField(required=False, read_only=True)
    status = serializers.CharField(required=False, read_only=True)
    worker = serializers.CharField(required=False, read_only=True)
    content_type = serializers.CharField(required=False, read_only=True)
    content_encoding = serializers.CharField(required=False, read_only=True)
    result = serializers.CharField(required=False, read_only=True)
    date_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",required=False, read_only=True)
    date_done = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",required=False, read_only=True)
    traceback = serializers.CharField(required=False, read_only=True)
    meta = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = TaskResult
        fields = '__all__'
