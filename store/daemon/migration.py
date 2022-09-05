from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import create_database, database_exists
from configdb import Configuration
from models import db

app = Flask(__name__)
app.config.from_object(Configuration)

migrateObject = Migrate(app, db)

flag = False

while not flag:
    try:
        if not database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
            create_database(Configuration.SQLALCHEMY_DATABASE_URI)

        db.init_app(app)

        with app.app_context() as context:
            init()
            migrate()
            upgrade()

            flag = True

    except Exception as e:
        print(e)
