from django.urls import path, re_path

from ops import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('assets/', views.AssetsView.as_view(), name='assets'),
    path('resinfo/', views.resinfo, name='resinfo'),
   # path('hostupdate/', views.hostupdate, name='hostupdate'),
    path('scan/', views.ScanView.as_view(), name='scan'),
    path('shell/', views.shell, name='shell'),
    path('runresult/', views.runresult, name='runresult'),
    path('openresult/', views.openresult, name='openresult'),
    path('rerun/', views.rerun, name='rerun'),
    path('test/', views.testhtml, name='test'),

    # path('api/hosts/', mv.HostView.as_view(actions={'get': 'retrieve', 'post': 'create'})),
    path('api/results/', views.ResultView.as_view(actions={'get': 'list'}), name='results'),
    path('api/hosts/', views.HostView.as_view(actions={'get': 'list', 'delete': 'delete','put':'update'}), name='api-hosts'),
    # re_path(r'api/hosts/(?P<pk>\d+)',  views.HostView.as_view(actions={'get': 'retrieve', 'put': 'update'})),


]
