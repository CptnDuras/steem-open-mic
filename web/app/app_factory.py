from flask import Flask
from flask_assets import Environment
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
# from flask_mail import Mail
from flask_pagedown import PageDown
from flask_uploads import UploadSet, IMAGES, configure_uploads
from steem import Steem

from bundles import register_assets
from web.app.views import public_blueprint, api_blueprint
from models import db

bcrypt = Bcrypt()
# mail = Mail()
pagedown = PageDown()
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()
login_manager = LoginManager()


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update({
        "block_start_string": '{&',
        "block_end_string": '&}',
        "variable_start_string": '{$',
        "variable_end_string": '$}',
        "comment_start_string": '{##',
        "comment_end_string": '##}',
    })


def create_app(config):
    app = CustomFlask(__name__)
    app.config.from_pyfile(config)

    with app.app_context():
        db.init_app(app)
        db.create_all()

        bcrypt.init_app(app)
        pagedown.init_app(app)

        login_manager.init_app(app)
        login_manager.login_view = "users.login"

        assets = Environment(app)
        register_assets(assets)

        # Configure the image uploading via Flask-Uploads
        images = UploadSet('images', IMAGES)
        configure_uploads(app, images)

        steem = Steem(nodes=app.config['STEEM_NODES'])

        app.register_blueprint(public_blueprint)
        app.register_blueprint(api_blueprint)

    return app, db, steem

