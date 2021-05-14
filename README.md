# DjOps 说明
* 主机管理系统，底层调用ansible，不支持windows
* 个人日常闲着没事儿干写的，代码乱七八糟。。希望有大神可以指教改进。
* Python版本： 3.9.2，前端用的layer，测试python3.6 也可以使用
* 目前实现的功能
  * 1 主机信息录入和更新 (调用ansible setup 模块)
  * 2 执行shell命令（调用ansible shell模块
  * 3 执行shell脚本（调用ansible script模块）

# 启动
```
# 拉代码
git clone https://github.com/ofriend-jinxin/DjOps.git
cd DjOps
# 安装依赖
pip install  -r requirements.txt
# 初始化数据库
python manage.py  makemigrations
python manage.py migrate
python manage.py shell
# 生成默认的测试数据
python manage.py shell
    from django.contrib.auth.models import User
    User.objects.create_superuser("admin", "admin@admin.com", "admin")
    from management.models import AppGroup,Vlaninfo,Idc,Cabinet,HostType
    AppGroup.objects.create(name='默认应用')
    Idc.objects.create(name='默认机房',address='默认地址',phone='10010',email='admin@admin.com')
    Cabinet.objects.create(name='001',idc_id=1)
    Vlaninfo.objects.create(vlan_net='192.168.0.1/24',vlan_area='测试')
    HostType.objects.create(name='虚拟机')
# 运行django
python manage.py runserver
# 运行celery
export PYTHONOPTIMIZE=1 
celery -A celery_tasks.celery  worker -B -l info --beat

```

* 目前还有好多问题。比如异步执行动作，页面样式等。慢慢来吧~
![image](https://user-images.githubusercontent.com/28593701/118287152-c0db6600-b505-11eb-9b9f-a07c3fd6bd49.png)

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
