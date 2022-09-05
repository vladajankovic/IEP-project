from flask import Flask, jsonify
from config import Configuration
from flask_jwt_extended import JWTManager
from models import db, Item, OrderItem, Category
from functions import jwt_admin_only
from sqlalchemy import func


app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


@app.get('/productStatistics')
@jwt_admin_only
def productStatistics():
    stat = []
    items = Item.query.all()

    for item in items:
        sold = 0
        pending = 0
        orders = OrderItem.query.filter(OrderItem.itemID == item.id).all()
        if len(orders) == 0:
            print(item)
            continue
        for o in orders:
            sold += o.requested
            pending += o.requested - o.received
        tmp = jsonify(name=item.name, sold=sold, waiting=pending)
        stat.append(tmp.get_json())

    return jsonify(statistics=stat), 200


@app.get('/categoryStatistics')
@jwt_admin_only
def categoryStatistics():
    c_stat = {}
    stat = []
    res = Category.query.all()
    for r in res:
        c_stat[r.name] = 0
    print(c_stat)

    res = OrderItem.query.group_by(OrderItem.itemID). \
        with_entities(OrderItem.itemID, func.sum(OrderItem.requested), func.sum(OrderItem.received)).all()

    for r in res:
        item_id = r[0]
        sold = int(r[1])
        item = Item.query.filter(Item.id == item_id).first()
        for category in item.categories:
            c_stat[category.name] = c_stat.get(category.name) + sold
    print(c_stat)

    sort_list = [t for t in c_stat.items()]
    print(sort_list)
    sort_list.sort(key=lambda x: x[0])
    sort_list.sort(key=lambda x: x[1], reverse=True)
    print(sort_list)

    for c in sort_list:
        stat.append(c[0])

    return jsonify(statistics=stat), 200


if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=6003)
