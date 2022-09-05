from flask import Flask, request, jsonify
from functions import jwt_buyer_only, isInt
from models import db, Item, Category, ItemCategory, Order, OrderItem
from sqlalchemy import and_, or_
from config import Configuration
from flask_jwt_extended import JWTManager, get_jwt_identity
from datetime import datetime
import re

app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


@app.get('/search')
@jwt_buyer_only
def search():
    name = ''
    category = ''
    category_list = []
    item_list = []
    for item in request.args.items():
        if "name" in item[0]:
            name = item[1].strip()
        if "category" in item[0]:
            category = item[1].strip()
    if re.search("=", name):
        return jsonify(categories=category_list, products=item_list), 200
    if re.search("=", category):
        return jsonify(categories=category_list, products=item_list), 200

    if name == '' and category == '':
        res = Category.query.all()
        for c in res:
            category_list.append(c.name)
        res = Item.query.all()

        for item in res:
            c_list = []
            for c in item.categories:
                c_list.append(c.name)
            tmp = jsonify(categories=c_list, id=item.id, name=item.name, quantity=item.quantity, price=item.price)
            item_list.append(tmp.get_json())

    elif len(name) > 0 and len(category) == 0:
        items = name.split(",")
        c_list = []
        i_list = []
        for it in items:
            item = it.strip()
            res = Item.query.filter(Item.name.like(f"%{item}%")).all()
            if len(res) == 0:
                continue
            for r in res:
                if r not in i_list:
                    i_list.append(r)

        for item in i_list:
            for c in item.categories:
                if c.name not in c_list:
                    c_list.append(c.name)

            tmp_list = []
            for c in item.categories:
                tmp_list.append(c.name)
            tmp = jsonify(categories=tmp_list, id=item.id, name=item.name, quantity=item.quantity, price=item.price)
            if tmp.get_json() not in item_list:
                item_list.append(tmp.get_json())
        category_list = c_list

    elif len(name) == 0 and len(category) > 0:
        cats = category.split(",")
        c_list = []
        i_list = []
        for c in cats:
            cat = c.strip()
            c1 = Category.query.filter(Category.name.like(f"%{cat}%")).all()
            if len(c1) == 0:
                continue
            for r in c1:
                if r.name not in c_list:
                    c_list.append(r.name)
        category_list = c_list

        for c in c_list:
            items = Item.query.join(ItemCategory).join(Category).filter(Category.name == c).all()
            for item in items:
                if item not in i_list:
                    i_list.append(item)

        for item in i_list:
            tmp_list = []
            for c in item.categories:
                tmp_list.append(c.name)
            tmp = jsonify(categories=tmp_list, id=item.id, name=item.name, quantity=item.quantity, price=item.price)
            if tmp.get_json() not in item_list:
                item_list.append(tmp.get_json())

    else:
        items = []
        categories = []
        i_list = []
        c_list = []
        tmp = name.split(",")
        for t in tmp:
            items.append(t.strip())
        tmp = category.split(",")
        for t in tmp:
            categories.append(t.strip())

        for item in items:
            res = Item.query.join(ItemCategory).join(Category).filter(
                and_(
                    Item.name.like(f"%{item}%"),
                    or_(Category.name.like(f"%{category_name}%") for category_name in categories)
                )
            ).all()
            for r in res:
                if r not in i_list:
                    i_list.append(r)

        for item in i_list:
            tmp_list = []
            for c in item.categories:
                tmp_list.append(c.name)
            tmp = jsonify(categories=tmp_list, id=item.id, name=item.name, quantity=item.quantity, price=item.price)
            if tmp.get_json() not in item_list:
                item_list.append(tmp.get_json())

        for cat in categories:
            res = Category.query.join(ItemCategory).join(Item).filter(
                and_(
                    Category.name.like(f"%{cat}%"),
                    or_(Item.name.like(f"%{n}%") for n in items)
                )
            ).all()
            if len(res) == 0:
                continue
            for r in res:
                if r.name not in c_list:
                    c_list.append(r.name)
        category_list = c_list

    return jsonify(categories=category_list, products=item_list), 200


@app.post('/order')
@jwt_buyer_only
def order():
    data = request.get_json()
    requests = data.get("requests", "")
    print(requests)
    if len(requests) == 0:
        return jsonify(message="Field requests is missing."), 400
    for idx, r in enumerate(requests):
        if "id" not in r.keys():
            return jsonify(message=f"Product id is missing for request number {idx}."), 400
        if "quantity" not in r.keys():
            return jsonify(message=f"Product quantity is missing for request number {idx}."), 400
        if not isInt(r.get("id")):
            return jsonify(message=f"Invalid product id for request number {idx}."), 400
        if not isInt(r.get("quantity")):
            return jsonify(message=f"Invalid product quantity for request number {idx}."), 400
        r["id"] = int(r.get("id"))
        r["quantity"] = int(r.get("quantity"))
        res = Item.query.filter(Item.id == r.get("id")).first()
        if not res:
            return jsonify(message=f"Invalid product for request number {idx}."), 400

    identity = get_jwt_identity()
    new_order = Order(buyer=identity, status="PENDING", timestamp=datetime.now().isoformat())
    db.session.add(new_order)

    pending = False
    order_list = []
    for r in requests:
        i = Item.query.filter(Item.id == r.get("id")).first()
        if r.get("quantity") <= i.quantity:
            Item.query.filter(Item.id == i.id).update({Item.quantity: Item.quantity - r.get("quantity")})
            db.session.commit()
            received = r.get("quantity")
        else:
            received = i.quantity
            Item.query.filter(Item.id == i.id).update({Item.quantity: 0})
            db.session.commit()
            pending = True

        order_item = OrderItem(orderID=new_order.id, itemID=i.id, price=i.price,
                               received=received, requested=r.get("quantity"))
        order_list.append(order_item)

    if not pending:
        Order.query.filter(Order.id == new_order.id).update({Order.status: "COMPLETE"})
    db.session.add_all(order_list)
    db.session.commit()

    return jsonify(id=new_order.id), 200


@app.get('/status')
@jwt_buyer_only
def status():
    orders = []
    identity = get_jwt_identity()
    res = Order.query.filter(Order.buyer == identity).all()
    for r in res:
        stat = r.status
        timestamp = r.timestamp
        sum_price = 0
        products = []
        res1 = OrderItem.query.filter(OrderItem.orderID == r.id).all()
        for r1 in res1:
            price = r1.price
            received = r1.received
            requested = r1.requested
            sum_price += price*requested
            item = Item.query.filter(Item.id == r1.itemID).first()
            c_list = []
            for c in item.categories:
                c_list.append(c.name)
            tmp = jsonify(categories=c_list, name=item.name, price=price, received=received, requested=requested)
            products.append(tmp.get_json())
        tmp = jsonify(products=products, price=sum_price, status=stat, timestamp=timestamp)
        orders.append(tmp.get_json())
    return jsonify(orders=orders), 200


if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=6002)
