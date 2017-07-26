# -*- coding: utf-8 -*-
__author__ = 'admin'
__date__ = '17/1/29 下午7:22'
#form表单中的input name字段与form定义的字段一定要一致不然无法做表单验证
from django import forms
#引入验证码字段
from captcha.fields import CaptchaField

from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    #error_messages自定义错误信息 invalid必须那样写
    captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    #error_messages自定义错误信息 invalid必须那样写
    captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})

#密码修改

class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


#上传文件表单
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


#个人信息保存表单
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birday', 'address', 'mobile']