
from wtforms import Form, ValidationError
from wtforms.fields import StringField, FileField, IntegerField
from wtforms.validators import Length, EqualTo, Regexp, InputRequired
from models.auth import UserModel
from flask_wtf.file import FileAllowed, FileSize


# ---注册表单校验---
class RegisterForm(Form):
    username = StringField(validators=[Length(min=1, max=20, message='请输入正确长度的用户名！')])
    phone_number = StringField(validators=[Regexp(r'^1[3-9]\d{9}$', message='请输入正确格式的手机号码！')])
    password = StringField(validators=[Length(min=6, max=20, message='请输入正确长度的密码！')])
    confirm_password = StringField(validators=[EqualTo(fieldname='password', message='两次密码不一致！')])


# 自定义校验
# 1.手机号码是否已经被注册过 （在数据库中是否存在）
def validate_phone_number(self, field):
    phone_number = field.data  # 获取用户填写的手机号
    phone = UserModel.query.filter_by(phone_number=phone_number).first()
    if phone:
        raise ValidationError('该手机号码已被注册！')


# --- 登陆校验 ---
class LoginForm(Form):
    phone_number = StringField(validators=[Regexp(r'^1[3-9]\d{9}$', message='手机格式错误!')])
    password = StringField(validators=[Length(min=6, max=20, message='密码不正确！')])


# --- 上传头像图片校验 ---
class UploadAvatarForm(Form):
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'], message='图片格式不符合！'),
                                  FileSize(max_size=1024*1024*5, message="图片不超过5M")])


# ---用户修改个人信息---
class EditSettingForm(Form):
    username = StringField(validators=[Length(min=1, max=20, message='请输入正确长度的用户名！')])


# ---图片上传表单验证---
class UploadImageText(Form):
    # filenames = FieldList(StringField('Filename', validators=[Length(max=60, message='文件名不能超过60个字符！')]),
    #                  min_entries=1, max_entries=10)
    title = StringField(validators=[Length(min=1, max=20, message='请输入正确长度的标题！')])
    detail = StringField(validators=[Length(min=1, max=200, message='请输入正确长度的描述！')])


# ---编辑图片---
class EditImageText(Form):
    post_id = IntegerField(validators=[InputRequired(message='请输入该专辑的id！')])
    title = StringField(validators=[Length(min=1, max=10, message="请输入正确长度的标题")])
    detail = StringField(validators=[Length(min=1, max=200, message='请输入正确长度的描述！')])
    #  imgs = FieldList(StringField('filename', validators=[Length(max=60, message='文件名不能超过60个字符！')]), min_entries=1, max_entries=10)
    #  imgs = FieldList(StringField(validators=[Length(min=1)]), min_entries=1)


# ---意见留言---
class MessageForm(Form):
    msg = StringField(validators=[Length(min=1, max=200, message='请输入正确长度的描述！')])
