from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
import os
# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjOps.settings')

# 创建 Celery 实例（也称 app），如果需要使用 Celery，导入即可。
# celery中间人 redis://redis服务所在的ip地址:端口/数据库号
# # redis://:password@hostname:port/db_number
BROKER_URL = 'redis://127.0.0.1:6379/0'
# celery结果返回，可用于跟踪结果
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

# 第一个参数为当前模块的名称，只有在 __main__ 模块中定义任务时才会生产名称。
# include 参数是程序启动时导入的模块列表，可以该处添加任务模块，便于职程能够对应相应的任务。
app = Celery('tasks')
app.config_from_object('celery_tasks.config')
# app.conf['imports'] = ['project.tasks', ]  # tasks文件的位置，不写这个会报KeyError
# Optional configuration, see the application user guide.
# 定时任务需要添加
app.autodiscover_tasks(['celery_tasks'])

# 定时任务
# app.conf.beat_schedule = {
#    "crontab_cron_task": {
#        "task": "project.tasks.cron_task",
#        # "schedule": crontab(hour=11, minute=28),# 每天的11点28分执行一次任务
#        "schedule": crontab(minute="*/1"),  # 每分钟
#        "args": (),  # 参数
#    }
# }

# Celery加载所有注册的应用
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
