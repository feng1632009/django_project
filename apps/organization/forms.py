# -*- coding: utf-8 -*-
__author__ = 'admin'
__date__ = '17/2/1 下午1:43'

import re
from django import forms

from operation.models import UserAsk

# class UserAskForm(forms.Form):
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     phone = forms.CharField(required=True, min_length=11, max_length=11)
#     course_name = forms.CharField(required=True, min_length=5, max_length=50)
#

class UserAskForm(forms.ModelForm):
    #modelform meta 指定是哪个model 要来生成modelform fields指定需要哪些字段
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):
        """
        验证手机号码是否合法
        """
        #cleaned_data 就是读取表单返回的值，返回类型为字典dict型cleaned_data['mobile'] 验证通过的数据才会保存在这里


        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")