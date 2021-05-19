# django
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse

from django.views.generic.base import View
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django_filters import rest_framework as filters
from django_celery_results.models import TaskResult
# rest_framework
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import PageNumberPagination
from ops.models import *
# myproject
from DjOps import settings
from ops import models
from ops import appseries
# sys
import os, json
# celery
from ops.tasks import ActionRun, task_scan

import ast
import logging

logger = logging.getLogger('django')

from django_celery_results.models import TaskResult


# Create your views here.

############方法############
def is_super_user(func):
    '''身份认证装饰器，
    :param func:
    :return:
    '''

    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('/')
        return func(request, *args, **kwargs)

    return wrapper


class APIJsonResponse(JsonResponse):
    '''
    自己封装了一个类，前端需要返回json数据并且需要加上code信息前端
    '''

    def __init__(self, msg, code=0, log=None, **kwargs):
        return_data = {
            "code": code,
            "log": log,
            "msg": msg,
        }
        super().__init__(data=return_data, **kwargs)


class APIResponse(Response):
    def __init__(self, data, status=0, count=None, msg='成功', results=None, http_status=None,
                 headers=None, exception=False, content_type=None, **kwargs):
        # 将status、msg、results、kwargs格式化成data
        return_data = {
            'code': status,
            'count': count,
            'data': data,
            'msg': msg,
        }
        # results只要不为空都是数据：False、0、'' 都是数据 => 条件不能写if results
        if results is not None:
            return_data['results'] = results
        # 将kwargs中额外的k-v数据添加到data中
        return_data.update(**kwargs)
        super().__init__(data=return_data, status=http_status, headers=headers, exception=exception,
                         content_type=content_type)


class HostFilter(filters.FilterSet):
    '''
    定义一个IP字段的过滤器?ip=
    lookup_expr gte >=,lte <=,icontains 模糊查询不区分大小写,exact 精准匹配
    '''
    lookup_expr = 'icontains'
    # hip = filters.CharFilter(field_name='hip', lookup_expr=lookup_expr)
    hsn = filters.CharFilter(field_name='hsn', lookup_expr=lookup_expr)
    hoobip = filters.CharFilter(field_name='hoobip', lookup_expr=lookup_expr)
    htype = filters.CharFilter(field_name='htype', lookup_expr='exact')
    happ = filters.CharFilter(field_name='happ_id', lookup_expr='exact')
    hidc = filters.CharFilter(field_name='hidc_id', lookup_expr='exact')
    hvlan = filters.CharFilter(field_name='hvlan_id', lookup_expr='exact')

    class Meta:
        model = models.Hostinfo
        fields = ['hsn', 'hoobip', 'htype', 'happ', 'hidc', 'hvlan']


class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='icontains')
    task_id = filters.CharFilter(field_name='task_id', lookup_expr='icontains')
    task_kwargs = filters.CharFilter(field_name='task_kwargs', lookup_expr='icontains')

    # # 开始时间
    sartdate = filters.DateTimeFilter(field_name='date_created', lookup_expr='gte')
    # # 结束时间
    enddate = filters.DateTimeFilter(field_name='date_created', lookup_expr='lte')

    class Meta:
        model = TaskResult
        fields = ['status', 'task_id', 'task_kwargs', 'sartdate', 'enddate']


class HostFilter_exact(filters.FilterSet):
    '''
    定义一个IP字段的过滤器?ip=
    lookup_expr gte >=,lte <=,icontains 模糊查询不区分大小写,exact 精准匹配
    '''
    lookup_expr = 'exact'
    # hip = filters.CharFilter(field_name='hip', lookup_expr=lookup_expr)
    hsn = filters.CharFilter(field_name='hsn', lookup_expr=lookup_expr)
    hoobip = filters.CharFilter(field_name='hoobip', lookup_expr=lookup_expr)
    htype = filters.CharFilter(field_name='htype', lookup_expr='exact')
    happ = filters.CharFilter(field_name='happ_id', lookup_expr='exact')
    hidc = filters.CharFilter(field_name='hidc_id', lookup_expr='exact')
    hvlan = filters.CharFilter(field_name='hvlan_id', lookup_expr='exact')

    class Meta:
        model = models.Hostinfo
        fields = ['hsn', 'hoobip', 'htype', 'happ', 'hidc', 'hvlan']


class CuseomPagination(PageNumberPagination):
    '''
    分页器
    '''
    page_size = 20  # 显示多少页
    page_query_param = 'page'  # /url/?page=100
    page_size_query_param = 'limit'  # /url/limit=10 前端控制每页显示最大条目数

    def get_paginated_response(self, data):
        return APIResponse(data, count=self.page.paginator.count)


def pagination_response(query_set, request, serializer):
    '''
    生成分页数据，传入obj，request，ser
    '''
    pagination = CuseomPagination()
    pagination_queryset = pagination.paginate_queryset(query_set, request)
    data = serializer(pagination_queryset, many=True).data
    return pagination.get_paginated_response(data)


############视图############
def logout(request):
    auth.logout(request)
    return redirect('/login/')


class LoginView(View):
    """
    登录视图
    """

    def get(self, request):
        return render(request, 'login/login.html')

    def post(self, request):
        next_url = request.GET.get('next')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        logger.error(next_url)
        if user:
            auth.login(request, user)
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            message = '用户名或密码不正确！'
            return render(request, 'login/login.html', {'message': message})


@method_decorator(login_required, 'dispatch')  # 装饰get请求，写view就是全部。也可以卸载class中函数上方，第二个get参数就不用写了
class IndexView(View):
    """
    主页视图,获取主机信息返回给页面展示
    """

    def get(self, request):
        allm = Hostinfo.objects.all().count()
        phy = Hostinfo.objects.filter(htype=1).count()
        host = Hostinfo.objects.filter(htype=2).count()
        vm = Hostinfo.objects.filter(htype=3).count()
        app = App.objects.all().count()

        count = {"all": allm, "phys": phy, "vms": vm, "apps": app, "hosts": host}
        return render(request, 'index.html', {'count': count})


@method_decorator(login_required, 'dispatch')
class AssetsView(View):
    """
    主机资源页面
    """

    def get(self, request):
        vlan = Vlan.objects.all()
        app = App.objects.all()
        idc = Idc.objects.all()
        htype = [
            {'id': 1, 'hname': '物理机'},
            {'id': 2, 'hname': '宿主机'},
            {'id': 3, 'hname': '虚拟机'}
        ]
        cabinet = Cabinet.objects.all()
        return_obj = {
            'vlan': vlan,
            'app': app,
            'idc': idc,
            'htype': htype,
            'cabinet': cabinet,

        }
        return render(request, 'ops/assets.html', return_obj)


@method_decorator(login_required, 'dispatch')
class HostView(ViewSet):  # ViewSet
    """
    api/hosts/ 获取主机资源接口
    """

    def list(self, request):
        is_like = request.GET.get('is_like')
        hip = request.GET.getlist('hip', '')
        print(hip)
        if "," in hip:
            hip = hip.split(",")
            hostinfo = models.Hostinfo.objects.filter(hip__in=hip)
        elif " " in hip:
            hip = hip.split(" ")
            hostinfo = models.Hostinfo.objects.filter(hip__in=hip)
        else:
            hostinfo = models.Hostinfo.objects.all()
        if is_like == 'true':
            filterset_class = HostFilter(request.GET, hostinfo)
        else:
            filterset_class = HostFilter_exact(request.GET, hostinfo)
        return pagination_response(filterset_class.qs, request, appseries.HostinfoSerializer)

    @method_decorator(is_super_user)
    def delete(self, request):
        pk = request.GET.get('id')
        if ',' in pk:
            idlist = pk.split(',')[:-1]
        else:
            idlist = [pk]

        try:
            models.Hostinfo.objects.filter(id__in=idlist).delete()
            return APIResponse(data=pk, msg='删除成功')
        except Exception as e:
            return APIResponse(code=1, msg=e)

    @method_decorator(is_super_user)
    # 行更新
    # def put(self, request):
    #     ip = request.GET.get('ip')
    #     if ',' in ip:
    #         iplist = str(ip).split(',')[:-1]
    #     else:
    #         iplist = [ip]
    #     ActionRun.delay(iplist=iplist, ctype='setup')
    #     return APIResponse(msg='任务进入后台执行请稍等', log=iplist, data=iplist)

    def put(self, request):
        pk = request.GET.get('id')
        data = request.GET.get('data')
        try:
            data = json.loads(data)
            hostobj=models.Hostinfo.objects.get(id=pk)
            hostobj.hoobip=data.get('hoobip')
            hostobj.hu=data.get('hu')
            hostobj.hnotes=data.get('hnotes')
            hostobj.save()
            return APIResponse(msg='仅更新oobip、u、备注', log=data, data=data)
        except Exception as e:
            return APIResponse(msg='参数错误', log=e, data=data)
@method_decorator(login_required, 'dispatch')
class ScanView(View):
    def get(self, request):
        vlaninfo = Vlan.objects.all()
        appinfo = App.objects.all()
        idcinfo = Idc.objects.all()
        info = "{} {} {}".format(vlaninfo, appinfo, idcinfo)
        logger.info(info)
        return render(request, 'ops/scan.html', {'vlaninfo': vlaninfo, 'appinfo': appinfo, 'idcinfo': idcinfo})

    @method_decorator(is_super_user)
    def post(self, request):
        vlan = request.POST.get('vlan')
        app_id = request.POST.get('app')
        idc_id = request.POST.get('idc')
        vlanobj = Vlan.objects.filter(vnet=vlan).first()
        if vlanobj:
            info = "scan : vlan-{},app-{},vlaid-{},idcid-{}".format(vlan, app_id, vlanobj.id, idc_id)
            logger.info(info)
            task_scan.delay(vlan=vlan, app_id=app_id, vlan_id=vlanobj.id, idc_id=idc_id, ctype='scan')
            return APIJsonResponse(msg="任务进入后台执行")
        else:
            return APIJsonResponse(code=1, msg='参数错误')


@login_required
@is_super_user
def resinfo(request):
    '''
    详情页，等重写
    '''
    return HttpResponseRedirect(reverse('ops:assets'))


def get_sh_file(fdir, fstr):
    '''
    获取sh，yml脚本文件
    '''
    fileList = []
    path = str(settings.BASE_DIR) + "/DjOps/localfile" + fdir
    # 先添加目录级别

    for cur_dir, dirs, files in os.walk(path):
        for f in files:  # 当前目录下的所有文件

            if f.endswith(fstr):
                file_path = "{}/{}".format(cur_dir, f)
                fileList.append({'name': f, 'path': file_path})
    return fileList


@method_decorator(login_required, 'dispatch')
class ActionView(View):
    def get(self, request):
        iplist = str(request.GET.get('ip')).split(',')[:-1]
        ctype = request.GET.get('type')
        if len(iplist) == 0:
            last_html = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(last_html)
        if ctype == 'script':
            filelist = get_sh_file("/shell", '.sh')
        elif ctype == 'playbook':
            filelist = get_sh_file("/playbook", '.yml')
        else:
            filelist = []
        return render(request, 'ops/shell.html', {'filelist': filelist, 'iplist': iplist, 'run_type': ctype})

    def post(self, request):
        try:
            iplist = request.POST.getlist('ip')
            ctype = request.POST.get('type')
            is_sudo = request.POST.get('open')
            if ctype == 'script':
                command = request.POST.get('script')
                script_args = request.POST.get('script_args')
                command = "{} {}".format(command, script_args)
            elif ctype == 'shell':
                command = request.POST.get('shell')
            elif ctype == 'playbook':
                command = request.POST.get('playbook')
            else:
                command = False
            ActionRun.delay(is_sudo=is_sudo, iplist=iplist, args=command, ctype=ctype)
            info = "{} {} {} {}".format(iplist, ctype, is_sudo, command)
            logger.info(info)
            return APIJsonResponse(code=0, msg="任务进入后台执行", log=info)
        except Exception as e:
            return APIJsonResponse(code=1, msg='操作失败', log=e)
    # 行更新
    def put(self, request):
        ip = request.GET.get('ip')
        if ',' in ip:
            iplist = str(ip).split(',')[:-1]
        else:
            iplist = [ip]
        ActionRun.delay(iplist=iplist, ctype='setup')
        return APIJsonResponse(msg='任务进入后台执行请稍等', log=iplist)

@method_decorator(login_required, 'dispatch')
class TaskView(View):
    '''
    执行日志页面
    '''

    def get(self, request):
        states = [('FAILURE', 'FAILURE'), ('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('RETRY', 'RETRY'),
                  ('REVOKED', 'REVOKED'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS')]

        ctypes = ['shell', 'playbook', 'scan', 'script', 'setup']
        result_obj = {
            'state': states,
            'ctype': ctypes,
        }
        return render(request, 'ops/tasks.html', result_obj)


@method_decorator(login_required, 'dispatch')
class TaskViewSet(ViewSet):  # ViewSet
    """
    api/tasks/ 获取任务信息接口
    """

    filterset_class = HostFilter

    def list(self, request):
        taskinfo = TaskResult.objects.all()
        filterset_class = TaskFilter(request.GET, taskinfo)
        return pagination_response(filterset_class.qs, request, appseries.TaskResultSerializer)

    def delete(self, request):
        pk = request.GET.get('id')
        if ',' in pk:
            pk = str(pk).split(',')[:-1]
        else:
            pk = [pk]
        logger.info(pk)
        TaskResult.objects.filter(id__in=pk).delete()
        return APIResponse(data=pk, msg='删除成功')

    def post(self, request):
        pk = request.POST.get('id')
        try:
            taskobj = TaskResult.objects.get(id=pk)
            task_kwargs = eval(taskobj.task_kwargs)
            task_kwargs = eval(task_kwargs)
            logger.info(task_kwargs)
            if 'scan' in str(task_kwargs):
                task_scan.delay(**task_kwargs)
                return APIResponse(msg='任务进入后台执行，稍后查看结果', data=pk)
            else:
                ActionRun.delay(**task_kwargs)
                return APIResponse(msg='任务进入后台执行，稍后查看结果', data=pk)
        except Exception as e:
            print(e)
            return APIResponse(data=pk, msg=e)


def testhtml(request):
    return render(request, 'test.html')
