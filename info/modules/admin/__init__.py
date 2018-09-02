from flask import Blueprint

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


# 蓝图请求钩子
def check_superuser():
    is_admin = session.get("is_admin")
    if not is_admin and not request.url.endswith("admin/login"):
        return redirect("/")


from .views import *

