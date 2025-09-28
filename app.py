from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
from datetime import datetime


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/libary.sqlite')}"
db.init_app(app)



@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        date_of_death_str = request.form.get('date_of_death')

        # String → date konvertieren
        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date() if birth_date_str else None
            date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date() if date_of_death_str else None
        except ValueError:
            return "Invalid date format", 400

        if name and birth_date:
            author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )
            db.session.add(author)
            db.session.commit()

    return render_template('add_author.html')



with app.app_context(): #data created ✅
  db.create_all()




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)