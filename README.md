## DjOps 说明
* 主机管理系统，底层调用ansible，不支持windows
* 个人日常闲着没事儿干写的，代码乱七八糟。。希望有大神可以指教改进。
* Python版本： 3.9.2，前端用的layer，测试python3.6 也可以使用
* 主要的的功能
  * 1 主机信息录入和更新 (调用ansible setup 模块)
  * 2 执行shell命令（调用ansible shell模块
  * 3 执行shell脚本（调用ansible script模块）

## 启动
```python
# 拉代码
git clone https://github.com/ofriend-jinxin/DjOps.git
cd DjOps
# 安装依赖
pip install  -r requirements.txt
# 初始化数据库
python manage.py  makemigrations
python manage.py migrate
# 生成默认的测试数据
python manage.py shell
from django.contrib.auth.models import User
User.objects.create_superuser("admin", "admin@admin.com", "admin")
from ops.models import *
App.objects.create(aname='默认应用')
Idc.objects.create(iname='默认机房',iaddress='默认地址',iphone='10010',iemail='admin@admin.com')
Cabinet.objects.create(cname='001',cidc_id=1)
Vlan.objects.create(vnet='192.168.0.0/24',varea='测试')
exit()
# 运行django
python manage.py runserver
# 运行celery
export PYTHONOPTIMIZE=1 
celery -A DjOps  worker  --loglevel=info 
celery -A DjOps   beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

```

* 目前还有好多问题。比如异步执行动作，页面样式等。慢慢来吧~
![image](https://user-images.githubusercontent.com/28593701/118287152-c0db6600-b505-11eb-9b9f-a07c3fd6bd49.png)
![image](https://user-images.githubusercontent.com/28593701/118388837-66531e80-b659-11eb-9937-24c53d57f766.png)


## 2021、5、10 更新
* 去掉nmap。重新写了个scan扫描端口
* 优化前端交互 增加搜索分页功能

## 2021、5、13 更新
* 增加异步执行
* 增加执行结果查询

## 2021、5、14 更新
* templates模板调整（乱调一通，反正能用）
* 优化扫描网段前端展示及记录
* 新增主机查询过滤器

## 2021、5、16 更新
* 优化ansible fork 设置默认为200
* 优化调整静态文件，执行结果查询过滤

## 2021、5、19 更新
* 增加django-celery-beat  django-celery-results 支持后台设置定时任务
* 重写查看结果页面，使用django-celery-results

