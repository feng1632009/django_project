# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals

from django.apps import AppConfig

#后台显示中文名
class OperationConfig(AppConfig):
    name = 'operation'
    verbose_name = u"用户操作"
