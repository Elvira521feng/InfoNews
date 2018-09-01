from datetime import datetime

from flask import current_app, abort, g, jsonify, request
from flask import render_template

from info import db
from info.common import rank_select, user_login_data
from info.models import News, Comment
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
    is_collected = False
    user = g.user
    if user:
        if news in user.collection_news:
            is_collected = True

    # 将用户登录信息传到模板中
    # user1 = g.user.to_dict() if g.user else None
    user = g.user
    # print("user1",user1.id)

    # 将当前新闻的评论取出传到模板中渲染
    try:
        comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 查询新闻中那些评论是被该用户点赞的
    comment_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        is_comment_like = False
        if user:
            if comment in user.up_comments:
                is_comment_like = True
        comment_dict['is_comment_like'] = is_comment_like
        comment_list.append(comment_dict)

    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user.to_dict(), comment_list=comment_list, is_collected=is_collected)


# 收藏新闻
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


# 点赞评论
@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    # 校验参数
    if not all([action, comment_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 将数据格式化
    try:
        comment_id = int(comment_id)
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断用户操作
    if action not in ["remove", "add"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if action == "add":
        if comment not in user.up_comments:
            user.up_comments.append(comment)
            comment.like_count += 1
    else:
        if comment in user.up_comments:
            user.up_comments.remove(comment)
            comment.like_count -= 1

    print(user.up_comments.all())

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())


# 发布评论
@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def news_comment():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 校验参数
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 格式化数据
    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 从数据库取到新闻
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    print("============")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 生成评论模型
    comment = Comment()
    comment.content = content
    comment.news_id = news_id
    comment.create_time = datetime.now()
    comment.user_id = user.id

    if parent_id:
        try:
            parent_id = int(parent_id)
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        comment.parent_id = parent_id

    # 添加数据到数据库中
    try:
        db.session.add(comment)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    print("+++++++++++++++++++++++++++++")
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())










