import os
from datetime import timedelta

db = os.environ['DB_URL']


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{db}/authentication"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_SECRET_KEY = 'kolkoparatolkomuzike'