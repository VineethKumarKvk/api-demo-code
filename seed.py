from app import app
from models import *
from werkzeug.security import generate_password_hash,check_password_hash

@app.cli.command('db_create')
def createDb():
    db.create_all()
    print('All the tables got created')

@app.cli.command('db_seed')
def seedDb():
    cp1 = CartProduct(cp_id=1,cart_id='1',product_id=2,quantity=2)
    db.session.add(cp1)
    db.session.commit()

    prod1 = Product(product_id=1,product_name='ipad',price=29190.0,seller_id=3,category_id=2)
    prod2 = Product(product_id=2,product_name='crocin',price=10.0,seller_id=4,category_id=5)
    db.session.add(prod1)
    db.session.add(prod2)
    db.session.commit()

    user1 = User(user_id=1,user_name='jack',password=generate_password_hash('pass_word',method='pbkdf2:sha256',salt_length=8),user_role=1)
    user2 = User(user_id=2,user_name='bob',password=generate_password_hash('pass_word',method='pbkdf2:sha256',salt_length=8),user_role=1)
    user3 = User(user_id=3,user_name='apple',password=generate_password_hash('pass_word',method='pbkdf2:sha256',salt_length=8),user_role=2)
    user4 = User(user_id=4,user_name='glaxo',password=generate_password_hash('pass_word',method='pbkdf2:sha256',salt_length=8),user_role=2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()

    cart1 = Cart(cart_id=1,total_amount=20.0,user_id=1)
    cart2 = Cart(cart_id=2,total_amount=0.0,user_id=2)
    db.session.add(cart1)
    db.session.add(cart2)
    db.session.commit()

    category1 = Category(category_id=1,category_name='Fashion')
    category2 = Category(category_id=2,category_name='Electronics')
    category3 = Category(category_id=3,category_name='Books')
    category4 = Category(category_id=4,category_name='Groceries')
    category5 = Category(category_id=5,category_name='Medicines')
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(category3)
    db.session.add(category4)
    db.session.add(category5)
    db.session.commit()

    role1 = Role(role_id=1,role_name='CONSUMER')
    role2 = Role(role_id=2,role_name='SELLER')
    db.session.add(role1)
    db.session.add(role2)
    db.session.commit()
    print('data seeded')

@app.cli.command('db_drop')
def deleteDb():
    db.drop_all()
    db.session.commit()
    print('data bases deleted')