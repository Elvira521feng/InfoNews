from flask import Blueprint

# 创建蓝图对象
passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

# 关联视图
from .views import *


