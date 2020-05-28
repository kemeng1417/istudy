from django.shortcuts import render, redirect
from . import models
from django import forms
import re
from django.core.exceptions import ValidationError
import hashlib


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


class RegForm(forms.ModelForm):
    password = forms.CharField(error_messages={'required': '这是必填项'},
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': '密码', 'type': 'password', 'autocomplete': "off"}),
                               label='密码',
                               min_length=6)
    re_password = forms.CharField(error_messages={'required': '这是必填项'},
                                  widget=forms.PasswordInput(
                                      attrs={'placeholder': '确认密码', 'type': 'password', 'autocomplete': "off"}),
                                  label='确认密码',
                                  min_length=6)

    class Meta:
        model = models.User
        fields = '__all__'  # ['username', 'password']
        exclude = ['last_time']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '用户名', 'autocomplete': "off"}),
            'position': forms.TextInput(attrs={'placeholder': '请填写职位', 'autocomplete': "off"}),
            'phone': forms.TextInput(attrs={'placeholder': '手机号', 'autocomplete': "off"}),
            # 'company': forms.Select()
        }
        error_messages = {
            'username': {
                'required': '这是必填项'
            }
        }

    # 局部钩子
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if re.match(r'^1[3-9]\d{9}$', phone):
            return phone
        raise ValidationError('手机号格式不正确')

    def clean(self):
        # 校验唯一性
        self._validate_unique = True
        password = self.cleaned_data.get('password', '')
        re_password = self.cleaned_data.get('re_password')

        if password == re_password:
            md5 = hashlib.md5()
            md5.update(password.encode('utf-8'))
            self.cleaned_data['password'] = md5.hexdigest()
            return self.cleaned_data
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields['company']
        choice = field.choices
        choice[0] = ('', '请选择公司')
        field.choices = choice


def register(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST)
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

    return render(request, 'index.html', locals())


def article(request, pk):
    article_obj = models.Article.objects.get(pk=pk)
    return render(request, 'article.html', {'article_obj': article_obj})


def backend(request):
    return render(request, 'dashboard.html')


def article_list(request):
    all_articles = models.Article.objects.all()
    return render(request, 'article_list.html', {'all_articles': all_articles})
