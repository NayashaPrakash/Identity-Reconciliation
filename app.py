from types import MethodType
from flask import Flask, request, jsonify
import models

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to Bitespeed's Identity Reconciliation task!"

@app.route('/records', methods=['GET'])
def get_records():
    phone = request.args.get('phoneNumber')
    email = request.args.get('email')
    records = models.query_records(email=email, phone=phone)
    return jsonify(records)

@app.route('/identify', methods=['POST'])
def get_customer():
    data = request.json
    phone = data.get('phoneNumber')
    email = data.get('email')

    records = models.add_or_update_contact(email=email, phone=phone)
    return jsonify(records)

if __name__ == '__main__':
    models.create_customer_table()
    app.run()
