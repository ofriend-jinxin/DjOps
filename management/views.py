from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from django.forms.models import model_to_dict
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
import json,ast

from DjOps.tools.Scan import Scan
from rest_framework.viewsets import ViewSet

from management import models
from management import appseries
from rest_framework.response import Response
from rest_framework import status
import os
from django.views.decorators.clickjacking import xframe_options_exempt

from DjOps import settings
from celery_tasks.tasks import RunAnsible


from rest_framework.pagination import PageNumberPagination
import logging
logger = logging.getLogger('django')

# Create your views here.
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


def return400():
    return APIResponse(results="请求的数据不存在", status=status.HTTP_400_BAD_REQUEST, msg="失败")


class APIJsonResponse(JsonResponse):
    def __init__(self, data, code=0, log=None, **kwargs):
        return_data = {
            'code': code,
            'log': log,
            'msg': data,
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


class CuseomPagination(PageNumberPagination):
    page_size = 100  # 每页显示多少条
    page_query_param = 'page'  # /url/?page=100
    page_size_query_param = 'limit'  # /url/limit=10 前端控制每页显示最大条目数

    def get_paginated_response(self, data):
        return APIResponse(data, count=self.page.paginator.count)


def pagination_response(query_set, request, serializer):
    pagination = CuseomPagination()
    pagination_queryset = pagination.paginate_queryset(query_set, request)
    data = serializer(pagination_queryset, many=True).data
    return pagination.get_paginated_response(data)




@login_required
def index(request):
    thepage = {}
    thepage['h1'] = '主页'
    thepage['name'] = '主页'
    allmachine = Hostinfo.objects.all().count()
    phymachine = Hostinfo.objects.all().count()
    vmmachine = Hostinfo.objects.all().count()
    groupnum = AppGroup.objects.all().count()
    count = {"all": allmachine, "phy": phymachine, "vm": vmmachine, "group": groupnum}

    return render(request, 'index.html', {'thepage': thepage, 'count': count})


@login_required
def allinfo(request):
    thepage = {}
    thepage['h1'] = '查看资源'
    thepage['name'] = '查看资源'
    allinfo = Hostinfo.objects.all()
    return render(request, 'allos.html', {'allinfo': allinfo, 'thepage': thepage})


# 新建一个过滤器
from django_filters import rest_framework as filters


class HostFilter(filters.FilterSet):
    ip = filters.CharFilter(field_name='ip', lookup_expr='icontains')
    name = filters.NumberFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = models.Hostinfo
        fields = ['ip', 'name']


class HostView(ViewSet):  # ViewSet
    filterset_class = HostFilter
    def list(self, request):
        hostinfo = models.Hostinfo.objects.all()
        filterset_class = HostFilter(request.GET, hostinfo)
        return pagination_response(filterset_class.qs, request, appseries.HostinfoSerializer)


def login(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            message = '用户名或密码不正确！'
            return render(request, 'login/login.html', {'message': message})

    return render(request, 'login/login.html')


@login_required
@is_super_user
def resinfo(request):
    thepage = {}
    thepage['h1'] = '详情'
    thepage['name'] = '详细信息'
    last_html = request.META.get('HTTP_REFERER', '/')
    if request.method == 'GET':
        osid = request.GET.get('osid')
        try:
            os_info = Hostinfo.objects.get(id=osid)
            os_info = model_to_dict(os_info)
            groupinfo = AppGroup.objects.all()
            vlaninfo = Vlaninfo.objects.all()
            app = AppGroup.objects.get(id=os_info['app']).name
            print('666')
            return render(request, 'resinfo.html',
                          {'osinfo': os_info, 'os_group': app, 'thepage': thepage, 'groupinfo': groupinfo,
                           'vlaninfo': vlaninfo})
        except Exception as e:
            print(e)
            return HttpResponseRedirect(last_html)
    elif request.method == 'POST':
        try:
            print(request.POST)
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
            print(e, '----')
            return HttpResponseRedirect(last_html)


@login_required
@is_super_user
@xframe_options_exempt
def hostupdate(request):
    ip = request.GET.get('ip')
    if ip != '':
        iplist = str(ip).split(',')
        print(iplist)
        RunAnsible.delay(is_sudo='on',iplist=iplist[:-1], ctype='setup', args=None)
        return APIJsonResponse(data='任务进入后台执行请稍等', log='666')


@login_required
@is_super_user
def hostdel(request):
    ip = request.GET.get('ip')
    try:
        Hostinfo.objects.filter(ip=ip).delete()
        return APIJsonResponse(data='操作成功')
    except Exception as e:
        return APIJsonResponse(code=1, data='操作失败', log=e)


@login_required
@is_super_user
def scan(request):
    thepage = {}
    thepage['h1'] = '扫描'
    thepage['name'] = '网段扫描'
    if request.method == 'POST':
        vlan = request.POST.get('lan')
        group = request.POST.get('comment')
        vlanobj = Vlaninfo.objects.get(vlan_net=vlan)
        if vlanobj:
            # 启动扫描程序
            s = Scan()
            print('开始扫描')
            s.run(vlan='10.57.16.0/24', port='22')
            hosts_list = s.ips
            print(hosts_list)
            for ip in hosts_list:
                groupobj = AppGroup.objects.get(name=group)
                if not Hostinfo.objects.filter(ip=ip):
                    Hostinfo.objects.create(ip=ip, vlan=vlanobj, app=groupobj)
                    print("create", ip, groupobj, vlanobj)
                else:
                    addos = Hostinfo.objects.get(ip=ip)
                    addos.vlan = vlanobj
                    addos.app = groupobj
                    addos.save()

                    print("edit", ip, groupobj, vlanobj)
            # last_html = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect('/allinfo/')
    vlaninfo = Vlaninfo.objects.all()
    groupinfo = AppGroup.objects.all()
    return render(request, 'scan.html', {'vlaninfo': vlaninfo, 'groupinfo': groupinfo, 'thepage': thepage})


def get_sh_file(fdir, fstr):
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
@xframe_options_exempt
def shell(request):
    fileList = []
    shell_res = []
    if request.method == 'POST':
        iplist = request.POST.getlist('ip')
        ctype = request.POST.get('type')
        is_sudo = request.POST.get('open')
        print(iplist)
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
            RunAnsible.delay(is_sudo=is_sudo,iplist=iplist,args=command,ctype=ctype)
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
    return render(request, 'shell.html',
                  {'filelist': fileList, 'iplist': iplist, 'shell_res': shell_res, 'run_type': ctype})


class ResultView(ViewSet):
    def list(self, request):
        RsultInfo = models.RunResult.objects.all()
        return pagination_response(RsultInfo, request, appseries.RunResultSerializer)


@login_required
@is_super_user
@xframe_options_exempt
def runresult(request):
    delid = request.GET.get('delid','')
    if len(delid) > 0:

        for id in str(delid).split(',')[:-1]:
            models.RunResult.objects.get(id=id).delete()
        return APIJsonResponse(data='操作成功')
    return render(request, 'runresult.html')
@login_required
@is_super_user
@xframe_options_exempt
def openresult(request):
    id = request.GET.get('id')
    if id:
        obj = models.RunResult.objects.get(id=id)
        result_txt = obj.result_txt
        if '任务正在执行中' in result_txt or '任务执行完成' in result_txt:
            types='str'
        else:
            types='list'
            result_txt=ast.literal_eval(result_txt)
        return render(request,'openresult.html',{'result':result_txt,'types':types})

@login_required
@is_super_user
@xframe_options_exempt
def rerun(request):
    id = request.GET.get('id')
    if id:
        task_obj = models.RunResult.objects.get(id=id)
        iplist = task_obj.iplist.split(',')
        is_sudo = task_obj.is_sudo
        ctype = task_obj.ctype
        args=task_obj.args
        RunAnsible.delay(is_sudo,iplist, args, ctype,id=id)
        return APIJsonResponse(data='任务进入后台执行请稍等', log='666')

def logout(request):
    auth.logout(request)
    return redirect('/login/')
