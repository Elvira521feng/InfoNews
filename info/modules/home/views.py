from info.modules.home import home_blu


@home_blu.route("/")
def index():

    return "index"