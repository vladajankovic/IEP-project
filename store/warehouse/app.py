from flask import Flask, request, Response, jsonify
from redis import Redis
from flask_jwt_extended import JWTManager
from functions import jwt_worker_only, isInt, isFloat
from config import Configuration
import io
import csv


app = Flask(__name__)
app.config.from_object(Configuration)

jwt = JWTManager(app)


@app.post('/update')
@jwt_worker_only
def update():
    with Redis(host=Configuration.REDIS_HOST) as redis:

        content = request.files.get("file", None)
        if content is None:
            return jsonify(message="Field file is missing."), 400
        content = content.stream.read().decode('utf-8')
        stream = io.StringIO(content)
        reader = csv.reader(stream)

        item_list = []
        for idx, row in enumerate(reader):
            if len(row) != 4:
                return jsonify(message=f"Incorrect number of values on line {idx}."), 400
            categories = row[0].strip()
            name = row[1].strip()
            quantity = row[2].strip()
            price = row[3].strip()
            if not isInt(quantity):
                return jsonify(message=f"Incorrect quantity on line {idx}."), 400
            if not isFloat(price):
                return jsonify(message=f"Incorrect price on line {idx}."), 400
            item = f"{categories}:{name}:{quantity}:{price}"
            item_list.append(item)

        for item in item_list:
            redis.rpush(Configuration.REDIS_ITEMS_LIST, item)

    return Response(status=200)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6001)
