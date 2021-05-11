import socket
import threading
import IPy


class Scan:

    def __init__(self):
        # 创建接收路由列表
        self.ips = []
        # 创建互斥锁
        self.lock = threading.Lock()

    # 定义查询路由函数
    def run(self,vlan,port):
        # 存放线程列表池
        self.IPylist = IPy.IP(vlan)
        all_threads = []
        for ip in self.IPylist:
            # 循环创建线程去链接该地址
            ip = str(ip)
            t = threading.Thread(target=self.check_ip, args=(ip, int(port)))
            t.start()
            # 把新建的线程放到线程池
            all_threads.append(t)
        # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
        for t in all_threads:
            t.join()

    # 创建访问IP列表方法
    def check_ip(self, new_ip, port):
        # 创建TCP套接字，链接新的ip列表
        scan_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置链接超时时间
        scan_link.settimeout(5)
        # 链接地址(通过指定我们 构造的主机地址，和扫描指定端口)
        result = scan_link.connect_ex((new_ip, port))
        #
        scan_link.close()
        # print(result)
        # 判断链接结果
        if result == 0:
            # 加锁
            self.lock.acquire()
            self.ips.append(new_ip)
            # 释放锁
            self.lock.release()



# 启动程序入口
if __name__ == '__main__':
    # 启动扫描程序
    s=Scan()
    print('开始扫描')
    s.run(vlan='10.57.16.0/24',port='22')
    print(s.ips)

