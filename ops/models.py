from django.db import models
from django.utils import timezone


# Create your models here.
# 应用表
class AppGroup(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='应用')

    class Meta:
        verbose_name = '应用'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.name


# 网段
class Vlaninfo(models.Model):
    vlan_net = models.CharField(max_length=128,unique=True ,verbose_name='网段地址')
    vlan_area = models.CharField(max_length=128, verbose_name='所在环境')

    class Meta:
        verbose_name = '网段信息'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.vlan_net


# 机房
class Idc(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='机房名称')
    address = models.CharField(verbose_name="机房地址", max_length=256)
    phone = models.CharField(verbose_name="联系人", max_length=15)
    email = models.EmailField(verbose_name="邮件地址", default="null")

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.name


# 机柜
class Cabinet(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='机柜')
    idc = models.ForeignKey(Idc, verbose_name="所在机房", on_delete=models.CASCADE)

    class Meta:
        verbose_name = '机柜'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.name

# 机器表
class Hostinfo(models.Model):
    HOSTTYPE_CHOICES = (  # 任务状态
        (1, '物理机'),
        (2, '宿主机'),
        (3, '虚拟机'),
    )
    # NULL 和数据库相关的控制，blank 和表单相关的控制 ,true 表示可以为空assets_type_choices
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    mtime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    ip = models.GenericIPAddressField(unique=True, verbose_name='ip')
    hostname = models.CharField(max_length=128, verbose_name='主机名', blank=True)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.SET_NULL, verbose_name='机柜', blank=True, null=True)
    idc = models.ForeignKey(Idc, on_delete=models.SET_NULL, verbose_name='机房', blank=True, null=True)
    type = models.SmallIntegerField(verbose_name='设备类型',choices=HOSTTYPE_CHOICES,blank=True, null=True)
    u = models.CharField(max_length=32, verbose_name='U位', blank=True)
    oobip = models.CharField(verbose_name='带外ip', default='无', blank=True, max_length=128)
    equipment_model = models.CharField(max_length=128, verbose_name='设备型号', blank=True)
    mac = models.CharField(max_length=128, verbose_name='mac地址', blank=True)
    sn = models.CharField(max_length=128, verbose_name='sn', blank=True)
    app = models.ForeignKey(AppGroup, on_delete=models.SET_NULL, verbose_name='应用', blank=True,null=True)
    # on_delete=models.CASCADE：admin后台删除vlaninfo 关联vlaninfo的host数据也删除
    vlan = models.ForeignKey(Vlaninfo, on_delete=models.SET_NULL, verbose_name='网段地址', blank=True, null=True)
    system = models.CharField(max_length=128, verbose_name='操作系统', blank=True)
    kernel = models.CharField(max_length=128, verbose_name='内核', blank=True)
    cpu = models.CharField(max_length=128, verbose_name='CPU型号', blank=True)
    vcpu = models.CharField(max_length=128, verbose_name='vcpus', blank=True)
    mem = models.CharField(max_length=128, verbose_name='内存', blank=True)
    disk = models.CharField(max_length=128, verbose_name='硬盘', blank=True)
    exceedtime = models.DateField(verbose_name="到期时间", blank=True, default=timezone.now)
    notes = models.TextField(verbose_name='备注', blank=True)

    # 使对象在后台显示更友好
    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = '服务器列表'  # 指定后台显示模型名称
        verbose_name_plural = verbose_name  # 指定后台显示模型复数名称
        ordering = ["id"]


class RunResult(models.Model):
    STATE_CHOICES = (  # 任务状态
        (1, '进行中'),
        (2, '异常'),
        (3, '完成'),
    )
    ctime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    ip = models.TextField(verbose_name='执行主机', blank=True)
    num = models.IntegerField(verbose_name='ip数量', blank=True, default=0)
    ctype = models.CharField(verbose_name='任务类型', max_length=128, blank=True)
    args = models.CharField(verbose_name='任务参数', max_length=256, blank=True)
    is_sudo = models.CharField(verbose_name='是否root', max_length=16, blank=True)
    state = models.SmallIntegerField(verbose_name='任务状态',choices=STATE_CHOICES)
    ustime = models.FloatField(blank=True,null=True)
    result_txt = models.TextField(verbose_name='命令结果', blank=True)
