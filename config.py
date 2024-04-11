# 配置文件
import os
from datetime import timedelta  # 延迟时间

# 项目的根路径
BASE_DIR = os.path.dirname(__file__)  # 当前文件所在的文件夹

# ----配置文件----
# 数据库的配置信息 （数据库的用户名/密码/mysql主机名/端口号/数据库的名字/
DB_USERNAME = "root"
DB_PASSWORD = "rootroot"
DB_HOST = "127.0.0.1"  # 数据库主机名（本地电脑）
DB_POST = 3306  # 端口号
DB_NAME = "database_learn4"

# DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
DB_URI = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4" % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_POST, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
# 密钥 CSRF 保护
SECRET_KEY = 'secret key'
# 头像配置 存放路径
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'media', 'avatars')
# 帖子图片 存放路径
POST_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, 'media', 'imgs')
# 模糊图 存放路径
BLURRED_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, 'media', 'blurredImg')
# 设置jwt过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=100)
# 分页器每页几条数据
PER_PAGE_COUNT = 20
