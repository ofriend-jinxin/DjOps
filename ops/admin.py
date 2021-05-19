from django.contrib import admin
import inspect
from ops import models



# 找出模块里所有的类名
# @admin.register(models.RunResult)
# class RunResult(admin.ModelAdmin):
#     display = ['id']
#     list_display = display
#     search_fields = display

@admin.register(models.Cabinet)
class Cabinetadmin(admin.ModelAdmin):
    display = ['cname']
    list_display = display
    search_fields = display


@admin.register(models.Idc)
class Idcadmin(admin.ModelAdmin):
    display = ['iname']
    list_display = display
    search_fields = display


@admin.register(models.Hostinfo)
class Hostoadmin(admin.ModelAdmin):
    list_per_page = 10
    display = [f.name for f in models.Hostinfo._meta.get_fields()]
    list_display = display
    search_fields = display


@admin.register(models.App)
class AppGroupadmin(admin.ModelAdmin):
    display = ['aname']
    list_display = display
    search_fields = display


@admin.register(models.Vlan)
class Vlaninfoadmin(admin.ModelAdmin):
    display = ['varea', 'vnet']
    list_display = display
    search_fields = display


# @admin.register(Osinfo)
# class Osinfoadmin(admin.ModelAdmin):
#     list_display = ['os_ip', 'os_sn', 'os_hostname']
#     search_fields = ['os_ip', 'os_sn','os_hostname']
