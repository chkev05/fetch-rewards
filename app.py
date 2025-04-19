import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import math

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ReceiptTable(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID string
    data = db.Column(db.JSON)

with app.app_context():
    db.create_all()

@app.route('/receipts/process', methods=['POST']) # task 1
def process_receipt():
    receipt = request.get_json()

    if not receipt:
        return jsonify({"error": "Invalid JSON"}), 400

    receipt_id = str(uuid.uuid4()) 

    new_receipt = ReceiptTable(
        id = receipt_id,
        data = receipt
    )
    db.session.add(new_receipt)
    db.session.commit()

    # returns example json { "id": "7fb1377b-b223-49d9-a31a-5a02701dd310" }
    return jsonify({
        "id": f"{receipt_id}"
    }), 200


@app.route('/receipts/<id>/points', methods=['GET']) # task 2
def get_points(id):

    receipt = db.session.get(ReceiptTable, id)

    receipt = receipt.data

    # print("hello", receipt)

    res = 0

    if receipt:

        # 1 point for every alpha numberic character in name
        print(0, sum(c.isalnum() for c in receipt["retailer"]))
        res += sum(c.isalnum() for c in receipt["retailer"])

        dollars, cents = receipt["total"].split(".")
        # 50 points if total is a round dollar number iwth no cents
        if cents == "00":
            print(1, "+50")
            res += 50
        
        # 25 points if cents is multiple of 25
        if int(cents) % 25 == 0: # this can also be done by just checking if cents is 00 25 50 75
            print(2, "+25")
            res += 25
        
        # 5 points for every 2 items on teh receipt
        print(3, 5 * (len(receipt["items"]) // 2))
        res += 5 * (len(receipt["items"]) // 2)


        # * If the trimmed length of the item description is a multiple of 3, multiply the price by `0.2` and round up to the nearest integer. 
        #The result is the number of points earned.
        for item in receipt["items"]:
            description = item["shortDescription"]
            price = item["price"]
            if len(description.strip()) % 3 == 0:
                print(4, math.ceil(float(price) * 0.2))
                res += math.ceil(float(price) * 0.2)
        
        # 6 points if day purchased is odd
        year, month, day = receipt["purchaseDate"].split("-")
        if int(day) % 2:
            print(5, 6)
            res += 6
        
        # 10 points if time purchased is between 2 and 4 pm not inlcuding 2 and 4pm
        hour, minute = receipt["purchaseTime"].split(":")
        # if 14 <= int(hour) < 16 or (int(hour) == 16 and int(minute) == 0):
        #     print(6, 10)
        #     res += 10

        if (int(hour) == 14 and int(minute) > 0) or int(hour) == 15:
            res += 10
        
        return jsonify({"points": res}), 200
        
    else:
        return jsonify({"error": "Receipt not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)