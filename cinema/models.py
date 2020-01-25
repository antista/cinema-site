from uuid import uuid4
from typing import Optional
from sqlalchemy import func, exc
from cinema.wsgi import db


class Product(db.Model):
    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer)
    count = db.Column(db.Integer)
    reservations = db.relationship('ProductReservation', backref='product', lazy='dynamic')

    @staticmethod
    def add_product(description: str, price: int, count: int) -> Optional[str]:
        product_id = uuid4().hex
        try:
            db.session.add(Product(id=product_id, description=description, price=price, count=count))
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return product_id

    @staticmethod
    def delete_product(product_id: str) -> Optional[bool]:
        if Product.query.get(product_id) is None:
            return
        Product.query.filter_by(id=product_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def update_product(product_id: str, **kwargs) -> Optional[bool]:
        product = Product.query.get(product_id)
        if product is None:
            return
        try:
            if 'description' in kwargs.keys():
                product.description = kwargs['description']
            if 'price' in kwargs.keys():
                product.price = kwargs['price']
            if 'count' in kwargs.keys():
                product.count = kwargs['count']
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return True

    def get_count(self, session_id: str) -> Optional[int]:
        product = Product.query.get(self.id)
        if product is None:
            return
        reserved = db.session.query(
            func.sum(ProductReservation.count)
        ).join(Order).filter(
            Order.session_id == session_id,
            ProductReservation.product_id == self.id,
        ).scalar()
        return product.count - reserved if reserved is not None else product.count

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @staticmethod
    def get_serializable_query():
        res = []
        for product in Product.query.order_by(Product.description).all():
            res.append(product.to_dict())
        return res


class Session(db.Model):
    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    movie = db.Column(db.String(180))
    link = db.Column(db.String(300))
    date = db.Column(db.DateTime, unique=True)
    price = db.Column(db.Integer)
    places = db.Column(db.Integer)
    orders = db.relationship('Order', backref='session', lazy='dynamic')

    @staticmethod
    def add_session(movie: str, link: str, date: str, price: int, places: int) -> Optional[str]:
        session_id = uuid4().hex
        try:
            db.session.add(Session(id=session_id, movie=movie, link=link, date=date, price=price, places=places))
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return session_id

    @staticmethod
    def delete_session(session_id: str) -> Optional[bool]:
        if Session.query.get(session_id) is None:
            return
        Session.query.filter_by(id=session_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def update_session(session_id: str, **kwargs) -> Optional[bool]:
        session = Session.query.get(session_id)
        if session is None:
            return
        try:
            if 'movie' in kwargs.keys():
                session.movie = kwargs['movie']
            if 'link' in kwargs.keys():
                session.link = kwargs['link']
            if 'date' in kwargs.keys():
                session.date = kwargs['date']
            if 'price' in kwargs.keys():
                session.price = kwargs['price']
            if 'places' in kwargs.keys():
                session.places = kwargs['places']
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return True

    def get_tickets_count(self) -> Optional[int]:
        if self is None:
            return
        reserved = db.session.query(
            func.sum(Order.tickets_count)
        ).filter(
            Order.session_id == self.id
        ).scalar()
        return self.places - reserved if reserved is not None else self.places


class Order(db.Model):
    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    customer_email = db.Column(db.String(80), nullable=False)
    tickets_count = db.Column(db.Integer)
    session_id = db.Column(db.String(80), db.ForeignKey('session.id'))
    products = db.relationship('ProductReservation', backref='order', lazy='dynamic')

    @staticmethod
    def add_order(customer_email: str, session_id: str, tickets_count: int) -> Optional[str]:
        order_id = uuid4().hex
        try:
            db.session.add(
                Order(id=order_id, customer_email=customer_email, session_id=session_id,
                      tickets_count=tickets_count))
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return order_id

    @staticmethod
    def delete_order(order_id: str) -> Optional[bool]:
        if Order.query.get(order_id) is None:
            return
        ProductReservation.delete_reservation(order_id)
        Order.query.filter_by(id=order_id).delete()
        db.session.commit()
        return True

    def get_res_sum(self):
        res = self.tickets_count * Session.query.get(self.session_id).price
        for product in ProductReservation.query.filter_by(order_id=self.id).all():
            res += product.count * Product.query.get(product.product_id).price
        return res


class ProductReservation(db.Model):
    order_id = db.Column(db.String(80), db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.String(80), db.ForeignKey('product.id'), primary_key=True)
    count = db.Column(db.Integer)

    @staticmethod
    def add_reservation(order_id: str, product_id: str, count: int) -> Optional[bool]:
        try:
            db.session.add(ProductReservation(order_id=order_id, product_id=product_id, count=count))
            db.session.commit()
        except exc.IntegrityError:
            db.session().rollback()
            return
        return True

    @staticmethod
    def delete_reservation(order_id: str) -> Optional[bool]:
        if ProductReservation.query.filter_by(order_id=order_id).first() is None:
            return
        for reservation in ProductReservation.query.filter_by(order_id=order_id).all():
            ProductReservation.query.filter_by(order_id=order_id, product_id=reservation.product_id).delete()
        db.session.commit()
        return True
