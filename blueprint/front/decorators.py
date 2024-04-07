from flask import g
from utils import restful
from functools import wraps
# 登陆装饰器
# 检测是否登陆状态


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(g, 'user'):
            return func(*args, **kwargs)
        else:
            return restful.params_error(message="请先登陆！")
    return inner
