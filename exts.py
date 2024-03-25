# 这个文件解决循环引用的问题  (存放扩展文件,插件) 例：flask-sqlalchemy(操控数据库）
from flask_sqlalchemy import SQLAlchemy
# 准许跨域
from flask_cors import CORS
# jwt鉴权 json web token
from flask_jwt_extended import JWTManager
# 头像
from flask_avatars import Avatars

db = SQLAlchemy()  # 数据库
cors = CORS()  # 准许跨域
jwt = JWTManager()  # 鉴权
avatar = Avatars()  # 头像
