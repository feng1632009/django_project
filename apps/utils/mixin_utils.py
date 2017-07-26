#!/use/bin/env python
# _*_ coding:utf-8 __
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

#此处回头要去学习下@login_required装饰器的用法和原理 封装成了一个类
class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)