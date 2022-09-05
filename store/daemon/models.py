from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

db = SQLAlchemy()


class ItemCategory(db.Model):
    __tablename__ = "itemcategory"
    id = sa.Column(sa.Integer, primary_key=True)
    itemID = sa.Column(sa.Integer, sa.ForeignKey("items.id"), nullable=False)
    categoryID = sa.Column(sa.Integer, sa.ForeignKey("categories.id"), nullable=False)


class OrderItem(db.Model):
    __tablename__ = "orderitem"
    id = sa.Column(sa.Integer, primary_key=True)
    orderID = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), nullable=False)
    itemID = sa.Column(sa.Integer, sa.ForeignKey("items.id"), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    received = sa.Column(sa.Integer, nullable=False)
    requested = sa.Column(sa.Integer, nullable=False)


class Item(db.Model):
    __tablename__ = "items"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    price = sa.Column(sa.Float, nullable=False)

    categories = db.relationship("Category", secondary=ItemCategory.__tablename__, back_populates="items")
    orders = db.relationship("Order", secondary=OrderItem.__tablename__, back_populates="items")

    def __repr__(self):
        return f"({self.id}: {self.name}, quantity:{self.quantity}, price:{self.price})"


class Category(db.Model):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)

    items = db.relationship("Item", secondary=ItemCategory.__tablename__, back_populates="categories")

    def __repr__(self):
        return f"{self.name}"


class Order(db.Model):
    __tablename__ = "orders"
    id = sa.Column(sa.Integer, primary_key=True)
    buyer = sa.Column(sa.String(256), nullable=False)
    status = sa.Column(sa.String(256), nullable=False)
    timestamp = sa.Column(sa.String(256), nullable=False)

    items = db.relationship("Item", secondary=OrderItem.__tablename__, back_populates="orders")

    def __repr__(self):
        return f"({self.id}: {self.buyer}, {self.status}, {self.timestamp})"


