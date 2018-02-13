#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__= 'luhj'
from django.db.models import Q
def table_filter(request,admin_class):
    '''进行条件过滤,并返回过滤后的数据'''
    filter_condition = {}
    # page为分页的字段,o为排序关键字,_q是搜索关键字,不是数据库的查询字段,此处要进行过滤
    keywords = ['page','o','_q']
    for k,v in request.GET.items():

        if k in keywords:
            continue
        if v:
            filter_condition[k]=v

    return admin_class.model.objects.filter(**filter_condition).order_by(\
       '-%s'%admin_class.ordering if admin_class.ordering else '-id'),filter_condition



def table_sort(request,objs):
    #获取前端的分页关键字进行排序
    orderby_key = request.GET.get('o')
    if orderby_key:
        res = objs.order_by(orderby_key)
        if orderby_key.startswith('-'):
            orderby_key = orderby_key.strip('-')
        else:
            orderby_key = '-%s'%orderby_key
    else:
        res = objs
    return res,orderby_key


def table_search(request,admin_class,object_list):
    search_key = request.GET.get('_q','')
    con = Q()
    con.connector = 'OR'
    for search_field in admin_class.search_fields:
        con.children.append(('%s__contains'%search_field,search_key))
    res = object_list.filter(con)
    return res