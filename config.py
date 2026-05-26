import os


class Config:

    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'coreti_dev'
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:c4p1w5@localhost/coreti'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024