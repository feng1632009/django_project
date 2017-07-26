# -*- coding: utf-8 -*-
import  json
from django.shortcuts import render
#引入django auth 用户认证 有一项通过则返回一个user类对象 没有返回异常 返回一个None
#命名规范不要与系统变量一致
from django.contrib.auth.backends import ModelBackend
#并级
from django.db.models import Q
#类的通用视图
from django.views.generic.base import View
#对明文进行加密
from django.contrib.auth.hashers import make_password
from django.contrib.auth import  authenticate, login,logout
from django.http import  HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile,EmailVerifyRecord
from .forms import LoginForm, RegisterForm,ForgetForm, ModifyPwdForm,UploadImageForm
from .forms import UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import  LoginRequiredMixin
from operation.models import UserCourse, UserFavourite,UserMessage
from organization.models import CourseOrg,Teacher
from courses.models import Course
from .models import Banner

#让邮箱等user可登录的类
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


#验证码激活逻辑
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, "login.html")


#注册逻辑
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form':register_form})
#通过验证之后 实例化一个user_profile
    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form":register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            #is_active这个字段数据库默认为True,用户未激活设置为False
            user_profile.is_active = False
            #因为后台密码是密文所以对取出来的password进行加密处理
            user_profile.password = make_password(pass_word)
            user_profile.save()

            #写入欢迎注册信息
            user_message = UserMessage()
            #新生成的用户因为是int类型不是外键所以传id
            user_message.user = user_profile.id
            user_message.message = "欢迎注册幕学在线网"
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form":register_form})


#登出逻辑
class LogoutView(View):
    def get(self, request):
        logout(request)#重定向reverse反向解析url 不懂谷歌
        return HttpResponseRedirect(reverse("index"))



#登录逻辑
class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            #必须设定默认值而且是固定写法
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                    #登录的时候不能在render要重定向 不然只是渲染个没有数据的空页面
                    # return render(request, "index.html")
                else:
                    return render(request, "login.html", {"msg": "未激活!"})
            else:
                return render(request, "login.html", {"msg": "用户名或者密码错误!"})
        else:
            return render(request, "login.html", {"login_form":login_form})

#忘记密码
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html",{"forget_form":forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_register_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})



class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, 'active_fail.html')
        return render(request, "login.html")

#修改用户密码
class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"msg":"密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return  render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "modify_form":modify_form})




#权限控制必须登录才能访问的view 继承LoginRequiredMixin
class UserinfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return  render(request, 'usercenter-info.html', {})
    # form是修改不是新增 如果不指定instance会新增加一个用户
    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:#dict转化为str
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')








class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """

    def post(self, request):
        # image_form = UploadImageForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse("{'status':'success'}", content_type='application/json')
        else:
            return HttpResponse("{'status':'fail'}", content_type='application/json')








# 个人中心修改用户密码
class UpdatePwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail", "msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success", "msg":"密码修改成功"}', content_type='application/json')
        else:#json 用法 字典直接转变成字符串
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')




class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_email(email, "update_email")

        return HttpResponse('{"status":"success"}', content_type='application/json')



class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改个人邮箱
    """
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')




#需要登录才能查看的页面 所以一样继承LoginrequireMIXin
class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html',{
            "user_courses":user_courses
        })




class MyFavOrgView(LoginRequiredMixin, View):
    """
    我收藏的课程机构
    """

    def get(self, request):#查询条件就是课程的类别2 model定义
        org_list =[]
        fav_orgs = UserFavourite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            "org_list": org_list
        })





class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我收藏的授课讲师

    收藏的 fav_id ，type 等于 1时，fav_id 就是当前课程的id

    收藏的 fav_id ，type 等于 2时，fav_id 就是当前课程机构的id

    收藏的 fav_id ，type 等于 3时，fav_id 就是当前讲师的id
    """
    #看不懂fav_id看这里！机构点击的收藏 机构的type是1  fav_id就是当前机构的id   数据库查询的时候遍历的时候 type是1 fav_id 就能查询到
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavourite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list": teacher_list
        })






class MyFavCourseView(LoginRequiredMixin, View):
    """
    我收藏的课程

    收藏的 fav_id ，type 等于 1时，fav_id 就是当前课程的id

    收藏的 fav_id ，type 等于 2时，fav_id 就是当前课程机构的id

    收藏的 fav_id ，type 等于 3时，fav_id 就是当前讲师的id
    """

    # 看不懂fav_id看这里！机构点击的收藏 机构的type是1  fav_id就是当前机构的id   数据库查询的时候遍历的时候 type是1 fav_id 就能查询到
    def get(self, request):
        course_list = []
        fav_courses = UserFavourite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list
        })




class MymessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    def get(self, request):#取id
        all_message = UserMessage.objects.filter(user=request.user.id)
        # 对个人消息进行分页
        #用户进入个人消息之后清空未读消息的记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 5是每页的数量必须写 不写报错原来的文档没写
        p = Paginator(all_message, 5, request=request)

        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            "messages":messages
        })





class IndexView(View):
    def get(self, request):
        #取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        courses_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html',{
            'all_banners':all_banners,
            'courses':courses,
            'banner_courses':banner_courses,
            'courses_orgs':courses_orgs

        })


def page_not_found(request):
    #全局404处理逻辑
    from django.shortcuts import render_to_response
    response = render_to_response('404.html',{})
    response.status_code = 404
    return response



def page_error(request):
    # 全局500处理逻辑
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response




            # Create your views here.
# def user_login(request):
#     if request.method == "POST":
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#         #必须设定默认值而且是固定写法
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, "index.html")
#         else:
#             return render(request, "login.html", {"msg":"用户名或者密码错误!"})
#     elif request.method == "GET":
#         return render(request, "login.html", {})