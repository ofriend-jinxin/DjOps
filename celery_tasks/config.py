# 创建 Celery 实例（也称 app），如果需要使用 Celery，导入即可。
# celery中间人 redis://redis服务所在的ip地址:端口/数据库号
# # redis://:password@hostname:port/db_number
broker_url = 'redis://127.0.0.1:6379/0'
# celery结果返回，可用于跟踪结果
backend = 'redis://127.0.0.1:6379/1'

# celery_tasks worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
# CELERYD_CONCURRENCY = 8
worker_concurrency = 2

# celery_tasks worker 每次去BROKER中预取任务的数量-
worker_prefetch_multiplier = 4

# 每个worker执行了多少任务就会死掉，默认是无限的,释放内存
worker_max_tasks_per_child = 200

# 任务结果保存时间
worker_task_result_expires = 60 * 60 * 2

# 非常重要,有些情况下可以防止死锁
worker_force_execv = True

# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
worker_disable_rate_limits = True

# 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
worker_result_serializer = "json"

# 设置时区，默认UTC
timezone = 'Asia/Shanghai'

# tasks文件的位置，不写这个会报KeyError
imports = ['celery_tasks.tasks']

