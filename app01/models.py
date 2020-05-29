from django.db import models
from django.utils.safestring import mark_safe
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class User(models.Model):
    """
    用户表
    """
    username = models.CharField(max_length=32, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')
    position = models.CharField(max_length=32, verbose_name='职位')
    company = models.CharField(max_length=32, verbose_name='公司',
                               choices=(('0', '总公司'), ('1', '石家庄分公司'), ('2', '广州分公司')))
    phone = models.CharField(max_length=11, verbose_name='手机号')
    last_time = models.DateTimeField(null=True, blank=True, verbose_name='上次登陆时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='img/avatar', default='img/avatar/default.jpg')

    def __str__(self):
        return self.username


class Category(models.Model):
    title = models.CharField(max_length=32, verbose_name='板块标题')

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    文章标题，内容，作者，创建时间，修改时间，板块
    """
    title = models.CharField(max_length=64, verbose_name='文章标题')
    abstract = models.CharField(max_length=256, verbose_name='文章摘要')
    author = models.ForeignKey('User', on_delete=models.DO_NOTHING, null=True, verbose_name='作者')
    category = models.ForeignKey('Category', on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='板块分类')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    publish_status = models.BooleanField(default=False, choices=((False, '未发布'), (True, '发布')), verbose_name='发布状态')
    detail = models.OneToOneField('ArticleDetail', on_delete=models.DO_NOTHING)


    def show_publish_status(self):
        show_dic = {
            True: 'green',
            False: '#c34a0c',
        }
        return mark_safe(
            '<span style="background:{};color:white;padding:3px">{}</span>'.format(show_dic[self.publish_status],
                                                                                   self.get_publish_status_display()))


class ArticleDetail(models.Model):
    content = RichTextUploadingField(verbose_name='文章内容')


class Comment(models.Model):
    """
    评论表
        评论者 评论内容 评论文章 时间 审核状态
    """
    author = models.ForeignKey('User', on_delete=models.DO_NOTHING, verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    article = models.ForeignKey('Article', verbose_name='文章', on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True, verbose_name='审核时间')
    status = models.BooleanField(verbose_name='审核状态', default=True)


class Series(models.Model):
    """
    系列
    """
    title =  models.CharField(verbose_name='系列名称', max_length=32)
    article = models.ManyToManyField('Article', verbose_name='文章')
    user = models.ManyToManyField('User', verbose_name='用户', through='UserSeries')
    # through 通过另外一张自定义的关系表创建多对多的关系


class UserSeries(models.Model):
    """
    用户和系列关系表,添加进度字段
    """
    user = models.ForeignKey('User', verbose_name='用户')
    series = models.ForeignKey('Series', verbose_name='系列')
    progress = models.CharField(max_length=32, default='0.00',verbose_name='进度')