from flask import Blueprint, send_from_directory, current_app

bp = Blueprint('media', __name__, url_prefix="/media")
#  (模版中访问这个地址 返回图片内容，用于渲染）
#  访问路径 media/avatar/abc.jpg


# 访问用户头像
@bp.route('/avatar/<filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)


# 访问上传图片 (模版中访问这个地址 返回图片内容，用于渲染）
@bp.route('/imgs/<filename>')
def get_post_image(filename):
    return send_from_directory(current_app.config['POST_IMAGE_SAVE_PATH'], filename)

