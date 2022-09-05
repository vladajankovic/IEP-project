from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import create_database, database_exists
from config import Configuration
from models import db, Role, User, UserRole

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

            admin_role = Role(name='admin')
            customer_role = Role(name='customer')
            worker_role = Role(name='worker')

            db.session.add(admin_role)
            db.session.add(customer_role)
            db.session.add(worker_role)
            db.session.commit()

            admin = User(forename='admin', surname='admin', email='admin@admin.com', password='1')
            db.session.add(admin)
            db.session.commit()

            user_role = UserRole(userID=admin.id, roleID=admin_role.id)
            db.session.add(user_role)
            db.session.commit()

            flag = True

    except Exception as e:
        print(e)

