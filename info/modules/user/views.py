from flask import g, redirect, render_template, jsonify, request, current_app, abort

from info import db
from info.common import user_login_data
from info.constants import USER_COLLECTION_MAX_NEWS
from info.models import News, tb_user_collection, Category
from info.modules.user import user_blu
from info.utils.image_storage import upload_img
from info.utils.response_code import RET, error_map


@user_blu.route('/')
@user_login_data
def index():
    user = g.user
    if not user:
        return redirect("/")

    return render_template("user/user.html", user=user.to_dict())


# 查看/修改个人基本信息
@user_blu.route('/user_info', methods=["GET", "POST"])
@user_login_data
def user_info():
    # 判断用户是否登录
    user = g.user
    if not user:
        return redirect("/")

    # get请求获取用户基本信息
    if request.method == "GET":
        user = user.to_dict()
        return render_template("user/user_base_info.html", user=user)

    # post请求修改用户信息
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    user.gender = gender
    user.nick_name = nick_name
    user.signature = signature

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 查看修改头像
@user_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    # 判断用户是否登录
    user = g.user
    if not user:
        return redirect("/")

    if request.method == "GET":
        return render_template("user/user_pic_info.html", user=user.to_dict())

    try:
        img_bytes = request.files.get("avatar").read()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        file_name = upload_img(img_bytes)
        print(file_name)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    user.avatar_url = file_name

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


# 修改密码
@user_blu.route('/user_pass_info', methods=["GET", "POST"])
@user_login_data
def user_pass_info():
    # 判断用户是否登录
    user = g.user
    if not user:
        return redirect("/")

    if request.method == "GET":
        return render_template("user/user_pass_info.html", user=user)

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not user.check_password(old_password):
            return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])

    # 设置新密码
    user.password = new_password

    return render_template("user/user_pass_info.html", user=user)


# 我的收藏
@user_blu.route('/user_collection')
@user_login_data
def user_collection():
    user = g.user
    if not user:
        return abort(404)

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 将当前用户的所有收藏传到模板中
    news_list = []
    total_page = 1
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "news_list": [news.to_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("user/user_collection.html", data=data)


@user_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    # 判断用户是否登录
    user = g.user
    if not user:
        return redirect("/")

    # 获得新闻的所有分类
    categories = []
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
        return render_template("user/user_news_release.html", categories=categories)

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    content = request.form.get("content")

    try:
        img_bytes = request.files.get("index_image").read()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    print(title, category_id, digest, img_bytes, content)

    if not all([title, category_id, digest, img_bytes, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        file_name = upload_img(img_bytes)
        print(file_name)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    try:
        category_id = int(category_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    news = News()
    news.title = title
    news.digest = digest
    news.category_id = category_id
    news.content = content
    news.index_image_url = file_name

    # 设置其他属性
    news.user_id = user.id
    news.status = 1
    news.source = "个人发布"

    db.session.add(news)

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/news_list')
@user_login_data
def news_list():
    # 判断用户是否登录
    user = g.user
    if not user:
        return abort(404)

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 将当前用户的所有发布的新闻传到模板中
    news_list = []
    total_page = 1
    try:
        pn = user.news_list.order_by(News.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "news_list": [news.to_review_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("user/user_news_list.html", data=data)

