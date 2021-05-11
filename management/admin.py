from django.contrib import admin
import inspect
from management import models


# 找出模块里所有的类名

@admin.register(models.Cabinet)
class Cabinetadmin(admin.ModelAdmin):
    display = ['name']
    list_display = display
    search_fields = display


@admin.register(models.Idc)
class Idcadmin(admin.ModelAdmin):
    display = ['name']
    list_display = display
    search_fields = display


@admin.register(models.Hostinfo)
class Hostoadmin(admin.ModelAdmin):
    list_per_page = 10
    display = [f.name for f in models.Hostinfo._meta.get_fields()]
    list_display = display
    search_fields = display


@admin.register(models.AppGroup)
class AppGroupadmin(admin.ModelAdmin):
    display = ['name']
    list_display = display
    search_fields = display


@admin.register(models.Vlaninfo)
class Vlaninfoadmin(admin.ModelAdmin):
    display = ['vlan_area', 'vlan_net']
    list_display = display
    search_fields = display


@admin.register(models.HostType)
class HostTypeoadmin(admin.ModelAdmin):
    display = ['name']
    list_display = display
    search_fields = display

# @admin.register(Osinfo)
# class Osinfoadmin(admin.ModelAdmin):
#     list_display = ['os_ip', 'os_sn', 'os_hostname']
#     search_fields = ['os_ip', 'os_sn','os_hostname']
