from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Product
from . import db
from math import ceil

productPagination = Blueprint('productPagination', __name__)

@productPagination.route('/')
def product_pagination():
  products = Product.query.all()

  # count products
  total_products = len(products)

  # pagination
  page = request.args.get('page', 1, type=int)
  per_page = 16

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
      products_query = Product.query.filter(Product.name.ilike(f"%{search_query}%"))
  else:
      products_query = Product.query

  # pagination logic
  total_products = products_query.count()
  products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_products / per_page)
  
  return render_template("/productPagination/products.html", user=current_user, products=products, total_products=total_products, total_pages=total_pages, current_page=page, search_query=search_query)

@productPagination.route('/product/<int:product_id>')
def product_detail(product_id):
    # Query the database for the product
    product = Product.query.get(product_id) 
    if product is None:
       abort(404)
    return render_template("/productPagination/productPage.html", user=current_user, product=product)