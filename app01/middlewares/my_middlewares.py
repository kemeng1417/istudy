from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, reverse
import re
from istudy import settings


class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        # 需要登陆后访问的地址，需要判断登陆状态
        # 默认所有的地址都需要登陆才能访问
        # 设置访问的白名单
        url = request.path_info
        # 白名单
        for i in settings.WHITE_LIST:
            if re.match(i, url):
                return
        is_login = request.session.get('is_login')
        if is_login:
            return
        return redirect('{}?url={}'.format(reverse('login'), url))
