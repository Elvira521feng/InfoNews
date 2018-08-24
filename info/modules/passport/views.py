import random
import re
from datetime import datetime

from info import sr, db
from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from flask import render_template, request, abort, make_response, Response, current_app, jsonify, session

from info.utils.captcha.pic_captcha import captcha
from info.utils.response_code import RET, error_map


@passport_blu.route("/login")
def login():
    return render_template()

# 返回图片验证码
@passport_blu.route('/get_img_code')
def get_img_code():
    """获取图片验证码"""
    # 获取参数---验证码图片id
    img_code_id = request.args.get("img_code_id")
    # 校验参数
    if not img_code_id:
        return abort(403)

    # 生成图片验证码
    name, img_code_text, img_code_bytes = captcha.generate_captcha()

    # 将图片key和验证码文字保存都数据库中
    try:
        sr.set("img_code_id" + img_code_id, img_code_text, ex = 300)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    # 创建自定义相应对象
    response = make_response(img_code_bytes) # type:Response
    response.content_type = "image/jpeg"

    # 返回图片
    return response


# 返回短信验证码
@passport_blu.route("/get_sms_code", methods = ["POST"])
def get_sms_code():
    # 获取参数
    img_code_id = request.json.get("img_code_id")
    mobile = request.json.get("mobile")
    img_code = request.json.get("img_code")

    # 校验参数
    if not all([img_code_id, mobile, img_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据手机号从数据库取出用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 判断用户是否已经注册
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="用户已存在")

    # 根据图片key取出对应的验证码文字
    try:
        real_img_text = sr.get("img_code_id"+img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="key"+error_map[RET.DBERR])

    print(real_img_text)
    print(img_code)

    # 校验图片验证码是否过期
    if not real_img_text:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码已经过期")

    # 验证图片验证码是否正确
    if real_img_text.decode("utf-8") != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码错误")

    # 如果正确就发短信
    # 生成短信验证码
    rand_num = "%04d" % random.randint(0, 9999)
    current_app.logger.info("短信验证码为:%s" % rand_num)
    # result = CCP().send_template_sms(mobile, [rand_num, 1], 1)
    # if result == -1:
    #     return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 将短信验证码保存到数据库中
    try:
        sr.set("sms_code_" + mobile, rand_num, ex=60)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 注册
@passport_blu.route("/register", methods = ["POST"])
def register():
    # 获取参数
    mobile = request.json.get("mobile")
    sms_code = request.json.get("sms_code")
    password = request.json.get("password")

    # 校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not re.match(r"1[35678]\d{9}$", mobile):  # 手机号格式是否合格
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 从数据库中取出短信验证码
    try:
        real_sms_code = sr.get("sms_code_" + mobile)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="1"+error_map[RET.DBERR])

    # 校验验证码
    if not real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码已过期")

    if real_sms_code.decode("utf-8") != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码错误")

    user = User()
    user.mobile = mobile
    # 生成计算属性password,封装加密过程

    user.password = password
    user.nick_name = mobile
    # 记录用户最后登录时间
    user.last_login = datetime.now()

    # 如果正确则存入数据库
    try:
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="2"+error_map[RET.DBERR])

    # 状态保持,免密登录
    session['user_id'] = user.id

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])









