from flask import Blueprint

home_blu = Blueprint("home", __name__)

# 关联视图
from .views import *
