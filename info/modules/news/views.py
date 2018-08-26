from flask import current_app, abort, g, jsonify, request
from flask import render_template

from info.common import rank_select, user_login_data
from info.models import News
from info.modules.news import news_blu


# 显示新闻详情
from info.utils.response_code import RET, error_map


@news_blu.route('/<int:news_id>')
@user_login_data
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

    # 查询当前用户是否收藏了该新闻
    is_collect = False
    user = g.user
    if user:
        if news in user.collection_news:
            is_collect = True

    # 将用户登录信息传到模板中
    user = g.user.to_dict() if g.user else None

    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user)


@news_blu.route('/news_collect', methods=["POST"])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 校验参数
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 将数据格式化
    try:
        news_id = int(news_id)
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if action == "collect":
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


