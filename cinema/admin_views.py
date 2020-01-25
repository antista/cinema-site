from functools import wraps
from hashlib import md5

from flask import Response, request, render_template, redirect, url_for, flash

from cinema.models import Product, Session, Order, ProductReservation
from cinema.wsgi import passw, app, db


# db.drop_all()
# db.create_all()


def check_auth(username, password):
    return md5((username + '%' + password).encode()).hexdigest() == passw


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth is None or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def get_login():
    auth = request.authorization
    return auth.username if auth is not None else None


@app.route('/admin')
@requires_basic_auth
def admin_page():
    return render_template('admin/admin_page.html')


@app.route('/admin/products')
@requires_basic_auth
def edit_products():
    return render_template('admin/edit_products.html', products=Product.query.order_by(Product.description))


@app.route('/admin/products/add', methods=['POST'])
@requires_basic_auth
def add_product():
    description = request.form['description']
    price = request.form['price']
    count = request.form['count']
    if not Product.add_product(description=description, price=price, count=count):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_products'))


@app.route('/admin/products/update/<product_id>', methods=['POST'])
@requires_basic_auth
def update_product(product_id):
    description = request.form['description']
    price = request.form['price']
    count = request.form['count']
    if not Product.update_product(product_id=product_id, description=description, price=price, count=count):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_products'))


@app.route('/admin/products/delete/<product_id>')
@requires_basic_auth
def delete_product(product_id):
    if not Product.delete_product(product_id=product_id):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_products'))


@app.route('/admin/sessions')
@requires_basic_auth
def edit_sessions():
    return render_template('admin/edit_sessions.html', sessions=Session.query.order_by(Session.date))


@app.route('/admin/sessions/add', methods=['POST'])
@requires_basic_auth
def add_session():
    movie = request.form['movie']
    link = request.form['link']
    date = request.form['date']
    price = request.form['price']
    places = request.form['places']
    if not Session.add_session(movie=movie, link=link, date=date, price=price, places=places):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_sessions'))


@app.route('/admin/sessions/update/<session_id>', methods=['POST'])
@requires_basic_auth
def update_session(session_id):
    movie = request.form['movie']
    link = request.form['link']
    date = request.form['date']
    price = request.form['price']
    places = request.form['places']
    if not Session.update_session(session_id=session_id, movie=movie, link=link, date=date, price=price, places=places):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_sessions'))


@app.route('/admin/sessions/delete/<session_id>')
@requires_basic_auth
def delete_session(session_id):
    if not Session.delete_session(session_id=session_id):
        flash('Что-то пошло не так. Проверьте введенные данные.')
    return redirect(url_for('edit_sessions'))


@app.route('/admin/orders')
@requires_basic_auth
def edit_orders():
    return render_template('admin/edit_orders.html', orders=Order.query.order_by(Order.session_id, Order.customer_email))


@app.route('/admin/orders/delete/<order_id>')
@requires_basic_auth
def delete_order(order_id):
    Order.delete_order(order_id=order_id)
    return redirect(url_for('edit_orders'))


@app.route('/admin/reservations')
@requires_basic_auth
def edit_reservations():
    return render_template('admin/edit_reservations.html', reservations=ProductReservation.query)
