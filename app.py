from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/libary.sqlite')}"
db.init_app(app)

with app.app_context():
  db.create_all()