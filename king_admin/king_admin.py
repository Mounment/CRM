#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__= 'luhj'
from crm import models
from django.shortcuts import render,redirect
enabled_admins = {}

class BaseAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 20
    filter_horizontal = [] #复选框显示字段
    ordering = None
    actions = ['delete_selected_objs',]
    readonly_fields = []
    readonly_table = False
    modelfrom_exclude_fields = []


    def delete_selected_objs(self,request,query_set):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        selected_ids = ','.join([str(i.id) for i in query_set])
        if self.readonly_table:
            errors = {'只读表':'该表是只读表,记录不允许更改'}
        else:
            errors = {}
        if request.POST.get('delete_confirm') == 'yes':
            if not self.readonly_table:
                query_set.delete()
                return redirect('/king_admin/%s/%s/' % (app_name,model_name))

        return render(request,'king_admin/table_delete.html',{'model_obj':query_set,
                                                              'admin_class':self,
                                                              'app_name':app_name,
                                                              'table_name':model_name,
                                                              'selected_ids':selected_ids,
                                                              'action':request._action,
                                                              'errors':errors})
    def default_form_validation(self):
        #用户在此处可以自定义表单的整体字段验证
        pass

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer', 'consultant','date']

class CustomerAdmin(BaseAdmin):
    list_display = ['qq','name','source','consultant','consult_course','date','status','enroll']
    list_filters = ['source','consultant','consult_course','status','date']
    search_fields = ['qq','name','consultant__name']
    list_per_page = 5
    ordering = 'id'
    filter_horizontal = ['tags',]
    actions = ['delete_selected_objs','test',]
    readonly_fields = ['qq','consultant','tags',]
    readonly_table = False

    def test(self,request,query_set):
        print('test...')

    test.display_name = '测试'

    def default_form_validation(self):
        '''整体表单字段的验证'''
        content = self.cleaned_data.get('content')
        if len(content)<=15:
            return self.ValidationError('content字段的值不能少于15个字符')

    def clean_name(self):
        if not self.cleaned_data['name']:
            self.add_error('姓名不能为空')

    def enroll(self):
        return '''<a href="%s/enrollment/">报名</a>'''%self.instance.id

    enroll.display_name = '报名'
    #model = model.Customer

class UserAdmin(BaseAdmin):
    list_display = ['email','name']
    readonly_fields = ['password',]
    modelfrom_exclude_fields = ['last_login','is_superuser','groups','user_permissions']




def register(model_class,admin_class=None):
    #获取app的名字
    if model_class._meta.app_label not in enabled_admins:
        #第一次进来如果没有app key对应的字典则初始化一个app名称作为字典
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class#绑定model对象和admin类
    #绑定app,model_name和admin_class绑定在一起
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class

register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.UserProfile,UserAdmin)