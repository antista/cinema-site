from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_conn = 'postgres+psycopg2://admin:12345678@localhost:5432/cinema'

app.config['SQLALCHEMY_DATABASE_URI'] = db_conn
db = SQLAlchemy(app)
app.secret_key = b'yhb77sw9_"F4Q8z\n\xec]/'
passw = '50d3ebfee610786167ef3976f71bd727'

from .views import *
from .admin_views import *
