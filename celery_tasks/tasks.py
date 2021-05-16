from __future__ import absolute_import, unicode_literals
from celery_tasks.celery import app
import datetime,logging
from DjOps import settings
from DjOps.tools.Ansible2 import *
from DjOps.tools.Scan import Scan
from ops import models

ssh_info = settings.SSH_INFO
ssh_user = ssh_info['SSH_USER']
ssh_port = ssh_info['SSH_PORT']
ssh_pass = ssh_info['SSH_PASS']

logger = logging.getLogger('django')


@app.task
def RunAnsible(is_sudo, iplist, args, ctype, id=False):
    start = datetime.datetime.now()
    if is_sudo == 'on':
        become = 'yes'
    else:
        become = None
        is_sudo = 'off'
    if id:
        task_obj = models.RunResult.objects.filter(id=id).first()
        task_obj.result_txt = ('任务正在执行中，请稍后刷新再试，如长时间未返回，请重新执行')
        task_obj.state=1

    else:
        task_obj = models.RunResult(is_sudo=is_sudo, num=len(iplist), ip=",".join(iplist), ctype=ctype,
                                                   args=str(args),
                                                   result_txt='任务正在执行中，请稍后刷新再试，如长时间未返回，请重新执行',state=1)
    task_obj.save()
    ans = MyAnsiable(iplist=iplist, remote_user=ssh_user, become=become, port=ssh_port,
                     remote_password={"conn_pass": ssh_pass})

    ans.run(module='setup')
    if ctype == 'setup':
        ans.run(module=ctype)
    elif ctype == 'playbook':
        ans.playbook(playbooks=args)
    else:
        ans.run(module=ctype, args=args)
    return_dic = ans.get_result()
    logger.info("success:{} failed:{} unreachable:{}".format(len(return_dic['success']), len(return_dic['failed']),
                                                             len(return_dic['unreachable'])))
    success = return_dic['success']
    unreachable = return_dic['unreachable']
    failed = return_dic['failed']
    result = []
    if ctype == 'setup':
        try:
            result_setup = ''
            for ip in iplist:
                if success.get(ip):
                    facts_dics = success[ip]['ansible_facts']
                    logger.info(facts_dics)
                    for network_infos in facts_dics:
                        if 'macaddress' in str(facts_dics[network_infos]) and ip in str(facts_dics[network_infos]):
                            mac = facts_dics[network_infos]['macaddress']
                            netdev = network_infos
                    kernel = facts_dics['ansible_kernel']
                    cpu = facts_dics['ansible_processor'][2]
                    vcpu = facts_dics['ansible_processor_vcpus']
                    system = facts_dics['ansible_distribution'] + facts_dics['ansible_distribution_version']
                    sn = facts_dics['ansible_product_serial']
                    memory = facts_dics['ansible_memory_mb']['real']['total']
                    hostname = facts_dics['ansible_fqdn']
                    equipment_model = facts_dics['ansible_system_vendor']
                    devices = facts_dics['ansible_devices']
                    device = {}
                    for i in devices.keys():
                        if 'storage' in str(devices[i].get('host')) or 'VMware Virtual S' in \
                                str(devices[i].get('model')):
                            device[i] = devices[i]['size']
                    disk_size = 0
                    for diskname in device:
                        size = float(device[diskname].split()[0])
                        danwei = str(device[diskname].split()[1])
                        if "TB" == danwei:
                            disk_size += size * 1024
                        elif "GB" == danwei:
                            disk_size += size
                        elif "KB" == danwei:
                            disk_size += size / 1024

                    disk_size = int(disk_size)
                    ip_obj = models.Hostinfo.objects.get(ip=ip)
                    ip_obj.mac = mac
                    ip_obj.hostname = hostname
                    ip_obj.cpu = cpu
                    ip_obj.vcpu = vcpu
                    ip_obj.disk = disk_size
                    ip_obj.system = system
                    ip_obj.kernel = kernel
                    ip_obj.sn = sn
                    ip_obj.mem = memory
                    ip_obj.equipment_model = equipment_model
                    ip_obj.save()
                    result_setup += 'success {}'.format(ip) + "\r\n"
                elif unreachable.get(ip):
                    result_setup += 'unreachable：{}:{}'.format(ip, unreachable.get(ip)) + "\r\n"
                else:
                    result_setup += 'failed：{}:{}'.format(ip, failed.get(ip)) + "\r\n"

                task_obj.result_txt = '任务执行完成' + "\r\n" + result_setup
                task_obj.state=3

        except Exception as e:
            task_obj.result_txt=e
            task_obj.state=2
    else:
        try:
            for i in iplist:
                resdic = {}
                resstr = ''
                resdic['resstr'] = ""
                cmdstr = "{} $: {}\n".format(i, args)
                resdic['cmdstr'] = cmdstr
                if success.get(i):
                    resstr += str(success.get(i)['stdout']) + "\n"
                    resdic['resstr'] += resstr
                if unreachable.get(i):
                    resstr += str(unreachable.get(i)['msg']) + "\n"
                    resdic['resstr'] += resstr
                if failed.get(i):
                    resstr += str(failed.get(i)['msg']) + "\n"
                    resdic['resstr'] += resstr
                result.append(resdic)
            task_obj.result_txt = result
            task_obj.state=2
        except Exception as e:
            task_obj.result_txt = e
            task_obj.state=3

    end = datetime.datetime.now()
    usetime = float((end - start).total_seconds())
    task_obj.ustime = usetime
    task_obj.save()
    return "run ansible done"

@app.task
def task_scan(vlan, group_id, vlan_id,idc_id):
    start = datetime.datetime.now()
    task_obj = models.RunResult(is_sudo='None', ip=vlan, ctype='scan',
                                args='None',
                                result_txt='任务正在执行中，请稍后刷新再试，如长时间未返回，请重新执行',state=1)
    task_obj.save()

    # 启动扫描程序
    try:
        s = Scan()
        s.run(vlan=vlan, port=ssh_port)
        hosts_list = s.ips
        for ip in hosts_list:
            if not models.Hostinfo.objects.filter(ip=ip).first():
                hostobj = models.Hostinfo(ip=ip, vlan_id=vlan_id, app_id=group_id,idc_id=idc_id)
                hostobj.save()
            else:
                addos = models.Hostinfo.objects.filter(ip=ip).first()
                addos.vlan_id = vlan_id
                addos.app_id = group_id
                addos.idc_id = idc_id
                addos.save()
        logger.info(hosts_list)
        logger.info(len(hosts_list))
        task_obj.result_txt = '扫描完成:'+ str(hosts_list)
        task_obj.num=len(hosts_list)
        task_obj.state=3
    except Exception as e:
        task_obj.result_txt = e
        task_obj.state=2
        logger.error(e)
    end = datetime.datetime.now()
    usetime = float((end - start).total_seconds())
    task_obj.ustime = usetime
    task_obj.save()
    return 'run scan done'