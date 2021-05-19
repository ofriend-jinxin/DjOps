
import socket
import threading
import IPy

class Telnet:

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
                t = threading.Thread(target=self.check_ip_port, args=(ip, int(port)))
                t.start()
                # 把新建的线程放到线程池
                all_threads.append(t)
            # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
            for t in all_threads:
                t.join()

        def check_ip_port(self,ip, port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
            sock.settimeout(0.1)  # 设置延时时间
            try:
                result = sock.connect_ex((ip, port))
                if result == 0:  # 如果连接成功，返回值为0
                    self.ips.append(ip)  # 如果端口开放，就把端口port赋给openPort
            except:
                pass
            sock.close()  # 关闭套接字
# 启动程序入口
if __name__ == '__main__':
    # 启动扫描程序
    t=Telnet()
    print('开始扫描')
    t.run(vlan='192.168.0.0/24',port=22)
    print(len(t.ips),t.ips)

