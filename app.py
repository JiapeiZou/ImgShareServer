from flask import Flask
import config
from exts import db, cors, jwt, avatar
from flask_migrate import Migrate
from blueprint.front import front_bp  # 导入蓝图
from blueprint.media import media_bp  # 导入蓝图


app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)
# 初始化数据库实例
db.init_app(app)
# jwt鉴权
jwt.init_app(app)
# 初始化头像
avatar.init_app(app)
# 准许跨域
cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# 将模型映射到数据库----- pip install flask-migrate (三部曲 1.flask db init 2.flask db migrate 3.flask db upgrade)
migrate = Migrate(app, db)

# 注册蓝图
app.register_blueprint(front_bp)
app.register_blueprint(media_bp)


if __name__ == '__main__':
    app.run()
