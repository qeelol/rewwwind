from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Cart, Product
from .forms import AddToCartForm
from . import db


addToCart = Blueprint('addToCart', __name__, template_folder='templates')

@addToCart.route('/cart', methods=['GET'])
@login_required
def view_cart():
    print(f"Current user: {current_user}")  # Debugging: Should print user object
    print(f"Authenticated: {current_user.is_authenticated}")  # Debugging: Should be True
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    #cart_total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('addToCart/cart.html', cart_items=cart_items) #cart_total=cart_total)


@addToCart.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity = max(1, quantity)  # Ensure quantity is at least 1
        db.session.commit()
    flash("Cart updated successfully!")
    return redirect(url_for('addToCart.view_cart'))



@addToCart.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    flash("Item removed from cart!")
    return redirect(url_for('addToCart.view_cart'))

@addToCart.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cartForm = AddToCartForm()
    product = Product.query.filter_by(id=product_id).first() # query the related product
    selected_condition = int(cartForm.condition.data) # index of selected condition from cta form

    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id, product_condition=product.conditions[selected_condition]).first()
    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, product_condition=product.conditions[selected_condition], quantity=1)
        db.session.add(new_item)
    db.session.commit()
    #flash("Item added to cart!")
    return redirect(url_for('addToCart.view_cart'))



#favourites
@addToCart.route('/favorites', methods=['GET'])
@login_required
def favorites_page():
    #Fetch favorite items for the current user
    favorite_items = Cart.query.filter_by(user_id=current_user.id, favorite=True).join(Product).all()
    return render_template('addToCart/favorites.html', favorite_items=favorite_items)


@addToCart.route('/add-to-favorites/<int:product_id>', methods=['POST'])
@login_required
def add_to_favorites(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.favorite = True  # Mark as favorite
        db.session.commit()
        flash("Item added to favorites!", "success")
    else:
        flash("Item not found in cart!", "error")
    return redirect(url_for('addToCart.favorites_page'))


@addToCart.route('/toggle-favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.favorite = not cart_item.favorite  # Toggle favorite status
        db.session.commit()
    return redirect(url_for('addToCart.view_cart'))