from flask import g
from utils import restful
# 登陆装饰器
# 检测是否登陆状态


def login_required(func):
    def inner(*args, **kwargs):
        if hasattr(g, 'user'):
            return func(*args, **kwargs)
        else:
            return restful.params_error(message="请先登陆！")

    inner.__name__ = func.__name__
    return inner
