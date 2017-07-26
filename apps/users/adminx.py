# -*- coding: utf-8 -*-
__author__ = 'admin'
__date__ = '17/1/28 下午3:23'


import  xadmin
from xadmin import views
from xadmin.plugins.auth import UserAdmin
from .models import EmailVerifyRecord,Banner, UserProfile

#注册userprofile
class UserProfileAdmin(UserAdmin):
    pass


#xadmin 全局配置 enable_themes 主题功能
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

#定义左上角头部和底部footer显示 menu_style 把APP收起来
class GlobalSettings(object):
    site_title = "慕学后台管理系统"
    site_footer = "幕学在线网"
    menu_style = "accordion"


#定义后台的显示
class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
    model_icon = 'fa fa-address-book-o' #定义后台icon 其他字段一样方法  暂时不做替换


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index','add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index','add_time']


#这两段卸载掉自带的user
# from django.contrib.auth.models import User
# xadmin.site.unregister(User)
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
#注册basesetting
xadmin.site.register(views.BaseAdminView, BaseSetting)
#注册GlobalSettings
xadmin.site.register(views.CommAdminView, GlobalSettings)
#注册userprofile
# xadmin.site.register(UserProfile, UserProfileAdmin)
