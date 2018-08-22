from datetime import timedelta
from redis import StrictRedis


class Config(object):
    """自定义配置信息类"""
    # 是否开启debug
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:950521@127.0.0.1:3306/infonews"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session存储的数据类型
    SESSION_TYPE = "redis"
    # 设置session存储使用redis连接对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 对cookie中保存的session进行加密
    SESSION_USE_SIGNER = True
    # 应用秘钥
    SECRET_KEY = "DxY3z7jndzYaiY1ndZh+OJOv800zHpRZiWwwNBjC5PAQ1IEMMcWqiyQ8xn2lvi"
    # 设置session存储时间
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DeveloperConfig(Config):
    """定义开发环境的配置"""
    DEBUG = True


class ProductConfig(Config):
    """定义生产环境的配置"""
    DEBUG = False


# 设置配置字典
config_dict = {
    "dev" : DeveloperConfig,
    "pro" : ProductConfig
}



