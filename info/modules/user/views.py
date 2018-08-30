from flask import g, redirect, render_template, jsonify, request
from info.common import user_login_data
from info.modules.user import user_blu
from info.utils.response_code import RET, error_map


@user_blu.route('/')
@user_login_data
def index():
    user = g.user
    if not user:
        return redirect("/")

    return render_template("user/user.html", user=user)


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




@user_blu.route('/user_pic_info')
@user_login_data
def user_pic_info():
    user = g.user
    if not user:
        return redirect("/")
    user = user.to_dict()
    return render_template("user/user_pic_info.html", user=user)

