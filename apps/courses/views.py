# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .models import Course, CourseResource, Video
from operation.models import UserFavourite,CourseComments,UserCourse
from utils.mixin_utils import LoginRequiredMixin
# Create your views here.


#课程列表页
class CourseListView(View):
    def get(self, request):#默认按添加时间最新排序
        all_courses = Course.objects.all().order_by("-add_time")

        #热门课程推荐排序
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]
        #前端页面全局搜索之课程搜索逻辑
        search_keywords = request.GET.get("keywords", "")
        if search_keywords:#此处双下划线 前面带i基本不区分大小写  __incontains 名称中包含 "search_keywords"，且不区分大小写用Q代表or或者多个字段都包含然后筛选
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))

        #最热门参与人数的课程排序 要放在分页数据之前
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")
        #对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 3 , request=request)
        courses = p.page(page)
        return render(request, 'course-list.html', {
            "all_courses":courses,#因为是传递分页数据 模板for循环的对象是是all_courses.object_list
            "sort":sort,
            "hot_courses":hot_courses
        })

class VideoPlayView(View):
    """
    视频播放页面
    """

    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该用户学过的其他的所有过程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-play.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
            "video": video
        })


#课程详情
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        #增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavourite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavourite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True


        #相关课程推荐没有直接返回空数组 不然会报错 在后台定义课程的tag形成关联关系
        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:1]
        else:
            relate_coures = []
        return render(request, "course-detail.html", {
            "course":course,
            "relate_coures":relate_coures,
            "has_fav_course":has_fav_course,
            "has_fav_org":has_fav_org
        })

#登录权限的验证
class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        #课程点击数+1
        course.students += 1
        course.save()
        #查询用户是否已经关联了该课程 如果没有就建立这种关联关系
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()


        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        #用户学的所有课程 外键加下划线id直接传递ID in是django查询级条件存在于一个list范围内
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出所有课程ID
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        #获取该用户学过的其他所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources":all_resources,
            "relate_courses":relate_courses
        })


#验证用户是否是登录状态的装饰器
class CommentsView(LoginRequiredMixin, View):
    """
    课程评论
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, "course-comment.html", {
            "course": course,
            "course_resources":all_resources,
            "all_comments":all_comments
        })


class AddComentsView(View):
    """
    用户添加课程评论
    """
    def post(self, request):
        #判断用户登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登陆"}', content_type='application/json')

        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        #ID必须大于0代表有数据 commens 为True 存在才会执行下面操作
        #实例化CourseComments对象，然后取出课程和评论的内容赋予实例化之后的课程和评论的属性 然后保存
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')
