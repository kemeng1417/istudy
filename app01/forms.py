from django import forms
import re
from django.core.exceptions import ValidationError
from . import models
import hashlib


class BKForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


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


class ArticleForm(BKForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        exclude = ['detail', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['author'].choices = [(self.instance.author_id, self.instance.author.username), ]


class ArticleDetailForm(forms.ModelForm):
    class Meta:
        model = models.ArticleDetail
        fields = '__all__'


class CategoryForm(BKForm):
    class Meta:
        model = models.Category
        fields = '__all__'



class SeriesForm(BKForm):
    class Meta:
        model = models.Series
        fields = '__all__'