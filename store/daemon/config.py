import os

db = os.environ['DB_URL']
redis = os.environ["REDIS_HOST"]


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{db}/store"
    REDIS_HOST = f"{redis}"
    REDIS_ITEMS_LIST = "items"
