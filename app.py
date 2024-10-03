from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:568312@localhost/ecommerce_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

class CustomerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('accounts', lazy=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))

# Create the database and tables
with app.app_context():
    db.create_all()

# CRUD Endpoints for Customer
@app.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], email=data['email'], phone_number=data['phone_number'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully'}), 201

@app.route('/customer/<int:id>', methods=['GET'])
def read_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'name': customer.name, 'email': customer.email, 'phone_number': customer.phone_number})

@app.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    customer = Customer.query.get_or_404(id)
    customer.name = data['name']
    customer.email = data['email']
    customer.phone_number = data['phone_number']
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'})

@app.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})

# CRUD Endpoints for CustomerAccount
@app.route('/customeraccount', methods=['POST'])
def create_customer_account():
    data = request.get_json()
    new_account = CustomerAccount(username=data['username'], password=data['password'], customer_id=data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'message': 'Customer account created successfully'}), 201

@app.route('/customeraccount/<int:id>', methods=['GET'])
def read_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    return jsonify({'username': account.username, 'customer': account.customer.name})

@app.route('/customeraccount/<int:id>', methods=['PUT'])
def update_customer_account(id):
    data = request.get_json()
    account = CustomerAccount.query.get_or_404(id)
    account.username = data['username']
    account.password = data['password']
    db.session.commit()
    return jsonify({'message': 'Customer account updated successfully'})

@app.route('/customeraccount/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Customer account deleted successfully'})

# CRUD Endpoints for Product
@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201

@app.route('/product/<int:id>', methods=['GET'])
def read_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({'name': product.name, 'price': product.price})

@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get_or_404(id)
    product.name = data['name']
    product.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([{'name': product.name, 'price': product.price} for product in products])

# Order Processing Endpoints
@app.route('/order', methods=['POST'])
def place_order():
    data = request.get_json()
    new_order = Order(order_date=data['order_date'], customer_id=data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    for item in data['items']:
        new_item = OrderItem(order_id=new_order.id, product_id=item['product_id'], quantity=item['quantity'])
        db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Order placed successfully'}), 201

@app.route('/order/<int:id>', methods=['GET'])
def retrieve_order(id):
    order = Order.query.get_or_404(id)
    items = [{'product': item.product.name, 'quantity': item.quantity} for item in order.items]
    return jsonify({'order_date': order.order_date, 'customer': order.customer.name, 'items': items})

@app.route('/order/<int:id>/track', methods=['GET'])
def track_order(id):
    order = Order.query.get_or_404(id)
    return jsonify({'order_date': order.order_date, 'expected_delivery': '2024-10-10'})  # Example date

if __name__ == '__main__':
    app.run(port=5000)