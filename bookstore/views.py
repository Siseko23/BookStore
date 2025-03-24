from datetime import datetime

import stripe
from flask import Blueprint, render_template, flash, redirect, request,jsonify
from .models import Product, Cart, Review, Order, Wishlist, BookSuggestion
from flask_login import login_required, current_user
from . import db

from flask import url_for


views = Blueprint('views', __name__)


@views.route('/cart')
@login_required
def show_cart():
    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()

    total_amount = sum(item.product.current_price * item.quantity for item in cart_items)

    return render_template('cart.html', cart=cart_items, total=total_amount)


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)



@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount
        }

        return jsonify(data)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount
        }

        return jsonify(data)








@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')





@views.route('/add_review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Handling the form submission
        rating = request.form.get('rating')
        review_text = request.form.get('review_text', '')  # Optional review text

        # Validate the rating
        if not rating or int(rating) < 1 or int(rating) > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return redirect(url_for('views.add_review', product_id=product_id))

        # Create a new review object
        new_review = Review(
            rating=int(rating),
            review_text=review_text,
            customer_id=current_user.id,
            product_id=product_id,
            date_posted=datetime.utcnow()  # Optional: timestamp of review
        )

        # Save the review to the database
        db.session.add(new_review)
        db.session.commit()

        flash('Your review has been submitted!', 'success')
        return redirect(url_for('views.product_details', product_id=product_id))  # Redirect to the product details page

    return render_template('add_review.html', product=product)

@views.route('/product_details/<int:product_id>', methods=['GET'])
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    # Fetch reviews for this product or any other relevant data
    reviews = Review.query.filter_by(product_id=product_id).all()
    return render_template('product_details.html', product=product, reviews=reviews)

@views.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()

    if not cart:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('views.show_cart'))

    line_items = []
    for item in cart:
        line_items.append({
            'price_data': {
                'currency': 'zar',
                'product_data': {
                    'name': item.product.product_name,
                },
                'unit_amount': int(item.product.current_price * 100),  # Convert to cents
            },
            'quantity': item.quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('views.payment_success', _external=True),
            cancel_url=url_for('views.show_cart', _external=True),
            customer_email=current_user.email,
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash("Error creating checkout session", "danger")
        print(e)
        return redirect(url_for('views.show_cart'))


@views.route('/payment-success')
@login_required
def payment_success():
    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()

    # Save the order
    for item in cart_items:
        new_order = Order(
            quantity=item.quantity,
            price=item.product.current_price * item.quantity,
            status="Paid",
            payment_id="Stripe",
            customer_link=current_user.id,
            product_link=item.product.id
        )
        db.session.add(new_order)

    db.session.commit()

    # Clear the cart
    Cart.query.filter_by(customer_link=current_user.id).delete()
    db.session.commit()

    flash("Payment successful! Your order has been placed.", "success")
    return redirect(url_for('views.home'))

@views.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


# Add Item to Wishlist
@views.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    existing_item = Wishlist.query.filter_by(customer_id=current_user.id,
                                             product_id=product_id).first()
    if existing_item:
        flash('Item already in wishlist', 'info')
    else:
        new_item = Wishlist(customer_id=current_user.id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added to wishlist!', 'success')
    return redirect(url_for('views.view_wishlist'))


# View Wishlist
@views.route('/wishlist')
@login_required
def view_wishlist():
    wishlist_items = Wishlist.query.filter_by(customer_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)


# Remove Item from Wishlist
@views.route('/remove_from_wishlist/<int:wishlist_id>')
@login_required
def remove_from_wishlist(wishlist_id):
    item = Wishlist.query.get_or_404(wishlist_id)

    if item.customer_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('views.view_wishlist'))

    db.session.delete(item)
    db.session.commit()
    flash('Item removed from wishlist.', 'success')
    return redirect(url_for('views.view_wishlist'))


# Add Item to Cart from Wishlist
@views.route('/add_to_cart_from_wishlist/<int:wishlist_id>')
@login_required
def add_to_cart_from_wishlist(wishlist_id):
    item = Wishlist.query.get_or_404(wishlist_id)
    if item:
        new_cart_item = Cart(quantity=1, product_link=item.product_id,
                             customer_link=current_user.id)
        db.session.add(new_cart_item)
        db.session.commit()
        db.session.delete(item)
        db.session.commit()
        flash('Item moved to cart.', 'success')
    return redirect(url_for('views.view_wishlist'))


# Suggest a Book Route
@views.route('/suggest-book', methods=['GET', 'POST'])
def suggest_book():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        book_title = request.form.get('book_title')


        if not customer_name or not customer_email or not book_title:
            flash('Please fill in all required fields!', 'danger')
            return redirect(request.referrer)

        new_suggestion = BookSuggestion(
            customer_name=customer_name,
            customer_email=customer_email,
            book_title=book_title

        )
        db.session.add(new_suggestion)
        db.session.commit()
        flash('Your book suggestion has been submitted successfully!', 'success')
        return redirect(url_for('views.suggest_book'))

    return render_template('suggest_book.html')


@views.route('/view-suggestions')
def view_suggestions():
    suggestions = BookSuggestion.query.all()
    return render_template('view_suggestions.html', suggestions=suggestions)



@views.route('/department/<department_name>', methods=['GET'])
def department_books(department_name):
    items = Product.query.filter_by(department=department_name).all()
    return render_template('bookDepartment.html', items=items, department=department_name)


@views.route('/')
def home():
    if current_user.is_authenticated:
        # Get the department of the logged-in user
        user_department = current_user.department

        # Fetch books that are on flash sale **and** belong to the student's department
        items = Product.query.filter_by(flash_sale=True, department=user_department).all()

        # Fetch the current user's cart items
        cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
        cart_ids = [item.product_link for item in cart_items]
    else:
        # Show all flash sale books if no user is logged in
        items = Product.query.filter_by(flash_sale=True).all()
        cart_items = []
        cart_ids = []

    return render_template('home.html', items=items, cart=cart_items, cart_ids=cart_ids, department=user_department if current_user.is_authenticated else "General")
