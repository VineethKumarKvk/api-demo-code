from app import app
from flask import jsonify,request,make_response
from models import *
import base64,jwt
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.orm import sessionmaker
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args,**kargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'token is missing'}),401
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],algorithms='HS256')
            print(data)
            current_user = User.query.filter_by(user_id=data['id']).first()
            print(current_user.user_id)
            print(current_user.user_role)
        except:
            return jsonify({'message':'Token is invalid'}),401
        return f(current_user,*args,**kargs)
    return decorated

"""Exam end points starts from here"""

@app.route('/login',methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if auth_header:
        auth_type, credentials = auth_header.split(' ')
        if auth_type == 'Basic':
            username_password = base64.b64decode(credentials).decode('UTF-8')
            username, password = username_password.split(':')
            user = User.query.filter_by(user_name=username).first()
            if(user):
                if check_password_hash(user.password,password):
                    tokens = jwt.encode({'id':user.user_id},app.config['SECRET_KEY'])
                    return make_response(tokens),200
                else:
                    return '',401
            else:    
                return '',401
        return '',401

#consumer end points starts here
@app.route('/api/public/product/search', methods=['GET'])
def get_products():
    searchKey = request.args['keyword']
    products = db.session.query(Product, Category).join(Category, Product.category_id == Category.category_id).filter(Product.product_name.like("%"+searchKey+"%")).all()
    output = []
    if products:
        for product, category in products:
            product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'price': product.price,
                'seller_id': product.seller_id,
                'category': {
                    'category_id': category.category_id,
                    'category_name': category.category_name
                }
            }
            output.append(product_data)
        return jsonify(output),200
    return '',400

@app.route('/api/auth/consumer/cart',methods=['GET'])
@token_required
def cart(current_user):
    if current_user.user_role == 1:
        result = db.session.query(Cart, CartProduct, Product, Category).join(CartProduct, Cart.cart_id == CartProduct.cart_id).join(Product, CartProduct.product_id == Product.product_id).join(Category, Product.category_id == Category.category_id).filter(Cart.user_id == current_user.user_id).all()
        output =[]
        for cart,cartproduct,product,category in result:
            product_data = {
                'product_id':product.product_id,
                'price':product.price,
                'product_name':product.product_name,
                'category':{
                    'category_name':category.category_name,
                    'category_id':category.category_id
                }
            }
            cartproductdata= {
                "product":product_data,
                "cp_id":cartproduct.cp_id
            }
            cartdata = {
                "cartproducts":cartproductdata,
                "cart_id":cart.cart_id,
                "total_amount":cart.total_amount
            }
            output.append(cartdata)
        return jsonify(output),200
    return '',403


@app.route('/api/auth/consumer/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):
    if current_user.user_role == 1:
        user_id = current_user.user_id
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity')

        cart = Cart.query.filter_by(user_id=user_id).first()

        existing_cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()

        if existing_cart_product:
            return '',409

        cart_product = CartProduct(cp_id=CartProduct.query.count()+1,cart_id=cart.cart_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_product)
        db.session.commit()

        cart_products = db.session.query(CartProduct,Product).join(Product).filter(CartProduct.cart_id==cart.cart_id).all()
        print(cart_products )
        total_amount = sum([product.price * cart_product.quantity for cart_product, product in cart_products])

        cart.total_amount = total_amount
        db.session.commit()
        
        return jsonify(total_amount), 200
    return '',403

@app.route('/api/auth/consumer/cart', methods=['PUT'])
@token_required
def update_to_cart(current_user):
    if current_user.user_role == 1:
        user_id = current_user.user_id
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity')

        cart = Cart.query.filter_by(user_id=user_id).first()

        existing_cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()
        existing_cart_product.quantity = quantity
        db.session.commit()

        cart_products = db.session.query(CartProduct,Product).join(Product).filter(CartProduct.cart_id==cart.cart_id).all()
        total_amount = sum([product.price * cart_product.quantity for cart_product, product in cart_products])

        cart.total_amount = total_amount
        db.session.commit()
        return jsonify(total_amount), 200
    return '',403


@app.route('/api/auth/consumer/cart', methods=['DELETE'])
@token_required
def delete_to_cart(current_user):
    if current_user.user_role == 1:
        user_id = current_user.user_id
        product_id = request.json.get('product_id')
        cart = Cart.query.filter_by(user_id=user_id).first()

        existing_cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()
        db.session.delete(existing_cart_product)
        db.session.commit()

        cart_products = db.session.query(CartProduct,Product).join(Product).filter(CartProduct.cart_id==cart.cart_id).all()
        total_amount = sum([product.price * cart_product.quantity for cart_product, product in cart_products])

        cart.total_amount = total_amount
        db.session.commit()
        return jsonify(total_amount), 200
    return '',403

#consumer end points ends here


#seller end point starts here
@app.route('/api/auth/seller/product',methods=['GET'])
@token_required
def get_products_sell(current_user):
    if current_user.user_role == 2:
        result = db.session.query(Product,Category).join(Category).filter(Product.seller_id==current_user.user_id)
        output = []
        for product,category in result:
            res = {
                "Category":{
                    'category_id':category.category_id,
                    'category_name':category.category_name
                },
                'price':product.price,
                'product_id':product.product_id,
                'product_name':product.product_name,
                'seller_id':product.seller_id

            }
            output.append(res)
        return jsonify(output),200
    return '',403


@app.route('/api/auth/seller/product/<int:product_id>',methods=['GET'])
@token_required
def get_products_byID_sell(current_user,product_id):
    if current_user.user_role == 2:
        result = db.session.query(Product,Category).join(Category).filter(Product.product_id==product_id,Product.seller_id==current_user.user_id).all()
        if not result:
            return '',404
        output = []
        for product,category in result:
            res = {
                "Category":{
                    'category_id':category.category_id,
                    'category_name':category.category_name
                },
                'price':product.price,
                'product_id':product.product_id,
                'product_name':product.product_name,
                'seller_id':product.seller_id

            }
            output.append(res)
        return jsonify(output),200
    return '',403


@app.route('/api/auth/seller/product',methods=['POST'])
@token_required
def update_products_byjson_sell(current_user):
    if current_user.user_role == 2:
        product_id = request.json.get('product_id')
        product_name = request.json.get('product_name')
        price = request.json.get('price')
        category_id = request.json.get('category_id')
        
        existing_product = Product.query.filter_by(product_id=product_id).first()
        if existing_product:
            return '',409
        
        new_product = Product(product_id=product_id,product_name=product_name,price=price,seller_id=current_user.user_id,category_id=category_id)
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.product_id),201
    return '',403


@app.route('/api/auth/seller/product',methods=['PUT'])
@token_required
def get_products_putUpdate_sell(current_user):
    if current_user.user_role == 2:
        product_id = request.json.get('product_id')
        price = request.json.get('price')
        existing_product = Product.query.filter_by(product_id=product_id).first()
        if existing_product.seller_id != current_user.user_id:
            return '',404
        existing_product.price=price
        db.session.commit()
        return '',200
    return '',403


@app.route('/api/auth/seller/product/<int:product_id>',methods=['DELETE'])
@token_required
def delete_product_sell(current_user,product_id):
    if current_user.user_role == 2:
        existing_product = Product.query.filter_by(product_id=product_id).first()
        if existing_product.seller_id != current_user.user_id:
            return '',404
        db.session.delete(existing_product)
        db.session.commit()
        return '',200
    return '',403