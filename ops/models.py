from django.db import models
from django.utils import timezone


# Create your models here.
# 应用表
class App(models.Model):
    aname = models.CharField(max_length=128, unique=True, verbose_name='应用')

    class Meta:
        db_table = 'ops_app'
        verbose_name = '应用'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.aname


# 网段
class Vlan(models.Model):
    vnet = models.CharField(max_length=128, unique=True, verbose_name='网段地址')
    varea = models.CharField(max_length=128, verbose_name='所在环境')

    class Meta:
        db_table = 'ops_vlan'
        verbose_name = '网段信息'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.vnet


# 机房
class Idc(models.Model):
    iname = models.CharField(max_length=128, unique=True, verbose_name='机房名称')
    iaddress = models.CharField(verbose_name="机房地址", max_length=256)
    iphone = models.CharField(verbose_name="联系人", max_length=15)
    iemail = models.EmailField(verbose_name="邮件地址", default="null")

    class Meta:
        db_table = 'ops_idc'
        verbose_name = '机房'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.iname


# 机柜
class Cabinet(models.Model):
    cname = models.CharField(max_length=128, unique=True, verbose_name='机柜')
    cidc = models.ForeignKey(Idc, verbose_name="所在机房", on_delete=models.PROTECT)

    class Meta:
        db_table = 'ops_cabinet'
        verbose_name = '机柜'
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.cname


# 机器表
class Hostinfo(models.Model):
    HOSTTYPE_CHOICES = (  # 任务状态
        (1, '物理机'),
        (2, '宿主机'),
        (3, '虚拟机'),
    )
    # NULL 和数据库相关的控制，blank 和表单相关的控制 ,true 表示可以为空assets_type_choices
    hctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    hmtime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    hip = models.GenericIPAddressField(unique=True, verbose_name='ip')
    hhostname = models.CharField(max_length=128, verbose_name='主机名', blank=True)
    hcabinet = models.ForeignKey(Cabinet, on_delete=models.SET_NULL, verbose_name='机柜', blank=True, null=True)
    happ = models.ForeignKey(App, on_delete=models.SET_NULL, verbose_name='应用', blank=True, null=True)
    hidc = models.ForeignKey(Idc, on_delete=models.SET_NULL, verbose_name='机房', blank=True, null=True)
    hvlan = models.ForeignKey(Vlan, on_delete=models.SET_NULL, verbose_name='网段地址', blank=True, null=True)
    htype = models.SmallIntegerField(verbose_name='设备类型', choices=HOSTTYPE_CHOICES, blank=True, null=True)
    hu = models.CharField(max_length=32, verbose_name='U位', blank=True)
    hoobip = models.CharField(verbose_name='带外ip', unique=True, blank=True, null=True, max_length=128)
    hmac = models.CharField(max_length=128, verbose_name='mac地址', blank=True)
    hsn = models.CharField(max_length=128, verbose_name='sn', blank=True)
    # on_delete=models.CASCADE：admin后台删除vlaninfo 关联vlaninfo的host数据也删除
    hsystem = models.CharField(max_length=128, verbose_name='操作系统', blank=True)
    hsystem_vendor = models.CharField(max_length=128, verbose_name='设备型号', blank=True)
    hkernel = models.CharField(max_length=128, verbose_name='内核', blank=True)
    hproduct_name = models.CharField(max_length=128, verbose_name='机器型号', blank=True)
    hbios_vendor = models.CharField(max_length=128, verbose_name='Bios生产商', blank=True)
    hcpu = models.CharField(max_length=128, verbose_name='CPU型号', blank=True)
    hvcpu = models.CharField(max_length=128, verbose_name='vcpus', blank=True)
    hmem = models.CharField(max_length=128, verbose_name='内存', blank=True)
    hdisk = models.CharField(max_length=128, verbose_name='硬盘', blank=True)
    hexceedtime = models.DateField(verbose_name="到期时间", blank=True, default=timezone.now)
    hnotes = models.TextField(verbose_name='备注', blank=True)

    # 使对象在后台显示更友好
    def __str__(self):
        return self.hip

    class Meta:
        db_table = 'ops_hostinfo'
        verbose_name = '服务器列表'  # 指定后台显示模型名称
        verbose_name_plural = verbose_name  # 指定后台显示模型复数名称
        ordering = ["id"]

#
# class RunResult(models.Model):
#     STATE_CHOICES = (  # 任务状态
#         (1, '进行中'),
#         (2, '异常'),
#         (3, '完成'),
#     )
#     rctime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#     rip = models.TextField(verbose_name='执行主机', blank=True)
#     rnum = models.IntegerField(verbose_name='ip数量', blank=True, default=0)
#     rtype = models.CharField(verbose_name='任务类型', max_length=128, blank=True)
#     rargs = models.CharField(verbose_name='任务参数', max_length=256, blank=True)
#     ris_sudo = models.CharField(verbose_name='是否root', max_length=16, blank=True)
#     rstate = models.SmallIntegerField(verbose_name='任务状态', choices=STATE_CHOICES)
#     rustime = models.FloatField(blank=True, null=True)
#     rresult_txt = models.TextField(verbose_name='命令结果', blank=True)
#
#     # 使对象在后台显示更友好
#     def __str__(self):
#         return self.rip
#
#     class Meta:
#         db_table = 'ops_runresult'
#         verbose_name = '执行结果'  # 指定后台显示模型名称
#         verbose_name_plural = verbose_name  # 指定后台显示模型复数名称
#         ordering = ["id"]
