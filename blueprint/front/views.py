# 视图函数
import os
import time
from flask import Blueprint, request, g, current_app
from .forms import RegisterForm, LoginForm, UploadAvatarForm, EditSettingForm, UploadImageText, EditImageText, MessageForm
from models.auth import UserModel, ImageModel, ImageTextModel, MessageModel
from utils import restful
from exts import db
from hashlib import md5
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_avatars import Identicon
from sqlalchemy import or_
from .decorators import login_required
from PIL import Image, ImageFilter  # 获取图片size
import io
import base64

bp = Blueprint('front', __name__, url_prefix='/api')


#  --钩子函数-- before_request:在执行视图函数之前，执行任何通过 @app.before_request 注册的钩子函数
@bp.before_request
@jwt_required(optional=True)
def front_before_request():
    if request.method == "OPTIONS":
        return
    # 从访问令牌中获取用户ID
    identity = get_jwt_identity()
    user = UserModel.query.filter_by(id=identity).first()
    if user:
        setattr(g, 'user', user)


# 生成图片的缩略图函数
# def get_blurred_thumbnail(image_bytes):
#     img = Image.open(io.BytesIO(image_bytes))
#     img.thumbnail((50, 50))  # 宽度和高度分别为 8 像素的缩略图
#     blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))  # 模糊效果
#     buffered = io.BytesIO()
#     blurred_img.save(buffered, format="JPEG")
#     return base64.b64encode(buffered.getvalue()).decode('utf-8')  # 返回：Base64 编码的字符串
# ---生成图片的缩略图函数---
def get_blurred_thumbnail(image_path, *, w=8, h=8):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()  # 读取图片文件到字节序列
    img = Image.open(io.BytesIO(image_bytes))  # 使用PIL Image.open 打开这个字节序列
    # 检查和转换模式  使用透明背景颜色的图片，否则无法生成缩略图）
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    # 保存转换后的图片到字节流，以便生成缩略图
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    new_img = Image.new('RGB', (w, h))
    region_width = width // w
    region_height = height // h
    for i in range(w):
        for j in range(h):
            left = i * region_width
            upper = j * region_height
            right = left + region_width
            bottom = upper + region_height
            region = img.crop((left, upper, right, bottom))
            avg_color = region.resize((1, 1), resample=Image.LANCZOS).getcolors()[0][1]
            new_img.putpixel((i, j), avg_color)

    new_img = new_img.filter(ImageFilter.GaussianBlur(radius=1))
    return new_img


# 格式化处理接口需要的图片数据
def export_data(img_textmodel, img_s):
    # img_textmodel => 图片描述模型
    # img_s => 该模型下 所关联的图片模型的列表

    # 该专辑的第一张图片存储路径 "/Users/jpz/Desktop/flask/flaskProject4/media/img/43af.png"
    image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], img_s[0].filename)
    # 该专辑的第一张图片对应的模糊图存储路径
    small_img_path = os.path.join(current_app.config['BLURRED_IMAGE_SAVE_PATH'], img_s[0].filename)
    small_img = None
    # 检查文件是否存在
    if os.path.exists(small_img_path):
        s_img = Image.open(small_img_path)
        #  将 PIL 图像对象转换为 JPEG 图片字符串
        buffered = io.BytesIO()
        s_img.save(buffered, format='JPEG')
        small_img = base64.b64encode(buffered.getvalue()).decode('utf-8')
    else:
        print("Image not found")
    # 打开并处理图片
    with Image.open(image_path) as img:
        # 在这里可以获取图片的宽高等信息
        width, height = img.size
    filenames = [img.filename for img in img_s]
    # 返回该专辑下的第一张图片的宽，高，缩略图
    item = {
        "id": img_textmodel.id,
        "username": img_textmodel.author.username,
        "user_id": img_textmodel.author.id,
        "user_avatar": img_textmodel.author.avatar,
        "title": img_textmodel.title,
        "detail": img_textmodel.detail,
        "width": width,
        "height": height,
        "filename": filenames,
        "small_img": small_img,
    }
    return item

    # ---------
    # with open(image_path, 'rb') as f:
    #     image_bytes = f.read()  # 读取图片文件到字节序列
    # img = Image.open(io.BytesIO(image_bytes))  # 使用PIL Image.open 打开这个字节序列
    # # 检查和转换模式  使用透明背景颜色的图片，否则无法生成缩略图）
    # if img.mode == 'RGBA':
    #     img = img.convert('RGB')
    # # 保存转换后的图片到字节流，以便生成缩略图
    # buffered = io.BytesIO()
    # img.save(buffered, format="JPEG")
    # image_bytes = buffered.getvalue()
    # # 生成模糊缩略图函数
    # small_img = get_blurred_thumbnail(image_bytes)
    # ---------


# login 视图函数
@bp.post('/login')
def login_page():
    # 获取表单数据-验证数据-存入数据库
    form = LoginForm(request.form)
    if form.validate():
        password = form.password.data
        phone_number = form.phone_number.data
        user = UserModel.query.filter_by(phone_number=phone_number).first()
        if not user:  # 是否已经存在此号码
            return restful.params_error(message='手机号码或密码错误！')
        if not user.password_check(password):  # 密码与之前是否相同
            return restful.params_error(message='手机号码或密码错误！')
        # 创建访问令牌 token
        token = create_access_token(identity=user.id)  # identity 能识别用户的唯一标识符
        # user.image_text
        return restful.ok(message="登陆成功！", data={"token": token, "user": user.to_dict()})
    else:
        message = form.errors
        return restful.params_error(message=message)


# register 视图函数
@bp.post('/register')
def register_page():
    # 获取表单数据-验证数据-存入数据库
    form = RegisterForm(request.form)
    if form.validate():
        phone_number = form.phone_number.data
        user = UserModel.query.filter_by(phone_number=phone_number).first()
        if user:  # 是否已经存在此号码
            return restful.params_error(message='该号码已被注册！')
        username = form.username.data
        user = UserModel.query.filter_by(username=username).first()
        if user:
            return restful.params_error(message="该用户名已被注册！")
        password = form.password.data
        identicon = Identicon()  # 自动生成头像
        filenames = identicon.generate(text=md5(phone_number.encode("utf-8")).hexdigest())
        avatar = filenames[1]
        # 存储在数据库中
        user = UserModel(username=username, password=password, phone_number=phone_number, avatar=avatar)
        db.session.add(user)
        db.session.commit()
        return restful.ok()
    else:
        message = form.errors
        return restful.params_error(message=message)


#  上传用户头像
@bp.post('/avatar/upload')
@login_required
def upload_avatar():
    #  获取数据 -》form验证 -》存储在数据库
    form = UploadAvatarForm(request.files)
    if form.validate():
        image = form.image.data
        filename = image.filename
        # 图片路径解包 acb.jpg ==> (abc,jpg) 拿到图片后缀 (_,ext)  ext=>jpg后缀
        _, ext = os.path.splitext(filename)
        # 加密处理用户头像图片文件名，避免黑客或者用户图片重名
        filename = md5((filename + str(time.time())).encode('utf-8')).hexdigest() + ext
        # 添加图片到文件夹中（路径）
        image_path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
        image.save(image_path)
        #  将用户数据库avatar 替换成新头像
        g.user.avatar = filename
        db.session.commit()
        return restful.ok(data={"filename": filename})
    else:
        message = form.errors
        return restful.params_error(message=message)


#  用户个性信息修改
@bp.post('/user/setting')
@login_required
def user_setting():
    form = EditSettingForm(request.form)
    if form.validate():
        username = form.username.data
        g.user.username = username  # 在全局变量中修改
        db.session.commit()
        return restful.ok(data={'username': username})  # 返回json数据
    else:
        return restful.params_error(message=form.errors)


#  上传图片
@bp.post('/upload/image')
@login_required
def upload_image():
    form = UploadAvatarForm(request.files)
    if form.validate():
        image = form.image.data
        filename = image.filename  # 获取文件名
        _, ext = os.path.splitext(filename)  # 解构后缀
        # 给图片重新命名。防止图片重名，加密后的图片文件
        filename = md5((filename + str(time.time())).encode('utf-8')).hexdigest() + ext
        # 存放路径
        image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], filename)
        image.save(image_path)
        return restful.ok(data={"filename": filename})
    else:
        message = form.errors
        return restful.params_error(message=message)


#  上传图片表单提交
@bp.post('/detail/image')
def detail_image():
    #   前端提交的数据结构 {title: '手绘', detail: '表情包', filenames:  ['c819d.png', 'de77e22f.png']}
    form = UploadImageText(request.form)
    if form.validate():
        title = form.title.data
        detail = form.detail.data
        # 提取 filenames ['c819d.png', 'de77e22f.png']
        filenames = []
        for key in request.form.keys():
            if key.startswith('filenames['):
                filenames.append(request.form[key])
        # 验证 filenames
        if not filenames:
            return restful.params_error(message="请上传图片！")
        # 图片存储位置的字符串 "/Users/jpz/Desktop/flask/flaskProject4/media/img/43af.png"
        small_image_path = os.path.join(current_app.config['BLURRED_IMAGE_SAVE_PATH'], filenames[0])
        image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], filenames[0])
        # 生成模糊缩略图函数
        small_img = get_blurred_thumbnail(image_path)
        # 存放模糊图路径
        small_img.save(small_image_path)
        # 存储标题和描述
        img_text = ImageTextModel(title=title, detail=detail, author_id=g.user.id)
        db.session.add(img_text)
        db.session.flush()  # 获取 img_text 的 id
        # 存储图片文件名
        for image in filenames:
            img = ImageModel(filename=image, text_id=img_text.id)
            db.session.add(img)
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.errors)


# 首页--视图函数
@bp.route('/home/<page>')
def index(page):
    page = int(page)  # 当前页数
    per_count = current_app.config['PER_PAGE_COUNT']  # 每页几条
    start = (page - 1) * per_count
    end = start + per_count
    #  返回用户数据
    image_info_list = []
    image_text_model = ImageTextModel.query.order_by(ImageTextModel.create_time.desc())
    image_all_count = image_text_model.count()
    image_text_s = image_text_model.slice(start, end).all()
    # image_text_s ==》[<ImageTextModel 5>, <ImageTextModel 9>] 需要处理成下面格式
    # [{'username': '小红', 'title': '自然', 'detail': '生活', 'filename': ['4b8c2fe.jpg', '71487.jpeg']},
    # {'username': 'shu 属鼠', 'title': '油画', 'detail': '手绘', 'filename': ['b40810.jpg', 'ef5376a9b.JPG']},
    # {'username': 'shu 属鼠', 'title': '表情包', 'detail': '可爱手绘', 'filename': ['d43af.png', 'dd86.png']}]
    if len(image_text_s) > 0:
        for image_text in image_text_s:
            images = image_text.images
            # 处理数据结构的自定义函数
            item = export_data(image_text, images)
            image_info_list.append(item)
        return restful.ok(data={"image_info_list": image_info_list, "image_all_count": image_all_count})
    else:
        return restful.params_error(message="暂无数据！")


# 用户详情页展示（当前用户的全部照片）
@bp.route('user/picture/<user_id>')
def user_picture(user_id):
    try:
        user = UserModel.query.get(user_id)
    except Exception as e:
        return restful.params_error(message="改用户不存在！")
    # all 图片， 图片数量， 头像， 姓名
    user_img_list = []

    text_list = user.image_text  # 当前用户的详情列表 [<ImageTextModel 8>, <ImageTextModel 9>]
    for text in text_list:
        image_list = text.images  # 详情下图片列表  [<ImageModel 1>, <ImageModel 2>]
        item = export_data(text, image_list)  # 自定义函数，处理数据结构
        filenames = [image.filename for image in image_list]
        items = {
            "title": text.title,
            "detail": text.detail,
            "filename": filenames,
            "id": text.id,
            'width': item['width'],
            'height': item['height'],
            'small_img': item['small_img']
        }
        user_img_list.append(items)

    return restful.ok(data={"avatar": user.avatar,
                            "user_join_time": user.join_time,
                            "username": user.username,
                            "user_img_list": user_img_list})


# 删除图片专辑
@bp.post('/delete/img')
@login_required
def delete_post_image():
    post_id = request.form.get('id')
    if not post_id:
        return restful.params_error('没有传入删除图片的ID！')
    try:
        post = ImageTextModel.query.get(post_id)
    except Exception as e:
        return restful.params_error(message="此专辑不存在！")
    db.session.delete(post)
    db.session.commit()
    return restful.ok(message="专辑删除成功！")


# 修改图片专辑
@bp.post('/update/img')
@login_required
def update_post_image():
    form = EditImageText(request.form)
    if form.validate():
        # ----- 验证 filenames数组
        # 提取数组 ('imgs[0]', '7c322.png') ，('imgs[1]', '595b9.png')
        filenames = []  # ==> ['7c322.png', '595b9.png' ]
        for key in request.form.keys():  # request.form.keys() ==> dict_keys(['title', 'detail', 'imgs[0]', 'imgs[1]'])
            if key.startswith('imgs['):
                filenames.append(request.form[key])
        if not filenames:
            return restful.params_error('图片不能为空！')

        #  ----在数据库中查询 是否存在---
        post_id = form.post_id.data
        try:
            post_img = ImageTextModel.query.get(post_id)
        except Exception as e:
            return restful.params_error("没有该专辑！")
        #  --- 重新赋值 修改图片信息---
        title = form.title.data
        detail = form.detail.data

        small_img_path = os.path.join(current_app.config['BLURRED_IMAGE_SAVE_PATH'], filenames[0])
        if not os.path.exists(small_img_path):  # 如果当前路径下找不到该文件 （说明用户该专辑的首图 与 原来不同，需要重新生成缩略图）
            # 生成模糊缩略图函数
            image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], filenames[0])
            small_img = get_blurred_thumbnail(image_path)
            # 存放模糊图路径
            small_img.save(small_img_path)

        post_img.title = title
        post_img.detail = detail
        for img in post_img.images:  # post_img.images ==》 [<ImageModel 18>, <ImageModel 19>]
            if img.filename not in filenames:
                db.session.delete(img)
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(form.errors)


# 搜索关键字
@bp.route('/search/img')
def search_img():
    q = request.args.get("q")  # /search/img?q=xxx 路径传参数

    result = ImageTextModel.query.filter(or_(ImageTextModel.title.contains(q), ImageTextModel.detail.contains(q))).all()
    image_info_list = []
    # result [<ImageTextModel 5>, <ImageTextModel 9>]
    if len(result) > 0:
        for imgTextmodel in result:
            images = imgTextmodel.images
            # 函数
            item = export_data(imgTextmodel, images)
            image_info_list.append(item)
        return restful.ok(data=image_info_list)
    else:
        return restful.params_error('没有找到相关的图片！')


#  搜索用户名
@bp.route('/search/username')
def search_username():  # /search/username?username=xxx
    username = request.args.get('username')
    users = UserModel.query.filter(UserModel.username.contains(username)).all()
    if len(users) < 1:  # [<UserModel 8Bg3erTghTdYRSJTqwd9pA>, <UserModel VrovN8QYvZxY6zmyFm7rCP>]
        return restful.params_error('没有找到相关的用户！')
    user_info = []
    for user in users:
        item = {
            'uid': user.id,
            'username': user.username,
            "avatar": user.avatar
        }
        user_info.append(item)
    return restful.ok(data=user_info)


# 提交留言
@bp.post('/send/message')
def send_message():
    form = MessageForm(request.form)
    if form.validate():
        msg = form.msg.data
        message = MessageModel(msg=msg)
        db.session.add(message)
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(form.errors)

