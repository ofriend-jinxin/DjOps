from django.urls import path, re_path

from ops import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    # 资源展示界面
    path('assets/', views.AssetsView.as_view(), name='assets'),
    path('resinfo/', views.resinfo, name='resinfo'),
    # path('hostupdate/', views.hostupdate, name='hostupdate'),
    # 扫描网段界面
    path('scan/', views.ScanView.as_view(), name='scan'),
    # 执行action界面
    path('action/', views.ActionView.as_view(), name='action'),
    # 执行动作结果页面
    path('tasks/', views.TaskView.as_view(), name='runlog'),



    path('test/', views.testhtml, name='test'),

    # path('api/hosts/', mv.HostView.as_view(actions={'get': 'retrieve', 'post': 'create'})),
#    path('api/runlogs/', views.RunlogViewSet.as_view(actions={'get': 'list', 'delete': 'delete'}), name='api-runlogs'),
    path('api/hosts/', views.HostView.as_view(actions={'get': 'list', 'delete': 'delete', 'put': 'put'}),name='api-hosts'),
    path('api/tasks/', views.TaskViewSet.as_view(actions={'get': 'list', 'delete': 'delete', 'post': 'post'}),name='api-tasks'),
    # re_path(r'api/hosts/(?P<pk>\d+)',  views.HostView.as_view(actions={'get': 'retrieve', 'put': 'update'})),

]
