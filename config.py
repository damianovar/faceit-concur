class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = "c9d652aa9c50c0bf0a4f5af2bd297cea"

    DB_NAME = "production-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    TEX_UPLOADS = "static/uploads/tex"
    ALLOWED_EXTENSIONS = "ZIP"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "KCMap"
    DB_USERNAME = "developer"
    DB_PASSWORD = "bruxellesmagdeburgpadovatrondheimuppsala"
    DB_HOST = "mongodb+srv://developer:bruxellesmagdeburgpadovatrondheimuppsala@la.ntmol.mongodb.net/KCMap?retryWrites=true&w=majority"

    ## old database
    #DB_PASSWORD = "TTK4260"
    #DB_HOST = "mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority"

    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    SESSION_COOKIE_SECURE = False
