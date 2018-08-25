from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, Category, News
from info.modules.home import home_blu
from flask import render_template, current_app, session


@home_blu.route("/")
def index():
    # 获取session的值判断用户是否登录
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    # 将用户登录信息传到模板中
    user = user.to_dict() if user else None

    # 获得数据库中的新闻分类
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)

    # 获取新闻排名列表
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except BaseException as e:
        current_app.logger.error(e)

    rank_list = [news.to_basic_dict() for news in rank_list]

    return render_template("index.html", user=user, categories=categories, rank_list=rank_list)


@home_blu.route('/favicon.ico')
def get_favicon():
    # 返回静态文件
    return current_app.send_static_file("news/favicon.ico")


@home_blu.route('/get_news_list')
def get_news_list():
    return ""

