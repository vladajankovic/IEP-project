from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

db = SQLAlchemy()


class UserRole(db.Model):
    __tablename__ = "userroles"
    id = sa.Column(sa.Integer, primary_key=True)
    userID = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    roleID = sa.Column(sa.Integer, sa.ForeignKey("roles.id"), nullable=False)

    def __repr__(self):
        return f"({self.userID}, {self.roleID})"


class User(db.Model):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    forename = sa.Column(sa.String(256), nullable=False)
    surname = sa.Column(sa.String(256), nullable=False)
    email = sa.Column(sa.String(256), nullable=False, unique=True)
    password = sa.Column(sa.String(256), nullable=False)

    roles = db.relationship("Role", secondary=UserRole.__tablename__, back_populates='users')

    def __repr__(self):
        return f"({self.id}: {self.forename}, {self.surname}, {self.email}, {self.password})\n"


class Role(db.Model):
    __tablename__ = "roles"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)

    users = db.relationship("User", secondary=UserRole.__tablename__, back_populates='roles')

    def __repr__(self):
        return f"({self.id}: {self.name})\n"
