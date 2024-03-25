# 用户数据模型
from exts import db
import shortuuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # 加密密码 | 检测密码
from sqlalchemy_serializer import SerializerMixin  # pip install SQLAlchemy-serializer 模型序列化


class UserModel(db.Model, SerializerMixin):
    serialize_rules = ("-_password",)  # 模型序列化时，去掉密码。使用时user.to_dict()就变成键值对的字符串
    __tablename__ = 'user'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    username = db.Column(db.String(50), nullable=False)  # nullable=False 即该字段是必填的
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    _password = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    avatar = db.Column(db.String(100))

# 重写__init__ ， 用户参数传入明文密码password ==》 加密密码
    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            self.password = kwargs.get('password')  # 给password赋值会执行【写函数】 获取到传入的参数password=的值（原始密码 明文密码）
            kwargs.pop('password')
        super(UserModel, self).__init__(*args, **kwargs)

    @property  # 【读】 访问password时 调用此函数 （取password它的值的时候调用）例：# 读取UserModel.password时 返回_password的值
    def password(self):
        return self._password

    @password.setter  # 【写】 给password赋值时 调用此函数 例： password = kwargs.get('password') 会把参数传递给此函数
    def password(self, new_password):
        self._password = generate_password_hash(new_password, method="pbkdf2")
        print("self._password", new_password, self._password)

    # 返回bool值  加密密码==未加密密码
    def password_check(self, pas):
        return check_password_hash(self.password, pas)


#  每次提交可能有一个标题和描述，但可以有多张图片_______________________________
# ImageTextModel 中存储标题和描述
class ImageTextModel(db.Model):
    __tablename__ = 'image_text'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 外键
    author_id = db.Column(db.String(100), db.ForeignKey('user.id'))
    #  ---relationship关系 ----backref反向引用 (每个外键可以写一个关系)
    author = db.relationship('UserModel', backref=db.backref('image_text'))  # 当前作者的所有图片标题 user.image_text


# ImageModel 中存储每个图片的文件名
class ImageModel(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(100), nullable=False)
    # 外键
    text_id = db.Column(db.Integer, db.ForeignKey('image_text.id'))
    #  ---relationship关系 ----backref反向引用 (每个外键可以写一个关系)
    text = db.relationship('ImageTextModel', backref=db.backref('images'))   # 当前标题的所有图片 image_text.images


# MessageModel 意见留言
class MessageModel(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg = db.Column(db.Text, nullable=False)
