# _*_ encoding:utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import render_to_response
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
#引入这个模块可以选择给用户返回的是什么样的数据
from django.http import  HttpResponse
# Create your views here

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFavourite
class OrgView(View):
    """
    课程机构列表功能
    """
    def get(self, request):
        #取出所有课程机构
        all_orgs = CourseOrg.objects.all()

        #取出热门机构
        hot_orgs = all_orgs.order_by("-click_nums")[:3]
        #取出所有城市
        all_citys = CityDict.objects.all()

        #机构搜索
        search_keywords = request.GET.get("keywords", "")
        if search_keywords:  # 此处双下划线 前面带i基本不区分大小写  __incontains 名称中包含 "search_keywords"，且不区分大小写用Q代表or或者多个字段都包含然后筛选
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        #取出筛选城市 外键也可以外键名下划线+id 进行筛选
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #类别筛选
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        #学习人数，课程数排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")



        #取出多少家机构
        org_nums = all_orgs.count()
        #对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        #5是每页的数量必须写 不写报错原来的文档没写
        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)

        return render(request, "org-list.html",{
            "all_orgs":orgs,
            "all_citys":all_citys,
            "org_nums":org_nums,
            "city_id":city_id,
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort
        })


class AddUserAskView(View):
    """
    用户咨询
    """
    def post(self, request):#实例化传递request.POST这个不能忘
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            #因为是model所以可以直接save commit为true 才是往数据库保存 不加只是提交而已
            user_ask = userask_form.save(commit=True)
            return HttpResponse("{'status': 'success'}", content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg":"添加出错"}', content_type='application/json')

class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        #current_page传递给后台用于标签激活状态判断在每个VIEW传递过去后台接收的就是对应的current_page
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        #用户是否收藏在html前端 一刷新收藏消失的问题
        has_fav = False
        #用户在登录状态下才能判断
        if request.user.is_authenticated():
            if UserFavourite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        #外键的反向引用 类名小写加个set 有外键的地方都可以这么做
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return  render(request, 'org-detail-homepage.html',{
            'all_courses':all_courses,
            'all_teachers': all_teachers,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        #用户在登录状态下才能判断
        if request.user.is_authenticated():
            if UserFavourite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        #外键的反向引用 类名小写加个set 有外键的地方都可以这么做
        all_courses = course_org.course_set.all()
        return  render(request, 'org-detail-course.html',{
            'all_courses':all_courses,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
        })

class OrgDescView(View):
    """
    机构介绍页
    """
    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        #用户在登录状态下才能判断
        if request.user.is_authenticated():
            if UserFavourite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return  render(request, 'org-detail-desc.html',{
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
        })


class OrgTeacherView(View):
    """
    机构教师页
    """
    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        #用户在登录状态下才能判断
        if request.user.is_authenticated():
            if UserFavourite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        #外键的反向引用 类名小写加个set 有外键的地方都可以这么做
        all_teachers = course_org.teacher_set.all()
        return  render(request, 'org-detail-teachers.html',{
            'all_teachers':all_teachers,
            "course_org":course_org,
            "current_page":current_page,
            'has_fav':has_fav
        })


class AddFavView(View):
    """
    用户收藏  用户取消收藏
    """
    #int对空串转换会抛出异常 用0代替
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)
        #必须判断用户是否是登录状态

        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail", "msg":"用户未登录"}', content_type='application/json')

        exist_records = UserFavourite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            #如果记录已经存在，则表示用户取消收藏 对应类型的收藏数-1操作
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                #避免负数出现
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type)== 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status": "success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavourite()
            #等于0代表没有取到 所以在做一层判断
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                #收藏数+1 类别收藏

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status": "success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status": "fail", "msg":"收藏出错"}', content_type='application/json')



class TeacherListView(View):
    """
    课程讲师列表页
    """
    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 课程讲师搜索
        search_keywords = request.GET.get("keywords", "")
        if search_keywords:  # 此处双下划线 前面带i基本不区分大小写  __incontains 名称中包含 "search_keywords"，且不区分大小写用Q代表or或者多个字段都包含然后筛选
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) |
                                               Q(work_company__icontains=search_keywords)|
                                               Q(work_position__icontains=search_keywords))

        sort = request.GET.get("sort", "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]




        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 1, request=request)

        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers":teachers,
            "sorted_teacher":sorted_teacher,
            "sort":sort,
        })



class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_number += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)#讲师所有课程
        #授课老师是否被收藏过
        has_teacher_faved = False
        if UserFavourite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True
        #授课机构是否收藏过
        has_org_faved = False
        if UserFavourite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        #讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, "teacher-detail.html", {
            "teacher":teacher,
            "all_courses":all_courses,
            "sorted_teacher":sorted_teacher,
            "has_teacher_faved":has_teacher_faved,
            "has_org_faved":has_org_faved
        })