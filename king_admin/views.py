from django.shortcuts import render,redirect
from king_admin import king_admin
from king_admin.utils import table_filter,table_sort,table_search
from king_admin.forms import create_model_form
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):

    return render(request, 'king_admin/table_index.html',{'table_list':king_admin.enabled_admins})

@login_required
def display_table_objs(request,app_name,table_name):
    admin_class = king_admin.enabled_admins[app_name][table_name]

    #post请求执行action操作
    if request.method == 'POST':
        selected_ids = request.POST.get('selected_ids')
        action_name = request.POST.get('action')
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError('没有数据')
        if hasattr(admin_class,action_name):
            action_func = getattr(admin_class,action_name)
            request._action = action_name
            return action_func(admin_class,request,selected_objs)


    #有后端查询出结果集,并对其进行分页操作
    object_list,filter_conditions = table_filter(request,admin_class)
    #搜索
    object_list = table_search(request,admin_class,object_list)
    #先过滤,在排序
    object_list,orderby_key = table_sort(request,object_list)

    paginator = Paginator(object_list, admin_class.list_per_page)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return render(request,'king_admin/table_objs.html',{'admin_class':admin_class,
                                                       'query_sets':objects,
                                                        'filter_conditions':filter_conditions,
                                                        'orderby_key':orderby_key,
                                                        'previous_orderby':request.GET.get('o') or '',
                                                        'search_text':request.GET.get('_q') or ''})

@login_required
def table_obj_change(request,app_name,table_name,table_id):
    #表修改
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_obj = create_model_form(request,admin_class)
    admin_class.is_add_form = False
    table_obj = admin_class.model.objects.get(id=table_id)
    if request.method == 'POST':
        #修改
        form_obj = model_obj(request.POST,instance=table_obj)

        if not admin_class.readonly_table:
            if form_obj.is_valid():
                form_obj.save()
    else:
        form_obj = model_obj(instance=table_obj)

    return render(request,'king_admin/table_change.html',{'form_obj':form_obj,
                                                          'admin_class': admin_class,
                                                          'app_name':app_name,
                                                          'table_name':table_name})
@login_required
def table_obj_add(request,app_name,table_name):
    #表新增
    admin_class = king_admin.enabled_admins[app_name][table_name]
    admin_class.is_add_form = True #表示是新增数据
    model_obj = create_model_form(request,admin_class)
    if request.method == 'POST':
        form_obj = model_obj(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace('/add/','/'))
    else:
        form_obj = model_obj
    return render(request,'king_admin/table_add.html',{'form_obj':form_obj,
                                                       'admin_class':admin_class})

@login_required
def table_obj_delete(request,app_name,table_name,obj_id):
    #表字段删除
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_obj = admin_class.model.objects.get(id=obj_id)
    if admin_class.readonly_table:
        errors = {'只读表':'该表是只读表,记录不允许更改'}
    else:
        errors = {}
    if request.method == 'POST':
        if not admin_class.readonly_table:
            model_obj.delete()
            return redirect('/king_admin/%s/%s/'%(app_name,table_name))
    return render(request,'king_admin/table_delete.html',{'model_obj':model_obj,
                                                          'app_name':app_name,
                                                          'table_name':table_name,
                                                          'errors':errors})

@login_required
def password_reset(request,app_name,table_name,obj_id):
    '''动态修改密码'''
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_obj = admin_class.model.objects.get(id=obj_id)
    errors = {}
    if request.method == 'POST':
        _password1 = request.POST.get('password1')
        _password2 = request.POST.get('password2')
        if _password1 == _password2:
            if len(_password2) > 5:
                model_obj.set_password(_password1)
                model_obj.save()
                return redirect(request.path.rstrip('password/'))
            else:
                errors['invalid_password'] = '密码长度不足6位'
        else:
            errors['invalid_password'] = '两次密码不一致'
    return render(request,'king_admin/password_reset.html',{'model_obj':model_obj})


