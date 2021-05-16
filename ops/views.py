# django
from django import forms
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse

from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic.edit import FormView
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django_filters import rest_framework as filters

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
import os
# celery
from celery_tasks.tasks import RunAnsible, task_scan

import json, ast
import logging

logger = logging.getLogger('django')


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

    def __init__(self, data, code=0, log=None, **kwargs):
        return_data = {
            "code": code,
            "log": log,
            "msg": data,
        }
        super().__init__(data=return_data, **kwargs)


class APIResponse(Response):
    def __init__(self, data, status=0, count=None, msg='成功', results=None, http_status=None,
                 headers=None, exception=False, content_type=None, **kwargs):
        # 将status、msg、results、kwargs格式化成data
        return_data = {
            'code': status,
            'count': count,
            'msg': msg,
            'data': data,
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
    ip = filters.CharFilter(field_name='ip', lookup_expr=lookup_expr)
    sn = filters.CharFilter(field_name='sn', lookup_expr=lookup_expr)
    oobip = filters.CharFilter(field_name='oobip', lookup_expr=lookup_expr)
    hosttype = filters.CharFilter(field_name='type', lookup_expr=lookup_expr)
    app = filters.CharFilter(field_name='app__name', lookup_expr=lookup_expr)
    idc = filters.CharFilter(field_name='idc__name', lookup_expr=lookup_expr)
    vlan = filters.CharFilter(field_name='vlan__vlan_area', lookup_expr=lookup_expr)

    class Meta:
        model = models.Hostinfo
        fields = ['ip', 'sn', 'oobip', 'hosttype', 'app', 'idc', 'vlan']


class HostFilter_exact(filters.FilterSet):
    '''
    定义一个IP字段的过滤器?ip=
    lookup_expr gte >=,lte <=,icontains 模糊查询不区分大小写,exact 精准匹配
    '''
    lookup_expr = 'exact'
    ip = filters.CharFilter(field_name='ip', lookup_expr=lookup_expr)
    sn = filters.CharFilter(field_name='sn', lookup_expr=lookup_expr)
    oobip = filters.CharFilter(field_name='oobip', lookup_expr=lookup_expr)
    hosttype = filters.CharFilter(field_name='type', lookup_expr=lookup_expr)
    app = filters.CharFilter(field_name='app__name', lookup_expr=lookup_expr)
    idc = filters.CharFilter(field_name='idc__name', lookup_expr=lookup_expr)
    vlan = filters.CharFilter(field_name='vlan__vlan_area', lookup_expr=lookup_expr)

    class Meta:
        model = models.Hostinfo
        fields = ['ip', 'sn', 'oobip', 'hosttype', 'app', 'idc', 'vlan']


class RunResultFilter(filters.FilterSet):
    '''
    定义一个IP字段的过滤器?ip=
    lookup_expr gte >=,lte <=,icontains 模糊查询不区分大小写,exact 精准匹配
    '''
    lookup_expr = 'icontains'
    ip = filters.CharFilter(field_name='ip', lookup_expr=lookup_expr)
    ctype = filters.CharFilter(field_name='ctype',lookup_expr=lookup_expr)
    state = filters.CharFilter(field_name='state',lookup_expr=lookup_expr)
    # 开始时间
    startdate = filters.DateTimeFilter(field_name='ctime', lookup_expr='gte')
    # 结束时间
    enddate = filters.DateTimeFilter(field_name='ctime', lookup_expr='lte')

    class Meta:
        model = models.RunResult
        fields = ['ip', 'ctype','state','startdate','enddate']

class CuseomPagination(PageNumberPagination):
    '''
    分页器
    '''
    page_size = 100  # 每页显示多少条
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

class LoginView(View):
    """
    登录视图
    """

    def get(self, request):
        return render(self.request, 'login/login.html')

    def post(self, request):
        next_url = self.request.GET.get('next')
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        logger.error(next_url)
        if user:
            auth.login(self.request, user)
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            message = '用户名或密码不正确！'
            return render(request, 'login/login.html', {'message': message})


@method_decorator(is_super_user, 'get')  # 装饰get请求，写view就是全部。也可以卸载class中函数上方，第二个get参数就不用写了
class IndexView(View):
    """
    主页视图
    """

    def get(self, request):
        allmachine = Hostinfo.objects.all()
        phymachine = Hostinfo.objects.all()
        vmmachine = Hostinfo.objects.all()
        groupnum = AppGroup.objects.all()
        count = {"all": allmachine, "phy": phymachine, "vm": vmmachine, "group": groupnum}
        return render(self.request, 'index.html', {'count': count})


@method_decorator(login_required, 'dispatch')
class AssetsView(View):
    """
    主机资源页面
    """

    def get(self, request):
        vlan = Vlaninfo.objects.all()
        app = AppGroup.objects.all()
        idc = Idc.objects.all()

        hosttype = [
            {'id': 1, 'name': '物理机'},
            {'id': 2, 'name': '宿主机'},
            {'id': 3, 'name': '虚拟机'}
        ]
        cabinet = Cabinet.objects.all
        return_obj = {
            'vlan': vlan,
            'app': app,
            'idc': idc,
            'hosttype': hosttype,
            'cabinet': cabinet,

        }

        return render(self.request, 'ops/assets.html', return_obj)


@method_decorator(login_required, 'dispatch')
class HostView(ViewSet):  # ViewSet
    '''
    api/hosts/ 获取主机资源接口
    '''
    filterset_class = HostFilter

    def list(self, request):
        is_like = self.request.GET.get('is_like')
        hostinfo = models.Hostinfo.objects.all()
        if is_like == 'true':
            filterset_class = HostFilter(self.request.GET, hostinfo)
        else:
            filterset_class = HostFilter_exact(self.request.GET, hostinfo)
        return pagination_response(filterset_class.qs, self.request, appseries.HostinfoSerializer)

    @method_decorator(is_super_user)
    def delete(self, request):
        id = self.request.GET.get('id')
        if ',' in id:
            idlist = id.split(',')[:-1]
        else:
            idlist = [id]

        try:
            models.Hostinfo.objects.filter(id__in=idlist).delete()
            return APIResponse(data=id, msg='删除成功')
        except Exception as e:
            return APIResponse(code=1, msg=e)

    @method_decorator(is_super_user)
    def update(self, request):
        ip = self.request.GET.get('ip')

        if ',' in ip:
            iplist = str(ip).split(',')[:-1]
        else:
            iplist = [ip]
        RunAnsible.delay(is_sudo='on', iplist=iplist, ctype='setup', args=None)
        return APIResponse(msc='任务进入后台执行请稍等', log='任务进入后台执行请稍等', data=ip)


@method_decorator(login_required, 'dispatch')
class ScanView(View):
    def get(self, request):
        vlaninfo = Vlaninfo.objects.all()
        groupinfo = AppGroup.objects.all()
        idcinfo = Idc.objects.all()
        return render(request, 'ops/scan.html', {'vlaninfo': vlaninfo, 'groupinfo': groupinfo, 'idcinfo': idcinfo})

    @method_decorator(is_super_user)
    def post(self, request):
        vlan = self.request.POST.get('vlan')
        app_id = self.request.POST.get('app')
        idc_id = self.request.POST.get('idc')
        vlanobj = Vlaninfo.objects.filter(vlan_net=vlan).first()

        if vlanobj:
            info = "scan : {} {} {} {}".format(vlan, app_id, vlanobj.id,idc_id)
            logger.info(info)
            task_scan.delay(vlan, app_id, vlanobj.id,idc_id)
            return APIJsonResponse(data=str(vlanobj))
        else:
            return APIJsonResponse(code=1, data='参数错误')


@login_required
@is_super_user
def resinfo(request):
    '''
    详情页，等重写
    '''
    thepage = {}
    thepage['h1'] = '详情'
    thepage['name'] = '详细信息'
    last_html = request.META.get('HTTP_REFERER', '/')
    if request.method == 'GET':
        osid = request.GET.get('osid')
        try:
            os_info = Hostinfo.objects.filger(id=osid)
            os_info = model_to_dict(os_info)
            groupinfo = AppGroup.objects.all()
            vlaninfo = Vlaninfo.objects.all()
            app = AppGroup.objects.get(id=os_info['app']).name

            return render(request, 'ops/resinfo.html',
                          {'osinfo': os_info, 'os_group': app, 'thepage': thepage, 'groupinfo': groupinfo,
                           'vlaninfo': vlaninfo})
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect(last_html)
    elif request.method == 'POST':
        try:
            logger.info(request.POST)
            id_num = request.POST.get('id_num')
            vlan = request.POST.get('vlan')
            mem = request.POST.get('mem')
            mac = request.POST.get('mac')
            disk = request.POST.get('disk')
            vcpu = request.POST.get('vcpu')
            cpu = request.POST.get('cpu')
            sn = request.POST.get('sn')
            kernel = request.POST.get('kernel')
            notes = request.POST.get('notes')
            group = request.POST.get('group')
            osobj = Hostinfo.objects.get(id=id_num)
            osobj.app = AppGroup.objects.get(id=group)
            osobj.mac = mac
            osobj.device = disk
            osobj.vcpu = vcpu
            osobj.cpu = cpu
            osobj.mem = mem
            osobj.sn = sn
            osobj.notes = notes
            osobj.kernel = kernel
            vlanobj = Vlaninfo.objects.get(id=vlan)
            osobj.vlan = vlanobj
            osobj.save()

            return redirect('/resinfo/?osid={}'.format(id_num))
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect(last_html)


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


@login_required
@is_super_user
def shell(request):
    '''
    执行shell 命令 playbook
    '''
    fileList = []
    shell_res = []
    if request.method == 'POST':
        try:
            if request.method == 'POST':
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
                if iplist:
                    RunAnsible.delay(is_sudo=is_sudo, iplist=iplist, args=command, ctype=ctype)
                info = "{} {} {} {}".format(iplist, ctype, is_sudo, command)
                logger.info(info)
                return APIJsonResponse(code=0, data='任务提交成功请稍后查看', log=info)
        except Exception as e:
            return APIJsonResponse(code=1, data='操作失败', log=e)
    else:
        iplist = str(request.GET.get('ip')).split(',')[:-1]
        ctype = request.GET.get('type')
        if len(iplist) == 0:
            last_html = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(last_html)
    if ctype == 'script':
        fileList = get_sh_file("/shell", '.sh')
    elif ctype == 'playbook':
        fileList = get_sh_file("/playbook", '.yml')
    return render(request, 'ops/shell.html',
                  {'filelist': fileList, 'iplist': iplist, 'shell_res': shell_res, 'run_type': ctype})


class ResultView(ViewSet):
    '''
    执行结果
    '''
    filterset_class = RunResultFilter()
    def list(self, request):
        RsultInfo = models.RunResult.objects.all()
        filterset_class = RunResultFilter(request.GET, RsultInfo)
        return pagination_response(filterset_class.qs, request, appseries.RunResultSerializer)


@login_required
@is_super_user
def runresult(request):
    delid = request.GET.get('delid', '')
    if len(delid) > 0:
        for id in str(delid).split(',')[:-1]:
            models.RunResult.objects.get(id=id).delete()
        return APIJsonResponse(data='操作成功')
    states = [
        {'id': 1, 'name': '执行中'},
        {'id': 2, 'name': '异常'},
        {'id': 3, 'name': '完成'}
    ]
    ctypes=['shell','playbook','scan','script']
    result_obj = {
        'state': states,
        'ctype':ctypes,
    }
    return render(request, 'ops/runresult.html',result_obj)


@login_required
@is_super_user
def openresult(request):
    id = request.GET.get('id')
    if id:
        obj = models.RunResult.objects.get(id=id)
        result_txt = obj.result_txt
        try:
            result_txt = ast.literal_eval(result_txt)
            types='list'
        except Exception as e:
            types='str'
        return render(request, 'ops/openresult.html', {'result': result_txt, 'types': types})


@login_required
@is_super_user
def rerun(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        task_obj = models.RunResult.objects.get(id=id)
        iplist = task_obj.ip.split(',')
        is_sudo = task_obj.is_sudo
        ctype = task_obj.ctype
        args = task_obj.args
        info = "{} {} {} {} {}".format(id, iplist, is_sudo, ctype, args)
        logger.info(info)
        if ctype == 'scan':
            return APIJsonResponse(code=1, data='暂不支持扫描重新执行', log=info)
        RunAnsible.delay(is_sudo, iplist, args, ctype, id=id)
        return APIJsonResponse(data='任务进入后台执行请稍等', log=info)


def testhtml(request):
    return render(request, 'test.html')


def logout(request):
    auth.logout(request)
    return redirect('/login/')
