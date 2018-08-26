from flask import current_app, abort
from flask import render_template

from info.common import rank_select
from info.models import News
from info.modules.news import news_blu


# 显示新闻详情
@news_blu.route('/<int:news_id>')
def news_details(news_id):
    news = None
    print(news_id)

    # 根据id取出新闻内容
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)

    if not news:
        return abort(404)

    # 新闻点击量+1
    news.clicks += 1

    rank_list = rank_select()
    rank_list = [news.to_basic_dict() for news in rank_list]


    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list)