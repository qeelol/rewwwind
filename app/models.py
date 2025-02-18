from . import db
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from itsdangerous import URLSafeTimedSerializer as Serializer
import random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stripe_id = db.Column(db.String, nullable=True) # link to stripe api
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image = db.Column(db.String(150), nullable=True, default='profile_image_default.jpg')
    google_account = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(150), nullable=True)
    orderCount = db.Column(db.Integer, nullable=False, default=0)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)  # role table
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 2FA fields
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(100), nullable=True)
    two_factor_expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # favourites
    wishlisted_items = db.Column(db.JSON, nullable=True)

    # Relationship to Cart
    cart_items = db.relationship('Cart', back_populates='user', lazy=True)


    # Relationship to Orders
    orders = db.relationship('Order', back_populates='user', lazy=True)

    # Relationship to Reviews
    reviews = db.relationship('Review', back_populates='user', lazy=True)


    # Reset password methods
    def get_reset_token(self):
      s = Serializer(current_app.config['SECRET_KEY'])
      return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
      s = Serializer(current_app.config['SECRET_KEY'])
      try:
        user_id = s.loads(token, max_age=expires_sec)['user_id']
      except:
        return None

      return User.query.get(user_id)
    
    def generate_2fa_code(self):
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.two_factor_secret = generate_password_hash(code, method='pbkdf2:sha256')
        self.two_factor_expiry = datetime.now() + timedelta(minutes=5)
        return code
    
    def verify_2fa_code(self, code):
        if not self.two_factor_secret or not self.two_factor_expiry:
            return False
        if datetime.now() > self.two_factor_expiry:
            return False
        return check_password_hash(self.two_factor_secret, code)
    
class BillingAddress(db.Model):
  __tablename__ = 'billing_addresses'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  address_one = db.Column(db.String(255), nullable=False)
  address_two = db.Column(db.String(255), nullable=True)  # Optional
  unit_number = db.Column(db.String(15), nullable=False)
  postal_code = db.Column(db.String(20), nullable=False)
  phone_number = db.Column(db.String(20), nullable=False)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class Pickup(db.Model):
  __tablename__ = 'pickup'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  pickup_date = db.Column(db.DateTime(timezone=True), nullable=False)

class PaymentInformation(db.Model):
  __tablename__ = 'payment_information'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  paymentType_id = db.Column(db.Integer, db.ForeignKey('payment_types.id'), nullable=False)  # payment method table
  card_number = db.Column(db.String(16), nullable=False) # store as string since leading zeros
  card_name = db.Column(db.String(255), nullable=False)
  expiry_date = db.Column(db.String(5), nullable=False)
  card_cvv = db.Column(db.String(3), nullable=False) # store as string since leading zeros
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class PaymentType(db.Model):
  __tablename__ = 'payment_types'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  payment_type = db.Column(db.String(50), unique=True, nullable=False)
  payment_information = db.relationship('PaymentInformation', backref='payment_types', lazy=True) # otm

class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  role_name = db.Column(db.String(50), unique=True, nullable=False)
  users = db.relationship('User', backref='role', lazy=True)  # otm

class Product(db.Model):
  __tablename__ = 'products'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(200), nullable=True)
  creator = db.Column(db.String(200), nullable=True)
  description = db.Column(db.Text, nullable=True)
  image_thumbnail = db.Column(db.String(300), nullable=True)
  images = db.Column(db.JSON, nullable=True)  # list of uploaded images
  conditions = db.Column(db.JSON, nullable=True)  # store conditions (name, stock, price)
  is_featured_special = db.Column(db.Boolean, nullable=False)
  is_featured_staff = db.Column(db.Boolean, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
  
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
  category = db.relationship('Category', back_populates='products')

  subcategories = db.relationship('SubCategory', secondary='product_subcategories', back_populates='products')
  
  order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')  # otm orderItem

  cart_entries = db.relationship('Cart', back_populates='product', lazy=True)
  reviews = db.relationship('Review', back_populates='product', lazy=True, cascade='all, delete-orphan')
  rating = db.Column(db.Float, default=0, nullable=True)
  def update_rating(self):
    if self.reviews:
      total_rating = sum(review.rating for review in self.reviews)
      self.rating = round(total_rating / len(self.reviews), 2)
    else:
      self.rating = 0

class Review(db.Model):
  __tablename__ = 'reviews'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  show_username = db.Column(db.Boolean, default=False)
  rating = db.Column(db.Integer, nullable=False)
  description = db.Column(db.String(1000), nullable=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
  product = db.relationship('Product', back_populates='reviews', lazy=True)

  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  user = db.relationship('User', back_populates='reviews', lazy=True)

class Category(db.Model): 
  __tablename__ = 'categories'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  category_name = db.Column(db.String(100), unique=True, nullable=False)

  subcategories = db.relationship('SubCategory', back_populates='category')
  products = db.relationship('Product', back_populates='category')

class SubCategory(db.Model):
  __tablename__ = 'subcategories'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  subcategory_name = db.Column(db.String(100), unique=True, nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

  category = db.relationship('Category', back_populates='subcategories')
  products = db.relationship('Product', secondary='product_subcategories', back_populates='subcategories')

class ProductSubCategory(db.Model):
  __tablename__ = 'product_subcategories'
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
  subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), primary_key=True)

class Order(db.Model):
  __tablename__ = 'orders'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  order_date = db.Column(db.DateTime(timezone=True), default=func.now())
  approval_date = db.Column(db.DateTime(timezone=True))
  delivery = db.Column(db.String(100), nullable=False)
  total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
  status = db.Column(db.String(50), default='Pending', nullable=False)

  voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=True)
  voucher = db.relationship('Voucher', backref='orders', lazy=True)
  
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  user = db.relationship('User', back_populates='orders', lazy=True)

  payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_types.id'), nullable=False)
  payment_type = db.relationship('PaymentType', backref='orders', lazy=True)

  payment_information_id = db.Column(db.Integer, db.ForeignKey('payment_information.id'), nullable=True)
  payment_information = db.relationship('PaymentInformation', backref='orders', lazy=True)

  billing_id = db.Column(db.Integer, db.ForeignKey('billing_addresses.id'), nullable=True)
  billing = db.relationship('BillingAddress', backref='orders', lazy=True)

  pickup_id = db.Column(db.Integer, db.ForeignKey('pickup.id'), nullable=True)
  pickup = db.relationship('Pickup', backref='orders', lazy=True)

  order_items = db.relationship('OrderItem', backref='order', lazy=True) # otm orderitems

  def update_total(self):
    if self.order_items:
      self.total_amount = sum(item.unit_price * item.quantity for item in self.order_items)
    else:
      self.total_amount = 0
    session = Session.object_session(self)
    session.commit()
  
  def update_approval(self):

    if self.status == 'Approved':
      self.approval_date = func.now()
    elif self.status == 'Pending':
      self.approval_date = None
    
    session = Session.object_session(self)
    session.commit()

class OrderItem(db.Model):
  __tablename__ = 'order_items'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False) 
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
  product_condition = db.Column(db.JSON, nullable=False)
  quantity = db.Column(db.Integer, nullable=False)
  unit_price = db.Column(db.Numeric(10, 2), nullable=False)

class Voucher(db.Model):
  __tablename__ = 'vouchers'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  voucher_code = db.Column(db.String(50), unique=True, nullable=False)
  voucher_description = db.Column(db.String(1000), nullable=False)
  voucherType_id = db.Column(db.Integer, db.ForeignKey('voucher_types.id'), nullable=False)
  discount_value = db.Column(db.Float, nullable=False)
  criteria = db.Column(db.JSON, nullable=True)
  eligible_categories = db.Column(db.JSON, nullable=True)
  expiry_days = db.Column(db.Integer, nullable=False)  # Days until expiry after claiming
  is_active = db.Column(db.Boolean, default=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())


class VoucherType(db.Model):
  __tablename__ = 'voucher_types'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  voucher_type = db.Column(db.String(50), unique=True, nullable=False)
  vouchers = db.relationship('Voucher', backref='voucher_types', lazy=True) # otm

class UserVoucher(db.Model):
  __tablename__ = 'user_vouchers'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=False)
  claimed_at = db.Column(db.DateTime(timezone=True), default=func.now())
  expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
  is_used = db.Column(db.Boolean, default=False)
  user = db.relationship('User', backref='vouchers', lazy=True)
  voucher = db.relationship('Voucher', backref='claims', lazy=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_condition = db.Column(db.JSON, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    conditions = db.Column(db.JSON, nullable=True)  # store conditions (name, stock, price)

    user = db.relationship('User', back_populates='cart_items')  # Changed backref name to 'cart_entries'
    product = db.relationship('Product', back_populates='cart_entries')  # Product can appear in multiple carts





class tradeDetail(db.Model):
    __tablename__ = 'trade_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    images = db.Column(db.JSON, nullable=False, default="[]")  
    item_type = db.Column(db.String(100), nullable=False)
    item_condition = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author_artist = db.Column(db.String(255), nullable=True)
    genre = db.Column(db.String(255), nullable=True)
    isbn_or_cat = db.Column(db.String(100), nullable=True)
    trade_number = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")

    user = db.relationship('User', backref='trade_items', lazy=True)

    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now())

    # For shipping and payment NEW!!
    shipping_option = db.Column(db.String(50))
    tracking_number = db.Column(db.String(50), nullable=True)
    street_address = db.Column(db.String(255))
    house_block = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    contact_number = db.Column(db.String(20))

    card_number = db.Column(db.String(4))  
    card_expiry = db.Column(db.String(10))
    card_name = db.Column(db.String(255))


    def add_image(self, filename):
        """ Helper function to add an image filename to the images list """
        if not self.images:
            self.images = []
        self.images.append(filename)
        db.session.commit()



class MailingList(db.Model):
  __tablename__ = 'mailing_list'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  email = db.Column(db.String(150), unique=True, nullable=False)
  unsubscribe_token = db.Column(db.String(100), unique=True, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now()) 

class MailingPost(db.Model):
  __tablename__ = 'mailing_posts'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String(200), nullable=False)
  description = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class ChatHistory(db.Model):
  __tablename__ = 'chat_histories'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  chat = db.Column(db.JSON, nullable=False) 
  admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  support_type = db.Column(db.String(50), nullable=False)
  chat_summary = db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    
  # Relationships
  admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_chats')
  user = db.relationship('User', foreign_keys=[user_id], backref='user_chats')