import re, threading
from ops import models


class SetupSave:
    def __init__(self, iplist, success, unreachable, failed):
        self.iplist = iplist
        self.success = success
        self.unreachable = unreachable
        self.failed = failed
        # 创建结果
        self.result_setup = ''
        self.exception = ''
        # 创建互斥锁
        self.lock = threading.Lock()

    # 定义生成多线程函数
    def run(self):

        all_threads = []
        for ip in self.iplist:
            # 循环创建线程
            ip = str(ip)
            t = threading.Thread(target=self.update_save, args=(ip,))
            t.start()
            # 把新建的线程放到线程池
            all_threads.append(t)
        # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
        for t in all_threads:
            t.join()

    # 创建执行函数
    def update_save(self, ip):
        try:
            if self.success.get(ip):
                mac = ''
                facts_dics = self.success[ip].get('ansible_facts')
                kernel = facts_dics.get('ansible_kernel')
                cpu = facts_dics.get('ansible_processor')[2]
                vcpu = facts_dics.get('ansible_processor_vcpus')
                system = facts_dics.get('ansible_distribution') + facts_dics.get('ansible_distribution_version')
                sn = facts_dics.get('ansible_product_serial')
                memory = facts_dics.get('ansible_memory_mb').get('real').get('total')
                hostname = facts_dics.get('ansible_fqdn')
                system_vendor = facts_dics.get('ansible_system_vendor')
                devices = facts_dics.get('ansible_devices')
                product_name = facts_dics.get('ansible_product_name')
                bios_vendor = facts_dics.get('ansible_bios_vendor')
                if "kvm" in str(product_name).lower() or 'qemu' in str(system_vendor).lower():
                    htype = 3
                #elif 'host' == str(facts_dics.get('ansible_virtualization_role')):
                #    htype = 2
                else:
                    htype = 1
                disk_size = 0
                for k, v in devices.items():
                    if k[0:2] in ['sd', 'hd', 'ss', 'vd', 'xv', 'nv']:
                        disk = int((int(v.get('sectors')) * int(v.get('sectorsize'))) / 1024 / 1024 / 1024)
                        disk_size = disk_size + disk
                # 获取网卡
                nks = []
                for nk in facts_dics.keys():
                    if re.match(r"^ansible_(eth|bind|eno|ens|em|bond)\d+?", nk):
                        device = facts_dics.get(nk).get('device')
                        try:
                            address = facts_dics.get(nk).get('ipv4').get('address')
                        except:
                            address = 'unkown'
                        macaddress = facts_dics.get(nk).get('macaddress')
                        module = facts_dics.get(nk).get('module')
                        mtu = facts_dics.get(nk).get('mtu')
                        if facts_dics.get(nk).get('active'):
                            active = 1
                        else:
                            active = 0
                        if macaddress == ip:
                            mac = macaddress
                        nks.append(
                            {"device": device, "address": address, "macaddress": macaddress, "module": module,
                             "mtu": mtu, "active": active})
                hostobj = models.Hostinfo.objects.get(hip=ip)
                hostobj.hmac = mac
                hostobj.hhostname = hostname
                hostobj.hcpu = cpu
                hostobj.hvcpu = vcpu
                hostobj.hdisk = disk_size
                hostobj.hsystem = system
                hostobj.hkernel = kernel
                hostobj.hproduct_name = product_name
                hostobj.hsn = sn
                hostobj.hbios_vendor = bios_vendor
                hostobj.hmem = memory
                hostobj.hsystem_vendor = system_vendor
                hostobj.hnotes = nks
                hostobj.htype = htype
                self.lock.acquire()
                hostobj.save()
                self.lock.release()
                self.result_setup += 'success {}'.format(ip) + "\r\n"
            elif self.unreachable.get(ip):
                self.result_setup += 'unreachable：{}:{}'.format(ip, self.unreachable.get(ip)) + "\r\n"
            else:
                self.result_setup += 'failed：{}:{}'.format(ip, self.failed.get(ip)) + "\r\n"
        except Exception as e:
            self.exception += e
