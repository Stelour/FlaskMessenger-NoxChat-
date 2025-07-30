import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    USERS_PER_PAGE = 20
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    ADMINS = ['support@noxchat.com']
    # aiosmtpd -n -c aiosmtpd.handlers.Debugging -l localhost:8025
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=utc"}
    }
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')