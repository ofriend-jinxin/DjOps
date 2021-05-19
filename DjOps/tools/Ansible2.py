import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible import context
from ansible.utils.vars import load_extra_vars
from ansible.utils.vars import load_options_vars
import ansible.constants as C
import datetime


class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.name] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host
        self.host_ok[host.name] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.name] = result


class MyAnsiable():
    def __init__(self,
                 connection='smart',  # 连接方式 local 本地方式，smart ssh方式
                 remote_user=None,  # ssh 用户
                 remote_password=None,  # ssh 用户的密码，应该是一个字典, key 必须是 conn_pass
                 private_key_file=None,  # 指定自定义的私钥地址
                 module_path=None,  # 模块路径，可以指定一个自定义模块的路径
                 become=None, become_method='sudo', become_user='root',  # 是否提权
                 check=False,
                 diff=False,
                 listhosts=None, listtasks=None, listtags=None,
                 verbosity=3,
                 syntax=None,
                 start_at_task=None,
                 forks=200,
                 poll_interval=15,
                 port=None,
                 iplist=None, ):  # inventory iplist
        # 函数文档注释
        """
        初始化函数，定义的默认的选项值，
        在初始化的时候可以传参，以便覆盖默认选项的值
        """
        C.HOST_KEY_CHECKING = False
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            private_key_file=private_key_file,
            module_path=module_path,
            become=become,
            become_method=become_method,
            become_user=become_user,
            verbosity=verbosity,
            listhosts=listhosts,
            listtasks=listtasks,
            listtags=listtags,
            syntax=syntax,
            forks=forks,
            check=check,
            diff=diff,
            poll_interval=poll_interval,
            start_at_task=start_at_task,
            timeout=10,  # ssh超时时间
        )

        # 实例化数据解析器
        self.loader = DataLoader()
        # 实例化 资产配置对象
        # self.iplist = ",".join(iplist) + ","
        # self.inventory = InventoryManager(loader=self.loader, sources=self.iplist)
        self.inventory = InventoryManager(loader=self.loader)
        for ip in iplist:
            self.inventory.add_host(host=ip, group='all', port=port)
        # 设置密码
        self.passwords = remote_password

        # 实例化回调插件对象
        self.results_callback = ResultCallback()

        # 变量管理器
        self.variable_manager = VariableManager(self.loader, self.inventory)

    def run(self, gether_facts="no", module="ping", args='', task_time=0):
        """
        参数说明：
        task_time -- 执行异步任务时等待的秒数，这个需要大于 0 ，等于 0 的时候不支持异步（默认值）。这个值应该等于执行任务实际耗时时间为好
        """
        play_source = dict(
            name="Ansible play",
            hosts='all',
            gather_facts=gether_facts,
            tasks=[
                # 这里每个 task 就是这个列表中的一个元素，格式是嵌套的字典
                # 也可以作为参数传递过来，这里就简单化了。
                {"action": {"module": module, "args": args}, "async": task_time, "poll": 0}
            ])

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback,
                forks=context.CLIARGS.get('forks')
            )
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def playbook(self, playbooks):
        """
        Keyword arguments:
        playbooks --  需要是一个列表类型
        """

        playbook = PlaybookExecutor(playbooks=[playbooks],
                                    inventory=self.inventory,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader,
                                    passwords=self.passwords)
        # 使用回调函数
        playbook._tqm._stdout_callback = self.results_callback
        result = playbook.run()

    def get_result(self):
        result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.results_callback.host_ok.items():
            result_raw['success'][host] = result._result
        for host, result in self.results_callback.host_failed.items():
            result_raw['failed'][host] = result._result
        for host, result in self.results_callback.host_unreachable.items():
            result_raw['unreachable'][host] = result._result
        return result_raw


if __name__ == '__main__':
    hostlist = []
    for i in range(10, 100):
        hostlist.append("{}{}".format('192.168.101.', i))

    hostlist = ['1.1.1.1']
    ans = MyAnsiable(iplist=hostlist, remote_user='root', become='yes', port='22',
                     remote_password={"conn_pass": '123456'})

    # ans.run(module='script', args='/ls_root.sh')
    # ans.run(module='shell', args='netstat -ntlp')
    ans.run(module='setup')
    print(ans.get_result())
    # ans.playbook(playbooks='/test.yml') #用时：04.744813
