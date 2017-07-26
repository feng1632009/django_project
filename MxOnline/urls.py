# -*- coding: utf-8 -*-
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
#专门处理静态文件的view 注意 根目录的url前面不用加/
from django.views.generic import TemplateView
import xadmin
#处理静态文件的serve方法
from django.views.static import serve
#url调用的时候调用类的as view方法 所以必须要加括号
from  users.views import LogoutView,  LoginView,RegisterView,ActiveUserView,ForgetPwdView,ResetView, ModifyPwdView
from users.views import IndexView
from organization.views import OrgView
from MxOnline.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),

    url('^$', IndexView.as_view(), name="index"),
    url('^login/$', LoginView.as_view(), name="login"),#登录
    url('^logout/$', LogoutView.as_view(), name="logout"),#登出
    url('^register/$', RegisterView.as_view(), name="register"),
    url(r'^captcha/', include('captcha.urls')),
    #提取一个变量作为参数，符合正则表达式取到的并放到active_code里面
    url(r'^active/(?P<active_code>.*)/$',ActiveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),

    #课程机构url配置总路由 路由分发 命名空间+冒号 +url的名称
    url(r'^org/', include('organization.urls', namespace="org")),

    # 课程相关url配置总路由 路由分发 命名空间+冒号 +url的名称
    url(r'^course/', include('courses.urls', namespace="course")),

    # 用户相关url配置总路由 路由分发 命名空间+冒号 +url的名称
    url(r'^users/', include('users.urls', namespace="users")),

    #配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT}),

    #url(r'^static/(?P<path>.*)$', serve, {"document_root":STATIC_ROOT})

    #富文本相关url
    url(r'uditor/', include('DjangoUeditor.urls')),

]

#全局404页面配置 变量是固定写法
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'