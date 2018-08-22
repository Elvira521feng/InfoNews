from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
import logging
from logging.handlers import RotatingFileHandler
from config import config_dict

# 将数据库操作对象全局话,方便其他文件操作数据库
db = None
sr = None


def set_log():
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)
    # 创建日志记录器,指明日志保存路径/每个日志文件的大小/保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚刚创建的日记记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象(flask app使用)添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(type):
    app = Flask(__name__)

    config_cls = config_dict[type]

    # 配置类加载应用配置
    app.config.from_object(config_cls)

    # 创建MYSQL数据库连接对象
    global db
    db = SQLAlchemy(app)

    # 创建redis连接对象
    global sr
    sr = StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)

    # 初始化session存储对象
    Session(app)

    # 初始化迁移器
    Migrate(app)

    # 注册蓝图
    from info.modules.home import home_blu
    app.register_blueprint(home_blu)

    # 配置日志文件
    set_log()

    # 让模型文件和主程序建立关系
    from info import models

    return app


