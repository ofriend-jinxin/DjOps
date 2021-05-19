from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
import os

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjOps.settings')
app = Celery('DjOps')

app.conf.update(
    # 创建 Celery 实例（也称 app），如果需要使用 Celery，导入即可。
    # celery中间人 redis://redis服务所在的ip地址:端口/数据库号
    # # redis://:password@hostname:port/db_number
    CELERY_BROKER_URL='redis://127.0.0.1:6379/0',
    # celery结果返回，可用于跟踪结果
    # CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/1',
    # 配合django_celery_beat 将结果放到django后台中
    CELERY_RESULT_BACKEND='django-db',
    # 时区
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,

    CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
    # celery_tasks worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
    # CELERYD_CONCURRENCY = 8
    # worker_concurrency = 2

    # celery_tasks worker 每次去BROKER中预取任务的数量-
    CELERY_PREFETCH_MULTIPLIER=4,

    # 每个worker执行了多少任务就会死掉，默认是无限的,释放内存
    CELERYD_MAX_TASKS_PER_CHILD=40,

    # 任务结果保存时间
    CELERY_TASK_RESULT_EXPIRES=60 * 60 * 2,

    # 非常重要,有些情况下可以防止死锁
    CELERY_FORCE_EXECV=True,

    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],

)

# 创建 Celery 实例（也称 app），如果需要使用 Celery，导入即可。
# celery中间人 redis://redis服务所在的ip地址:端口/数据库号
# # redis://:password@hostname:port/db_number
BROKER_URL = 'redis://127.0.0.1:6379/0'
# celery结果返回，可用于跟踪结果
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

# 第一个参数为当前模块的名称，只有在 __main__ 模块中定义任务时才会生产名称。
# include 参数是程序启动时导入的模块列表，可以该处添加任务模块，便于职程能够对应相应的任务。

app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery加载所有注册的应用
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.conf['imports'] = ['project.tasks', ]  # tasks文件的位置，不写这个会报KeyError
# Optional configuration, see the application user guide.
# 定时任务
# app.conf.beat_schedule = {
#    "crontab_cron_task": {
#        "task": "project.tasks.cron_task",
#        # "schedule": crontab(hour=11, minute=28),# 每天的11点28分执行一次任务
#        "schedule": crontab(minute="*/1"),  # 每分钟
#        "args": (),  # 参数
#    }
# }
