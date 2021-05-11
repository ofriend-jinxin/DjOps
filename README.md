# DjOps 说明
* 主机管理系统，底层调用ansible，不支持windows
* 个人日常闲着没事儿干写的，代码乱七八糟。。希望有大神可以指教改进。
* Python版本： 3.9.2，前端用的layer
* 目前实现的功能
  * 1 主机信息录入和更新 (调用ansible setup 模块)
  * 2 执行shell命令（调用ansible shell模块
  * 3 执行shell脚本（调用ansible script模块）

```
git clone https://github.com/ofriend-jinxin/DjOps.git
cd DjOps
sudo mkdir /etc/ansible/
sudo ln -s ./ansible.cfg /etc/ansible/
pip install  -r requirements.txt
python manage.py  makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
# 页面操作
* admin 后台服务器列表添加机柜，设备类型，应用，网段地址，新建的第一个可以写成默认xx（默认机柜、默认机房。。。。）
* admin 后台添加主机，填写IP 保存
* 前端----资源管理----查看资源----更新


* 目前还有好多问题。比如异步执行动作，页面样式等。慢慢来吧~
![image](https://user-images.githubusercontent.com/28593701/117625902-1b449180-b1a9-11eb-96da-24b684611348.png)

## 2021、5、10 更新
去掉nmap。重新写了个scan扫描端口
优化前端交互 增加搜索分页功能
