# 定义索引转换器
from flask import current_app

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News


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

