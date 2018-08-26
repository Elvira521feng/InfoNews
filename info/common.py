# 定义索引转换器
import functools

from flask import current_app, session, g

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, User


def index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(index, "")


# 按点击量查询新闻
def rank_select():
    # 获取新闻排名列表
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)

    return rank_list


# 登录前判断是否登录
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user

        return f(*args, **kwargs)
    return wrapper