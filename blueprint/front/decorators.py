from flask import g, redirect, url_for
# 登陆装饰器
# 检测是否登陆状态


def login_required(func):
    def inner(*args, **kwargs):
        if hasattr(g, 'user'):
            func(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    inner.__name__ = func.__name__
    return inner
