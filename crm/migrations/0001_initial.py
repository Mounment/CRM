# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-28 03:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('name', models.CharField(max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': '用户',
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('addr', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name_plural': '校区',
            },
        ),
        migrations.CreateModel(
            name='ClassList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.PositiveSmallIntegerField(verbose_name='学期')),
                ('class_type', models.SmallIntegerField(choices=[(0, '面授班(脱产)'), (1, '面授班(周末)'), (2, '网络班')])),
                ('start_date', models.DateField(verbose_name='开班日期')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='结业日期')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Branch', verbose_name='分校')),
            ],
            options={
                'verbose_name_plural': '班级',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('price', models.PositiveSmallIntegerField()),
                ('period', models.PositiveSmallIntegerField(verbose_name='周期(月)')),
                ('outline', models.TextField()),
            ],
            options={
                'verbose_name_plural': '课程',
            },
        ),
        migrations.CreateModel(
            name='CourseRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_num', models.PositiveSmallIntegerField(verbose_name='第几节(天)')),
                ('has_homework', models.BooleanField(default=True)),
                ('homework_title', models.CharField(blank=True, max_length=256, null=True)),
                ('homework_content', models.TextField(blank=True, null=True)),
                ('outline', models.TextField(verbose_name='本节课大纲')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('from_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ClassList', verbose_name='班级')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '上课记录',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('qq', models.CharField(max_length=64, unique=True)),
                ('qq_name', models.CharField(blank=True, max_length=64, null=True)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('source', models.SmallIntegerField(choices=[(0, '转介绍'), (1, 'QQ群'), (2, '官网'), (3, '百度推广'), (4, '51cto'), (5, '知乎推荐'), (6, '市场推广')])),
                ('referral_from', models.CharField(blank=True, max_length=64, null=True, verbose_name='转介绍人QQ')),
                ('content', models.TextField(verbose_name='咨询详情')),
                ('memo', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('signed', '已报名'), ('unregistered', '未报名')], default='unregistered', max_length=64, verbose_name='客户状态')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consult_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course', verbose_name='咨询课程')),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='销售')),
            ],
            options={
                'verbose_name_plural': '客户',
            },
        ),
        migrations.CreateModel(
            name='CustomerFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='跟进内容')),
                ('intention', models.SmallIntegerField(choices=[(0, '2周内报名'), (1, '1个月报名'), (2, '近期无报名计划'), (3, '已在其他机构报名'), (4, '已报名'), (5, '已拉黑')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
            options={
                'verbose_name_plural': '客户跟进记录',
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_agreed', models.BooleanField(default=False, verbose_name='学生已同意合同条款')),
                ('contact_approved', models.BooleanField(default=False, verbose_name='合同已审核')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='课程顾问')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
                ('enrolled_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ClassList', verbose_name='所报班级')),
            ],
            options={
                'verbose_name_plural': '报名',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('url_name', models.CharField(max_length=64, unique=True)),
                ('url_type', models.PositiveIntegerField(choices=[(0, 'alias'), (1, 'absolute_url')], default=0)),
            ],
            options={
                'verbose_name_plural': '菜单',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=500, verbose_name='数额')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
            options={
                'verbose_name_plural': '缴费记录',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('menus', models.ManyToManyField(blank=True, to='crm.Menu')),
            ],
            options={
                'verbose_name_plural': '角色',
            },
        ),
        migrations.CreateModel(
            name='StudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.SmallIntegerField(choices=[(0, '已签到'), (1, '迟到'), (2, '缺勤'), (3, '早退')], default=0)),
                ('score', models.SmallIntegerField(choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (75, 'B-'), (70, 'C+'), (60, 'C'), (40, 'C-'), (-50, 'D'), (-100, 'COPY'), (0, 'N/A')])),
                ('memo', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('course_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.CourseRecord')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Enrollment')),
            ],
            options={
                'verbose_name_plural': '学习记录',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'verbose_name_plural': '标签',
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='crm.Tag'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='teachers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='studyrecord',
            unique_together=set([('student', 'course_record')]),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set([('customer', 'enrolled_class')]),
        ),
        migrations.AlterUniqueTogether(
            name='courserecord',
            unique_together=set([('from_class', 'day_num')]),
        ),
        migrations.AlterUniqueTogether(
            name='classlist',
            unique_together=set([('branch', 'course', 'semester')]),
        ),
    ]
