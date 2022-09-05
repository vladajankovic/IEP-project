import os

db = os.environ['DB_URL']


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{db}/store"
    JWT_SECRET_KEY = 'kolkoparatolkomuzike'
