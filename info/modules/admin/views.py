from flask import render_template, request, session, url_for, current_app, redirect, g

from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))

        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="用户名/密码不完整")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).all()
    except BaseException as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据库查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="用户名/或密码错误")

    session["is_admin"] = True
    session["use_id"] = username

    return redirect(url_for("admin.index"))


@admin_blu.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("admin/index.html")


@admin_blu.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)
    return redirect("/")