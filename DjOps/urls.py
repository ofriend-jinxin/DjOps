"""DjOps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path

urlpatterns = [
    path('admin/', admin.site.urls),
]

from management import views as mv
from django.conf.urls import handler404, handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', mv.login),
    path('logout/', mv.logout),
    path('', mv.index),
    path('allinfo/', mv.allinfo),
    path('resinfo/', mv.resinfo),
    path('hostupdate/', mv.hostupdate),
    path('hostdel/',mv.hostdel),
    path('scan/', mv.scan),
    path('shell/', mv.shell),

    #path('api/hosts/', mv.HostView.as_view(actions={'get': 'retrieve', 'post': 'create'})),

    path('api/hosts/', mv.HostView.as_view(actions={'get': 'list'})),
    re_path('api/hosts/(?P<pk>\d+)',
            mv.HostView.as_view(actions={'get': 'retrieve','put':'update'})),

]