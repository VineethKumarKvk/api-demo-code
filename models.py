from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,String,Integer,Float,ForeignKey
from app import app
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'ecommerceapp.db')
app.config['SECRET_KEY'] = 'thisissecretkey'
db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'Role'
    role_id = Column(Integer,primary_key=True)
    role_name = Column(String)


class User(db.Model):
    __tablename__ = 'User'
    user_id = Column(Integer,primary_key=True)
    user_name = Column(String)
    password = Column(String)
    user_role = Column(Integer,ForeignKey('Role.role_id'))


class Cart(db.Model):
    __tablename__ = 'Cart'
    cart_id = Column(Integer,primary_key=True)
    total_amount = Column(Float)
    user_id = Column(Integer,ForeignKey('User.user_id'))


class Category(db.Model):
    __tablename__ = 'Category'
    category_id = Column(Integer,primary_key=True)
    category_name = Column(String)


class Product(db.Model):
    __tablename__ = 'Product'
    product_id = Column(Integer,primary_key=True)
    product_name = Column(String)
    price = Column(Float)
    seller_id = Column(Integer,ForeignKey('User.user_id'))
    category_id = Column(Integer,ForeignKey('Category.category_id'))


class CartProduct(db.Model):
    __tablename__ = 'CartProduct'
    cp_id = Column(Integer,primary_key=True)
    cart_id = Column(String,ForeignKey('Cart.cart_id'))
    product_id = Column(Integer,ForeignKey('Product.product_id'))
    quantity = Column(Integer)
