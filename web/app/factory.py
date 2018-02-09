from flask import Flask
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from steem import Steem

from web.app.views import public_blueprint


def create_app(config):
    app = Flask(__name__)
    app.config.from_pyfile(config)

    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    pagedown = PageDown(app)
    migrate = Migrate(app, db)
    auth = HTTPBasicAuth()
    auth_token = HTTPBasicAuth()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    # Configure the image uploading via Flask-Uploads
    images = UploadSet('images', IMAGES)
    configure_uploads(app, images)

    steem = Steem(nodes=app.config['STEEM_NODES'])

    app.register_blueprint(public_blueprint)

    return app, db, steem

