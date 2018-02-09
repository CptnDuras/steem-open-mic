from flask import Flask
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_uploads import UploadSet, IMAGES, configure_uploads
from steem import Steem

from web.app.views import public_blueprint
from web.app.models import db

bcrypt = Bcrypt()
mail = Mail()
pagedown = PageDown()
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()
login_manager = LoginManager()


def create_app(config):
    app = Flask(__name__)
    app.config.from_pyfile(config)

    with app.app_context():
        db.init_app(app)
        db.create_all()
        bcrypt.init_app(app)
        pagedown.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = "users.login"

        # Configure the image uploading via Flask-Uploads
        images = UploadSet('images', IMAGES)
        configure_uploads(app, images)

        steem = Steem(nodes=app.config['STEEM_NODES'])

        app.register_blueprint(public_blueprint)

    return app, db, steem

