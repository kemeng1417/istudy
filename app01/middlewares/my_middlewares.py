from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, reverse
import re
from istudy import settings
from app01 import models

class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        # 需要登陆后访问的地址，需要判断登陆状态
        # 默认所有的地址都需要登陆才能访问
        # 设置访问的白名单
        url = request.path_info

        is_login = request.session.get('is_login')
        if is_login:
            user_obj = models.User.objects.filter(pk=request.session.get('pk')).first()
            request.user_obj = user_obj # 千万不能命名成request.user 因为admin里有内置的user表
            return
        # 白名单
        for i in settings.WHITE_LIST:
            if re.match(i, url):
                return
        return redirect('{}?url={}'.format(reverse('login'), url))


