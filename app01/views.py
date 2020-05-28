from django.shortcuts import render, redirect
from . import models
import hashlib
from .forms import RegForm, ArticleForm


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
    url = request.path_info
    if url:
        return redirect(url)
    return redirect('index')


def register(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST,request.FILES)
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


def index(request):
    # 查询所有的文章
    all_articles = models.Article.objects.all()
    is_login = request.session.get('is_login')
    username = request.session.get('username')
    user_obj = models.User.objects.filter(pk=request.session.get('pk')).first()

    return render(request, 'index.html', locals())


def article(request, pk):
    article_obj = models.Article.objects.get(pk=pk)
    return render(request, 'article.html', {'article_obj': article_obj})


def backend(request):
    return render(request, 'dashboard.html')


def article_list(request):
    all_articles = models.Article.objects.all()
    return render(request, 'article_list.html', {'all_articles': all_articles})


def article_add(request):
    form_obj = ArticleForm()
    if request.method == 'POST':
        form_obj = ArticleForm(request.POST)
        if form_obj.is_valid():
            # 保存文章内容表
            detail = request.POST.get('detail')
            detail_obj = models.ArticleDetail.objects.create(content=detail)
            # 保存文章表
            # 方法一
            # form_obj.cleaned_data['detail_id'] = detail_obj.pk
            # models.Article.objects.create(**form_obj.cleaned_data)
            # 方法二
            form_obj.instance.detail_id = detail_obj.pk
            form_obj.save()
            return redirect('article_list')
    return render(request, 'article_add.html', {'form_obj': form_obj})


def article_edit(request, pk):
    article_obj = models.Article.objects.filter(pk=pk).first()
    form_obj = ArticleForm(instance=article_obj)
    if request.method == 'POST':
        form_obj = ArticleForm(request.POST, instance=article_obj)
        if form_obj.is_valid():
            form_obj.instance.detail.content = request.POST.get('detail')

            form_obj.instance.detail.save() # 保存文章详情
            form_obj.save() # 保存文章信息
            return redirect('article_list')
    return render(request, 'article_edit.html', {'article_obj': article_obj, 'form_obj': form_obj})


def article_del(request, pk):
    article_obj = models.Article.objects.filter(pk=pk).first()
    article_obj.delete()
    return redirect('article_list')