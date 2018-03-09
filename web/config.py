##########################################################
#
# This is a sample flask.cfg for developing the Flask App.
#
##########################################################
import os

# Set defaults if environment strings aren't set. This is used for easier developer setup
if "PRIMARY_STEEM_RPC_NODE" not in os.environ:
    os.environ["PRIMARY_STEEM_RPC_NODE"] = "https://api.steemit.com"
    os.environ["SECONDARY_STEEM_RPC_NODE"] = "https://rpc.buildteam.io"

if "YOUTUBE_API_KEY" not in os.environ:
    os.environ['YOUTUBE_API_KEY'] = "AIzaSyC_6S-t0g2_s2MCZZf24cHCM7HPRFF4WHI"

if "DEBUGGING_KEY" not in os.environ:
    os.environ['DEBUGGING_KEY'] = "ca283012190ca76ae2d87426a4345ff16bcab161"

if "FLASK_SECRET_KEY" not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = "Magical mystery tour"

if "POSTGRES_USER" not in os.environ:
    os.environ['POSTGRES_USER'] = "steem"
    os.environ['POSTGRES_HOST'] = "localhost"
    os.environ['POSTGRES_PASS'] = "steem"
    os.environ['POSTGRES_DB'] = "openmic"

# grab the folder of the top-level directory of this project
BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.getcwd())

# Update later by using a random number generator and moving
# the actual key outside of the source code under version control
SECRET_KEY = os.environ['FLASK_SECRET_KEY']
WTF_CSRF_ENABLED = True
DEBUG = True

# SQLAlchemy
postgres_user = os.environ["POSTGRES_USER"]
postgres_host = os.environ["POSTGRES_HOST"]
postgres_pass = os.environ["POSTGRES_PASS"]
postgres_db = os.environ["POSTGRES_DB"]

SQLALCHEMY_DATABASE_URI = f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:5432/{postgres_db}"
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Bcrypt algorithm hashing rounds
BCRYPT_LOG_ROUNDS = 15

# Email settings
MAIL_SERVER = 'smtp'
MAIL_PORT = 1025
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'support@localhost'
MAIL_PASSWORD = 'support'
MAIL_DEFAULT_SENDER = 'support@localhost'

# Uploads
UPLOADS_DEFAULT_DEST = TOP_LEVEL_DIR + '/project/static/img/'
#UPLOADS_DEFAULT_URL = 'http://localhost:5000/static/img/'

UPLOADED_IMAGES_DEST = TOP_LEVEL_DIR + '/project/static/img/'
#UPLOADED_IMAGES_URL = 'http://localhost:5000/static/img/'

# App specifics

STEEM_NODES = [os.environ['PRIMARY_STEEM_RPC_NODE'], os.environ['SECONDARY_STEEM_RPC_NODE']]
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
DEBUGGING_KEY = os.environ['DEBUGGING_KEY']

if "RECREATE_DATABASE" in os.environ and os.environ['RECREATE_DATABASE'].lower() == 'true':
    RECREATE_DATABASE = True
else:
    RECREATE_DATABASE = False
