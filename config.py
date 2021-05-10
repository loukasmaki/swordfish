import os
basedir = os.path.abs(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ssscccchhuperscheeecreeeet'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') 'smtp.googlemail.com)
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    EVENT_MAIL_SUBJECT_PREFIX = '[Swordfish]'
    EVENT_MAILS_SENDER = 'Swordfish Admin <swordfish@ghfs.se>'
    EVENT_ADMIN = os.environ.get('EVENT_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_U   RI = os.environ.get('DEV_DATABASE_URL') or 'mysql://dev:1234@127.0.0.1/sf')

class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' +os.path.join(basedir, 'data.sqlite')

config = {
    'development' = DevelopmentConfig,
    'testing' = TestingConfig,
    'production' = ProductionConfig,
    'default' = DevelopmentConfig
}