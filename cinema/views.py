import json

from cinema.mails import send_order_info
from cinema.models import Session, Product, Order, ProductReservation
from cinema.wsgi import app
from flask import redirect, render_template, url_for, request

import locale

locale.setlocale(locale.LC_ALL, "ru")


@app.route('/')
def empty():
    return redirect(url_for('about'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/sessions')
def sessions():
    return render_template('sessions.html', sessions=Session.query.order_by(Session.date),
                           products=Product.query.order_by(Product.description).all(),
                           products_dict=json.dumps(Product.get_serializable_query()))


@app.route('/order/create/<session_id>', methods=['POST'])
def order(session_id):
    email = request.form['customer_email']
    tickets_count = request.form['tickets_count']
    order_id = Order.add_order(email, session_id, tickets_count)
    order = Order.query.get(order_id)
    session = Session.query.get(session_id)
    res_sum = int(tickets_count) * int(session.price)
    for product in Product.query.all():
        product_count = request.form[product.id + '_count']
        ProductReservation.add_reservation(order_id, product.id, product_count)
        res_sum += int(product.price) * int(product_count)
    send_order_info(email, order_id[:6], session.movie, session.date, order.get_res_sum())
    return render_template('order.html', email=email)


@app.route('/price')
def price():
    return render_template('products.html', products=Product.query.order_by(Product.description))


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')
