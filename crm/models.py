from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
# Create your models here.
class Customer(models.Model):
    '''客户信息表'''
    name = models.CharField(max_length=32,null=True,blank=True,)
    qq = models.CharField(max_length=64,unique=True)
    qq_name = models.CharField(max_length=64,null=True,blank=True)
    phone = models.CharField(max_length=64,null=True,blank=True)
    source_choices = ((0,'转介绍'),(1,'QQ群'),(2,'官网'),(3,'百度推广'),(4,'51cto'),(5,'知乎推荐'),(6,'市场推广'))
    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.CharField(verbose_name='转介绍人QQ',max_length=64,null=True,blank=True)
    consult_course = models.ForeignKey('Course',verbose_name='咨询课程')
    content = models.TextField(verbose_name='咨询详情')
    consultant = models.ForeignKey('UserProfile',verbose_name='销售')
    tags = models.ManyToManyField('Tag',blank=True,null=True);
    memo = models.TextField(blank=True,null=True)
    status_choice = (('signed','已报名'),('unregistered','未报名'))
    status = models.CharField(max_length=64,choices=status_choice,default='unregistered',verbose_name='客户状态')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '客户'

    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    '''客户跟进表'''
    customer = models.ForeignKey('Customer')
    content = models.TextField(verbose_name='跟进内容')
    consultant = models.ForeignKey('UserProfile')
    intention_choices = ((0,'2周内报名'),(1,'1个月报名'),(2,'近期无报名计划'),(3,'已在其他机构报名'),(4,'已报名'),(5,'已拉黑'))
    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.customer.qq, self.intention)

    class Meta:
        verbose_name_plural = '客户跟进记录'

class Course(models.Model):
    '''课程表'''
    name = models.CharField(max_length=128,unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name='周期(月)')
    outline = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '课程'

class Branch(models.Model):
    '''校区表'''
    name = models.CharField(max_length=128,unique=True)
    addr = models.CharField(max_length=512)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '校区'

class ClassList(models.Model):
    '''班级表'''
    branch = models.ForeignKey('Branch',verbose_name='分校')
    course = models.ForeignKey('Course')
    semester = models.PositiveSmallIntegerField(verbose_name='学期')
    teachers =  models.ManyToManyField('UserProfile')
    class_type_choice = ((0,'面授班(脱产)'),(1,'面授班(周末)'),(2,'网络班'))
    class_type = models.SmallIntegerField(choices=class_type_choice)
    start_date = models.DateField(verbose_name='开班日期')
    end_date = models.DateField(verbose_name='结业日期',blank=True,null=True)

    def __str__(self):
        return '%s %s %s' % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course', 'semester')
        verbose_name_plural = '班级'



class CourseRecord(models.Model):
    '''上课记录表'''
    from_class = models.ForeignKey('ClassList',verbose_name='班级')
    day_num = models.PositiveSmallIntegerField(verbose_name='第几节(天)')
    teacher = models.ForeignKey('UserProfile')
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=256,blank=True,null=True)
    homework_content = models.TextField(blank=True,null=True)
    outline = models.TextField(verbose_name='本节课大纲')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name_plural = '上课记录'


class StudyRecord(models.Model):
    '''学习记录表'''
    student = models.ForeignKey('Enrollment')
    course_record = models.ForeignKey('CourseRecord')
    attendance_choice = ((0,'已签到'),(1,'迟到'),(2,'缺勤'),(3,'早退'))
    attendance = models.SmallIntegerField(choices=attendance_choice,default=0)
    score_choices = ((100,'A+'),(90,'A'),(85,'B+'),(80,'B'),(75,'B-'),(70,'C+'),(60,'C'),(40,'C-'),(-50,'D'),(-100,'COPY'),(0,'N/A'))
    score = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s %s' % (self.student, self.course_record, self.score)

    class Meta:
        unique_together = ('student', 'course_record')
        verbose_name_plural = '学习记录'




class Enrollment(models.Model):
    '''学生报名表(学生报名信息,合同,入学日期,所报班级)'''
    customer = models.ForeignKey('Customer')
    enrolled_class = models.ForeignKey('ClassList',verbose_name='所报班级')
    consultant = models.ForeignKey('UserProfile',verbose_name='课程顾问')
    contact_agreed = models.BooleanField(default=False,verbose_name='学生已同意合同条款')
    contact_approved = models.BooleanField(default=False,verbose_name='合同已审核')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ('customer', 'enrolled_class')
        verbose_name_plural = '报名'

class Payment(models.Model):
    '''缴费记录'''
    customer = models.ForeignKey('Customer')
    course = models.ForeignKey('Course')
    amount = models.PositiveIntegerField(verbose_name='数额',default=500)
    consultant = models.ForeignKey('UserProfile')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.customer, self.amount)

    class Meta:
        verbose_name_plural = '缴费记录'
#
# class UserProfile(models.Model):
#     '''账号表'''
#     user = models.OneToOneField(User)
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField('Role',blank=True,null=True)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = '用户'
class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):

        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(_('password'), max_length=128,help_text = mark_safe('<a href="password/">修改密码</a>'))
    roles = models.ManyToManyField('Role',blank=True)
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: active users are staff
        return self.is_active

    class Meta:
        verbose_name_plural = '用户'



class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=64,unique=True)
    menus = models.ManyToManyField('Menu',blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色'

class Tag(models.Model):
    '''标签备注'''
    name = models.CharField(max_length=64,unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = '标签'


class Menu(models.Model):
    '''菜单表'''
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64,unique=True)
    url_type_choices = ((0,'alias'),(1,'absolute_url'))
    url_type = models.PositiveIntegerField(choices=url_type_choices,default=0)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = '菜单'

