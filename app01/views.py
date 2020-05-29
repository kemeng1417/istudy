from django.shortcuts import render, redirect
from . import models
import hashlib
from .forms import RegForm, ArticleForm, ArticleDetailForm, CategoryForm
from utils.pagination import Pagination
from django.db.models import Q
from django.http.response import JsonResponse
from django.utils import timezone


# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        user_obj = models.User.objects.filter(username=username, password=md5.hexdigest()).first()
        if user_obj:
            # 登陆成功
            # 保存登陆状态 用户名
            request.session['is_login'] = True
            request.session['username'] = user_obj.username
            request.session['pk'] = user_obj.pk
            url = request.GET.get('url')
            if url:
                return redirect(url)
            return redirect('index')
        error = '登陆名或密码错误'
    return render(request, 'login.html', locals())


def logout(request):
    request.session.delete()
    return redirect('index')


def register(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST, request.FILES)
        if form_obj.is_valid():
            # 注册成功
            # print(request.POST)
            # print(form_obj.cleaned_data)
            # 插入数据库方式一
            # form_obj.cleaned_data.pop('re_password')
            # models.User.objects.create(**form_obj.cleaned_data)
            # 插入数据库方式二
            form_obj.save()
            return redirect('login')
    return render(request, 'register.html', {'form_obj': form_obj})


def search_query(request, field_list):
    query = request.GET.get('query', '')
    q = Q()
    q.connector = 'OR'
    for field in field_list:
        q.children.append(Q(('{}__contains'.format(field), query)))

    return q


def index(request):
    # 查询所有的文章
    all_articles = models.Article.objects.all()
    is_login = request.session.get('is_login')
    username = request.session.get('username')

    return render(request, 'index.html', locals())


def article(request, pk):
    article_obj = models.Article.objects.get(pk=pk)

    return render(request, 'article.html', {'article_obj': article_obj})


def backend(request):
    return render(request, 'dashboard.html')


def article_list(request):
    fields_list = ['title', 'category__title', 'detail__content']
    q = search_query(request, fields_list)

    all_articles = models.Article.objects.filter(q, author=request.user_obj)
    page = Pagination(request, all_articles.count())
    return render(request, 'article_list.html',
                  {'all_articles': all_articles[page.start:page.end], 'page_html': page.page_html})


def article_add(request):
    obj = models.Article(author=request.user_obj)
    form_obj = ArticleForm(instance=obj)
    article_detail_form_obj = ArticleDetailForm()
    if request.method == 'POST':
        form_obj = ArticleForm(request.POST, instance=obj)
        article_detail_form_obj = ArticleDetailForm(request.POST)
        if form_obj.is_valid() and article_detail_form_obj.is_valid():
            # 保存文章内容表
            # detail = request.POST.get('detail')
            # detail_obj = models.ArticleDetail.objects.create(content=detail)
            # 保存文章表
            # 方法一
            # form_obj.cleaned_data['detail_id'] = detail_obj.pk
            # models.Article.objects.create(**form_obj.cleaned_data)
            # 方法二
            detail_obj = article_detail_form_obj.save()
            form_obj.instance.detail_id = detail_obj.pk
            form_obj.save()
            return redirect('article_list')
    return render(request, 'article_add.html',
                  {'form_obj': form_obj, 'article_detail_form_obj': article_detail_form_obj})


def article_edit(request, pk):
    article_obj = models.Article.objects.filter(pk=pk).first()
    article_detail_form_obj = ArticleDetailForm(instance=article_obj.detail)
    form_obj = ArticleForm(instance=article_obj)
    if request.method == 'POST':
        form_obj = ArticleForm(request.POST, instance=article_obj)
        article_detail_form_obj = ArticleDetailForm(request.POST, instance=article_obj.detail)
        if form_obj.is_valid() and article_detail_form_obj.is_valid():
            # form_obj.instance.detail.content = request.POST.get('detail')
            article_detail_form_obj.save()
            # form_obj.instance.detail.save()  # 保存文章详情
            form_obj.save()  # 保存文章信息
            url = request.GET.get('url')
            if url:
                return redirect(url)
            return redirect('article_list')
    return render(request, 'article_edit.html', {'article_obj': article_obj, 'form_obj': form_obj,
                                                 'article_detail_form_obj': article_detail_form_obj})


def article_del(request, pk):
    article_obj = models.Article.objects.filter(pk=pk).first()
    article_obj.delete()
    return redirect('article_list')


user = [{'username': 'username_{}'.format(i), 'pwd': 123} for i in range(1, 466)]


def user_list(request):
    page = Pagination(request, len(user), )
    return render(request, 'user_list.html', {'user': user[page.start:page.end], 'page_html': page.page_html})


def category_list(request):
    all_categories = models.Category.objects.all()
    return render(request, 'category_list.html', {'all_categories': all_categories})


def category_change(request, pk=None):
    obj = models.Category.objects.filter(pk=pk).first()
    form_obj = CategoryForm(instance=obj)
    if request.method == 'POST':
        form_obj = CategoryForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('category_list')
    title = '编辑分类' if pk else '新增分类'
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


def category_del(request, pk):
    models.Category.objects.filter(pk=pk).delete()
    return redirect('category_list')


def comment(request):
    obj = models.Comment.objects.create(**request.GET.dict())
    time = timezone.localtime(obj.time).strftime('%Y-%m-%d %H:%M%S')
    return JsonResponse({'status': True, 'time': time})


def series_list(request):

    all_series = models.Series.objects.filter()
    return render(request, 'series_list.html',
                  {'all_series': all_series})
