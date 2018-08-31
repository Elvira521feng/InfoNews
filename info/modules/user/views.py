from flask import g, redirect, render_template, jsonify, request, current_app
from info.common import user_login_data
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


#