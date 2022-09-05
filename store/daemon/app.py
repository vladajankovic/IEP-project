from redis import Redis
from config import Configuration
from models import db, Item, Category, ItemCategory, OrderItem, Order
from flask import Flask
from time import time

app = Flask(__name__)
app.config.from_object(Configuration)

db.init_app(app)

with app.app_context() as context:
    with Redis(host=Configuration.REDIS_HOST) as redis:
        while True:
            data = redis.lpop(Configuration.REDIS_ITEMS_LIST)
            if not data:
                continue
            db.session.flush()
            item = data.decode('utf-8')
            item = item.split(':')
            res = Item.query.filter(Item.name == item[1]).first()

            if not res:
                new_item = Item(name=item[1], quantity=int(item[2]), price=float(item[3]))
                db.session.add(new_item)
                db.session.commit()

                cat_list = []
                cats = item[0].split("|")
                for c in cats:
                    cat = c.strip()
                    new_cat = Category.query.filter(Category.name == cat).first()
                    if not new_cat:
                        new_cat = Category(name=cat)
                        db.session.add(new_cat)
                        db.session.commit()
                    cat_list.append(ItemCategory(itemID=new_item.id, categoryID=new_cat.id))
                db.session.add_all(cat_list)
                db.session.commit()

            else:
                flag = False
                cats = item[0].split("|")
                categories = res.categories
                for cat in categories:
                    if cat.name in cats:
                        cats.remove(cat.name)
                    else:
                        flag = True
                if flag:
                    continue

                new_price = (res.quantity * res.price + int(item[2]) * float(item[3])) / (res.quantity + int(item[2]))

                i = Item.query.filter(Item.name == item[1]).first()

                Item.query.filter(Item.name == item[1]).update({Item.quantity: Item.quantity + int(item[2])})
                db.session.commit()
                i = Item.query.filter(Item.name == item[1]).first()

                tmp = i.price*(i.quantity - int(item[2])) + float(item[3])*int(item[2])
                tmp = tmp / i.quantity
                Item.query.filter(Item.name == item[1]).update({Item.price: tmp})
                db.session.commit()

            product = Item.query.filter(Item.name == item[1]).first()
            quantity = product.quantity
            all_orders = OrderItem.query.all()
            for o in all_orders:
                if o.itemID == product.id and quantity != 0:
                    if o.requested - o.received == 0:
                        continue
                    pending = o.requested - o.received
                    if quantity >= pending:
                        quantity -= pending
                        Item.query.filter(Item.id == product.id).update({Item.quantity: quantity})
                        OrderItem.query.filter(OrderItem.id == o.id).update({OrderItem.received: o.requested})
                        db.session.commit()
                    else:
                        OrderItem.query.filter(OrderItem.id == o.id).update(
                            {OrderItem.received: o.received + quantity})
                        Item.query.filter(Item.id == product.id).update({Item.quantity: 0})
                        db.session.commit()
                        quantity = 0
                    if quantity == 0:
                        break

            all_pending_orders = Order.query.filter(Order.status == "PENDING").all()
            for o in all_pending_orders:
                pending = 0
                o1 = OrderItem.query.filter(OrderItem.orderID == o.id).all()
                for o2 in o1:
                    pending += o2.requested - o2.received
                if pending == 0:
                    Order.query.filter(Order.id == o.id).update({Order.status: "COMPLETE"})
                    db.session.commit()
