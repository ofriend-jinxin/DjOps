from __future__ import absolute_import, unicode_literals
from django_celery_results.models import TaskResult
from DjOps.celery import app
import logging, json
from DjOps import settings
from DjOps.tools.Ansible2 import *
from DjOps.tools.Scan import Scan
from DjOps.tools.SetupSave import SetupSave
from ops import models

ssh_info = settings.SSH_INFO
ssh_user = ssh_info['SSH_USER']
ssh_pass = ssh_info['SSH_PASS']
ssh_port = ssh_info['SSH_PORT']

logger = logging.getLogger('django')

@app.task
def ActionRun(**kwargs):
    ssh_port = ssh_info['SSH_PORT']
    is_sudo = kwargs.get('is_sudo')
    iplist = kwargs.get('iplist')
    args = kwargs.get('args')
    ctype = kwargs.get('ctype')

    if is_sudo == 'on':
        become = 'yes'
    else:
        become = None

    if ctype == 'setup':
        ans = MyAnsiable(iplist=iplist, remote_user=ssh_user, become='yes', port=ssh_port,
                         remote_password={"conn_pass": ssh_pass})
        ans.run(module='setup')

        return_dic = ans.get_result()

        logger.info("success:{} failed:{} unreachable:{}".format(len(return_dic['success']), len(return_dic['failed']),
                                                                 len(return_dic['unreachable'])))
        success = return_dic.get('success')
        unreachable = return_dic.get('unreachable')
        failed = return_dic.get('failed')

        s = SetupSave(iplist, success, unreachable, failed)
        s.run()
        errorlog = s.exception
        logger.error(errorlog)

        return (return_dic)

    elif ctype == 'playbook':
        ans = MyAnsiable(iplist=iplist, remote_user=ssh_user, become=become, port=ssh_port,
                         remote_password={"conn_pass": ssh_pass})
        ans.playbook(playbooks=args)
    else:
        ans = MyAnsiable(iplist=iplist, remote_user=ssh_user, become=become, port=ssh_port,
                         remote_password={"conn_pass": ssh_pass})
        ans.run(module=ctype, args=args)

    return_dic = ans.get_result()
    logger.info("success:{} failed:{} unreachable:{}".format(len(return_dic['success']), len(return_dic['failed']),
                                                             len(return_dic['unreachable'])))
    return (return_dic)
    #
    # for i in iplist:
    #     resdic = {}
    #     resstr = ''
    #     resdic['resstr'] = ""
    #     cmdstr = "{} $: {}\n".format(i, args)
    #     resdic['cmdstr'] = cmdstr
    #     if success.get(i):
    #         resstr += str(success.get(i)['stdout']) + "\n"
    #         resdic['resstr'] += resstr
    #     if unreachable.get(i):
    #         resstr += str(unreachable.get(i)['msg']) + "\n"
    #         resdic['resstr'] += resstr
    #     if failed.get(i):
    #         resstr += str(failed.get(i)['msg']) + "\n"
    #         resdic['resstr'] += resstr
    #     result.append(resdic)
    # return result


@app.task
def task_scan(**kwargs):
    vlan = kwargs.get('vlan')
    group_id = kwargs.get('group_id')
    vlan_id = kwargs.get('vlan_id')
    idc_id = kwargs.get('idc_id')
    # 启动扫描程序
    s = Scan()
    s.run(vlan=vlan, port=ssh_port)
    s.ips = []
    s.run(vlan=vlan, port=ssh_port)
    logger.info("scan_res:{}".format(s.ips))
    for ip in s.ips:
        if not models.Hostinfo.objects.filter(hip=ip).first():
            models.Hostinfo.objects.create(hip=ip, hvlan_id=vlan_id, happ_id=group_id, hidc_id=idc_id)
        else:
            hostobj = models.Hostinfo.objects.filter(hip=ip).first()
            hostobj.hvlan_id = vlan_id
            hostobj.happ_id = group_id
            hostobj.hidc_id = idc_id
            hostobj.save()

    return ({"success": s.ips})


