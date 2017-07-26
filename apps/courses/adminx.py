# -*- coding: utf-8 -*-
__author__ = 'admin'
__date__ = '17/1/28 下午4:04'

from .models import Course, Lesson, Video, CourseResource,BannerCourse

import xadmin

#model只能一层嵌套
class LessonInline(object):
    model = Lesson
    extra = 0

class CourseResourceInline(object):
    model = CourseResource
    extra = 0

class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','get_zj_nums','add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']#后台显示为只读字段 无法修改
    list_editable = ['degree', 'desc']#在列表页有哪些字段可以直接修改
    exclude = ['fav_nums']#后台不包含的字段
    inlines = [LessonInline, CourseResourceInline]
    # refresh_times = [3,5] #定时刷新

    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']#后台显示为只读字段 无法修改
    exclude = ['fav_nums']#后台不包含的字段
    inlines = [LessonInline, CourseResourceInline]

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs




#有外键的过滤两个下划线变量名

class LessonAdmin(object):
    list_display = ['course','name','add_time']
    search_fields = ['course','name']
    list_filter = ['course__name','name','add_time']


class VideoAdmin(object):
    list_display = ['lesson','name','add_time']
    search_fields = ['lesson','name','add_time']
    list_filter = ['lesson','name','add_time']


class CourseResourceAdmin(object):
    list_display = ['course','name','download', 'add_time']
    search_fields = ['course','name','download']
    list_filter = ['course','name','download', 'add_time']

xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)