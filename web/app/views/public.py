from flask import Blueprint, render_template
from config import DEBUGGING_KEY

public_blueprint = Blueprint("public", __name__)


@public_blueprint.route("/")
def index():
    """
    Index page, this will load the Vue app
    :return:
    """
    return render_template(
        "index.html",
        title="Open Mic"
    )


@public_blueprint.route(f'/api/{DEBUGGING_KEY}/status')
def status():
    """
    This is how we can see how the processing services are doing
    :return:
    """
    return render_template("status.html")

