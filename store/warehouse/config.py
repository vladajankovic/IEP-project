import os

redis = os.environ["REDIS_HOST"]


class Configuration():
    JWT_SECRET_KEY = 'kolkoparatolkomuzike'
    REDIS_HOST = f"{redis}"
    REDIS_ITEMS_LIST = "items"
