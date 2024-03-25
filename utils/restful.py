#  Restful API 前后端通过jaxa交互 接口
from flask import jsonify


#  定义状态码
class HttpCode(object):
    ok = 200  # 响应正常
    unloginerror = 401  # 没有登陆错误
    permissionerror = 403  # 没有权限错误
    paramserror = 400  # 客户端参数错误
    servererror = 500  # 服务器错误


#  返回统一模版
def _restful_response(code, message, data):
    return jsonify({'code': code, 'message': message or "", 'data': data or {}})


def ok(message=None, data=None):
    return _restful_response(code=HttpCode.ok, message=message, data=data)


def unlogin_error(message='没有登陆!'):
    return _restful_response(code=HttpCode.unloginerror, message=message, data=None)


def permission_error(message='没有权限访问！'):
    return _restful_response(code=HttpCode.permissionerror, message=message, data=None)


def params_error(message='参数错误!'):
    return _restful_response(code=HttpCode.paramserror, message=message, data=None)


def server_error(message='服务器开小差啦！'):
    return _restful_response(code=HttpCode.servererror, message=message or '服务器内部错误', data=None)
