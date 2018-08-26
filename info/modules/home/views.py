from info.common import rank_select, user_login_data
from info.constants import HOME_PAGE_MAX_NEWS
from info.models import User, Category, News
from info.modules.home import home_blu
from flask import render_template, current_app, session, jsonify, request, g

from info.utils.response_code import RET, error_map


@home_blu.route("/")
@user_login_data
def index():
    # 将用户登录信息传到模板中
    user = g.user.to_dict() if g.user else None

    # 获得数据库中的新闻分类
    categories = []
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)

    # 获取新闻排名列表
    rank_list = rank_select()
    rank_list = [news.to_basic_dict() for news in rank_list]

    return render_template("news/index.html", user=user, categories=categories, rank_list=rank_list)


@home_blu.route('/favicon.ico')
def get_favicon():
    # 返回静态文件
    return current_app.send_static_file("news/favicon.ico")


@home_blu.route('/get_news_list')
def get_news_list():
    # 获取参数
    cur_page = request.args.get("cur_page")
    cid = request.args.get("cid")
    per_count = request.args.get("per_count", HOME_PAGE_MAX_NEWS)

    # 校验参数
    if not all([cur_page, cid, per_count]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 数据格式转换
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    filter_list = []
    if cid != 1:
        filter_list = [News.category_id == cid]

    # 从数据库中取出新闻列表
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 封装成json
    data = {
        "news_list": [news.to_dict() for news in pn.items],
        "total_page": pn.pages
    }

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)



