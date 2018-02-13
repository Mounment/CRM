#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__= 'luhj'
from django.forms import forms,ModelForm
from django.forms import ValidationError

def create_model_form(request,admin_class):
    '''动态生成表单'''
    error_list = []

    def __new__(cls,*args,**kwargs):
        #动态生成样式
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if not admin_class.is_add_form: #如果是新建的数据,去除disabled样式
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'
            else:
                pass
            if hasattr(admin_class,'clean_%s'%field_name):
                field_clean_func=getattr(admin_class,'clean_%s'%field_name)
                setattr(cls,'field_clean_func',field_clean_func)

        return ModelForm.__new__(cls)

    def default_clean(self):
        #所有的表单都适用,readonly字段的后端验证
        if self.instance.id:#如果instance对象不为空,说明是修改,否则是新建
            for field in admin_class.readonly_fields:
                field_obj_db = getattr(self.instance,field) #数据库的值

                if hasattr(field_obj_db,'select_related'):
                    m2m_objs = getattr(field_obj_db,'select_related')().select_related()
                    m2m_values = [i[0] for i in m2m_objs.values_list('id')]
                    if set(m2m_values) != set([i.id for i in self.cleaned_data.get(field)]):
                        self.add_error('%s是只读字段,不能修改'%field)
                    continue

                field_obj_front = self.cleaned_data.get(field) #前端readonly的值
                if field_obj_db!=field_obj_front:
                    error_list.append(ValidationError('%s字段是只读字段,不允许更改'%field))

        #调用用户自定义验证
        self.ValidationError = ValidationError
        response= admin_class.default_form_validation(self)

        if response:
            error_list.append(response)

        if error_list:
            raise ValidationError(error_list)

    class Meta:
        model = admin_class.model
        fields = '__all__'
        exclude = admin_class.modelfrom_exclude_fields     #排除的字段

    attrs = {'Meta':Meta}

    _model_form_class = type('DynamicModelForm',(ModelForm,),attrs)
    #添加new方法在生成实例的时候添加样式
    setattr(_model_form_class,'__new__',__new__)
    setattr(_model_form_class,'clean',default_clean)
    return _model_form_class