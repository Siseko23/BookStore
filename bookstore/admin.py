from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Customer, Order
from . import db

admin = Blueprint('admin', __name__)

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET','POST'])
@login_required
def add_shop_items():
    if current_user.email =="admin@dut.ac.za":
        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data


            flash_sale = form.flash_sale.data


            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            department=form.department.data

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_shop_item =Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.department=department

            new_shop_item.flash_sale = flash_sale


            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added successfully')
                print('Item added')
                return render_template('add-shop-items.html', form=form)
            except Exception as e:
                print(e)
                flash('Item Not Added')

            return render_template('add-shop-items.html', form=form)





        return render_template('add-shop-items.html', form=form)

    return render_template('404.html')

@admin.route('/shop-items', methods=['GET','POST'])
@login_required
def shop_items():
    if current_user.email =="admin@dut.ac.za":
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)

    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.email == "admin@dut.ac.za":
        item_to_update = Product.query.get_or_404(item_id)
        form = ShopItemsForm(obj=item_to_update)  # Pre-fill form with current item data

        if form.validate_on_submit():
            # Update product details
            item_to_update.product_name = form.product_name.data
            item_to_update.current_price = form.current_price.data
            item_to_update.previous_price = form.previous_price.data
            item_to_update.in_stock = form.in_stock.data
            item_to_update.department = form.department.data
            item_to_update.flash_sale = form.flash_sale.data

            # Handle product picture (only update if a new one is uploaded)
            if form.product_picture.data:
                file = form.product_picture.data
                file_name = secure_filename(file.filename)
                file_path = f'./media/{file_name}'
                file.save(file_path)
                item_to_update.product_picture = file_path

            try:
                db.session.commit()
                flash(f'{item_to_update.product_name} updated successfully!', 'success')
                print('Product updated')
                return redirect('/shop-items')
            except Exception as e:
                print('Product not updated:', e)
                flash('Item not updated!', 'danger')
                db.session.rollback()

        return render_template('update_item.html', form=form, item=item_to_update)

    return render_template('404.html')


@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.email =="admin@dut.ac.za":
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One Item deleted')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.email.lower() == "admin@dut.ac.za":

        orders = Order.query.all()
        print("Orders in DB:", orders)  # Debugging
        if not orders:
            flash("No orders found!")
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    # Ensure only admin can update orders
    if current_user.email != 'admin@dut.ac.za':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.home'))

    form = OrderForm()
    order = Order.query.get_or_404(order_id)

    if form.validate_on_submit():
        new_status = form.order_status.data  # Get new status from the form
        try:
            order.update_status(new_status)  # Call the method to update status and pickup details
            flash(f'Order {order_id} updated successfully!', "success")
            return redirect(url_for('views.view_orders'))
        except Exception as e:
            print(f"Error updating order {order_id}: {e}")
            db.session.rollback()


    return render_template('order_update.html', form=form, order=order)



@admin.route('/customers')
@login_required
def display_customers():
    if current_user.email =="admin@dut.ac.za":
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.email =="admin@dut.ac.za":
        return render_template('admin.html')
    return render_template('404.html')




@admin.route('/department/<department_name>', methods=['GET'])
@login_required
def department_books(department_name):
    if current_user.email == "admin@dut.ac.za":
        # Query the products in the selected department
        items = Product.query.filter_by(department=department_name).all()
        return render_template('bookDepartment.html', items=items, department=department_name)
    return render_template('404.html')
