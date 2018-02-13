#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__= 'luhj'
from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta
from django.db.models.query import QuerySet
from django.core.exceptions import FieldDoesNotExist
register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    '''渲染表名'''
    return admin_class.model._meta.verbose_name_plural


@register.simple_tag
def bulid_table_row(request,obj,admin_class):
    '''生成数据内容的td,填充到table中,展示前端'''
    row_ele = ''
    for index,column in enumerate(admin_class.list_display):
        #获取每个字段的类型的对象
        field_obj = obj._meta.get_field(column)
        try:
            #判断是否是choice字段
            if field_obj.choices:
                #如果是choice字段,则按照choice的值进行展示
                column_data = getattr(obj,"get_%s_display"%column)()
            else:
                #否则通过反射去对象中取值
                column_data = getattr(obj,column)

            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime('%Y-%m-%d %H:%M:%S')

            if index == 0:#添加a标签,跳转到修改页面
                column_data = '<a href={request_path}{obj_id}/change>{data}</a>'.format(request_path=request.path,
                                                                                        obj_id=obj.id,data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                admin_class.instance = obj
                admin_class.request = request
                column_func = getattr(admin_class,column)
                column_data = column_func()
        row_ele += '<td>%s</td>'%column_data
    return mark_safe(row_ele)


@register.simple_tag
def render_filter_ele(condition,admin_class,filter_conditions):
    select_ele = '<select class="form-control" name="{condition}"><option value="">----</option>'
    field_obj = admin_class.model._meta.get_field(condition)
    selected = ''
    if field_obj.choices:

        #choice字段的值的获取
        for choice_item in field_obj.choices:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = 'selected'
            select_ele += '<option value="%s" %s>%s</option>'%(choice_item[0],selected,choice_item[1])
            selected = ''
    if type(field_obj).__name__=='ForeignKey':
        #外键字段的获取
        for choice_item in field_obj.get_choices()[1:]:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = 'selected'
            select_ele += '<option value="%s" %s>%s</option>' % (choice_item[0], selected,choice_item[1])
            selected = ''
    if type(field_obj).__name__ in ['DateTimeField','DateField']:
        #日期字段获取,通过计算当前时间-天数来实现日期过滤
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天',today_ele])
        date_els.append(['昨天',today_ele - timedelta(days=1)])
        date_els.append(['近7天', today_ele - timedelta(days=7)])
        date_els.append(['本月', today_ele.replace(day=1)])
        date_els.append(['近30天', today_ele - timedelta(days=30)])
        date_els.append(['近90天', today_ele - timedelta(days=90)])
        date_els.append(['近180天', today_ele - timedelta(days=180)])
        date_els.append(['本年', today_ele.replace(month=1,day=1)])
        date_els.append(['近一年', today_ele - timedelta(days=365)])
        selected = ''
        for date in date_els:
            select_ele += '<option value="%s" %s>%s</option>'%(date[1],selected,date[0])
        filter_field_name = '%s__gte'%condition
    else:
        filter_field_name = condition

    select_ele+='</select>'
    select_ele=select_ele.format(condition=filter_field_name)
    return mark_safe(select_ele)

@register.simple_tag
def build_paginations(query_sets,filter_conditions,previous_orderby,search_text):
    '''返回整个的分页元素'''
    filters = ''
    for k, v in filter_conditions.items():
        filters += '&%s=%s' % (k, v)

    page_btns = ''
    added_dot_ele = False
    for page_num in query_sets.paginator.page_range:
        #代表最前2页,或最后2页
        if page_num < 3 or page_num > query_sets.paginator.num_pages-2 or \
                        abs(query_sets.number - page_num) <= 1:
            ele_class = ''
            if query_sets.number == page_num:
                ele_class = 'active'
                added_dot_ele = False
            page_btns += '<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>' % (ele_class, page_num, filters,previous_orderby,search_text,page_num)
        else:
            if not added_dot_ele:#现在还没有加...
                page_btns += '<li><a>...</a></li>'
                added_dot_ele = True

    return mark_safe(page_btns)


@register.simple_tag
def build_table_header_column(column,orderby_key,filter_condition,admin_class):
    filters = ''
    for k,v in filter_condition.items():
        filters += '&%s=%s'%(k,v)
    #生成每一列表头的超链接,点击触发排序
    ele = '<th><a href="?{filters}&o={orderby_key}">{column}</a>{sort_icon}</th>'
    if orderby_key:
        if orderby_key.startswith('-'):
            #加入样式
            sort_icon = '<span class="glyphicon glyphicon-chevron-up"></span>'
        else:
            sort_icon = '<span class="glyphicon glyphicon-chevron-down"></span>'

        if orderby_key.strip('-') == column: #排序的就是当前字段
            orderby_key = orderby_key

        else:
            orderby_key = column
            sort_icon = ''

    else:#没有排序,
        orderby_key = column
        sort_icon = ''
    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist as e:
        #去除非数据库字段的排序错误
        column_verbose_name = getattr(admin_class,column).display_name
        ele = '<th><a href="javascript:void(0)">{column}</a></th>'.format(column=column_verbose_name)
        return mark_safe(ele)
    return mark_safe(ele.format(orderby_key=orderby_key,column=column_verbose_name,sort_icon=sort_icon,filters=filters))


@register.simple_tag
def get_m2m_tags(admin_class,field,form_obj):
    #返回多对多所有待选数据

    #表结构对象的多对多字段
    all_field_obj = getattr(admin_class.model,field.name)
    #全部多对多字段
    all_field_list = all_field_obj.rel.to.objects.all()

    if form_obj.instance.id:#判断记录是否有多对多对象,如果没有则是新建,有就是修改
        # 已选数据的多对多对象
        choose_field_obj = getattr(form_obj.instance, field.name)
        #已选数据的多对多字段
        selected_obj_list = choose_field_obj.all()
    else: #表示创建新的记录
        return all_field_list

    standby_obj_list = []
    for obj in all_field_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)


    return standby_obj_list

@register.simple_tag
def get_m2m_selected_tags (form_obj,field):
    #返回已选中的复选框数据
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance,field.name)
        return field_obj.all()


@register.simple_tag
def display_obj_related(model_obj):
    #将行数据所关联的数据全部取出来
    objs = None
    if isinstance(model_obj,QuerySet):
        objs=model_obj
    else:
        objs=[model_obj,]
    return mark_safe(recursive_related_objs_look(objs))



def recursive_related_objs_look(objs):
    '''拼接多对多和一对多的标签'''
    ul_ele = '<ul>'
    for obj in objs:
        #前端的样式排除'<>'
        li_ele = '<li>%s:%s</li>'%(obj._meta.verbose_name,obj.__str__().strip('<>'))
        ul_ele += li_ele

        #把所有和这个对象直接关联的多对多对象的值
        for m2m_field in obj._meta.local_many_to_many:

            sub_ul_ele = create_sub_ul(obj,m2m_field,m2m_field.name,True)
            ul_ele += sub_ul_ele

        for related_obj in obj._meta.related_objects:
            #获取外键多对多的信息
            if 'ManyToManyRel' in related_obj.__repr__():
                if hasattr(obj,related_obj.get_accessor_name()):
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    sub_ul_ele = create_sub_ul(obj,related_obj.get_accessor_name(),False)
                    ul_ele+=sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()):
                #如果有一对多属性,则获取一对多属性的对象
                accessor_obj = getattr(obj,related_obj.get_accessor_name())

                if hasattr(accessor_obj,'select_related'):
                    #找出所有一对多属性的值
                    target_objs = accessor_obj.select_related()

                if len(target_objs) > 0:
                    nodes = recursive_related_objs_look(target_objs)
                    ul_ele += nodes
    ul_ele += '</ul>'
    return ul_ele


def create_sub_ul(obj,field_name,field,m2m_flag):
    #创建子标签
    sub_ul_ele = '<ul>'
    field_obj = getattr(obj,field)
    if m2m_flag:
        for obj_list in field_obj.select_related():
            sub_li_ele = '<li>%s:%s</li>'%(field_name.verbose_name,obj_list.__str__().strip('<>'))
            sub_ul_ele += sub_li_ele
    else:
        for obj_list in field_obj.select_related():
            sub_li_ele = '<li>%s:%s</li>'%(obj_list._meta.verbose_name,obj_list.__str__().strip('<>'))
            sub_ul_ele += sub_li_ele
    sub_ul_ele += '</ul>'
    return sub_ul_ele


@register.simple_tag
def build_action_name(admin_class,action):
    #获取自定义action对象
    action_func = getattr(admin_class,action)
    return action_func.display_name if hasattr(action_func,'display_name') else action



