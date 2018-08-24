from info.modules.home import home_blu
from flask import render_template


@home_blu.route("/")
def index():

    return render_template("index.html")


@home_blu.route("/1")
def favicon():
    return