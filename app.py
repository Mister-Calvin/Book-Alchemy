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

        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:

            return render_template('add_author.html', error="Author already exists")

        elif name and birth_date:
            author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )
            db.session.add(author)
            db.session.commit()
            return render_template('add_author.html', message="Added new author")
        return render_template('add_author.html', error="Invalid input")
    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not author_id:
            return render_template('add_book.html', authors=authors)


        try:
            publication_year = datetime.strptime(publication_year, "%Y-%m-%d").date() if publication_year else None
        except ValueError:
            return "Invalid publication year", 400

        if isbn and publication_year and title:
            book = Book(
                title=title,
                isbn=isbn,
                publication_year=publication_year,
                author_id=int(author_id)
            )
            db.session.add(book)
            db.session.commit()
            return render_template('add_book.html',authors=authors, message= f'Added {book.title}')
        return render_template('add_book.html',authors=authors,  error= 'Invalid input')

    return render_template('add_book.html', authors=authors)

@app.route('/')
def home():
    sort = request.args.get('sort')
    search_term = request.args.get('search')

    query = Book.query.join(Author)

    if search_term:
        query = query.filter(Book.title.ilike(f"%{search_term}%"))

    if sort == 'title_asc':
        query = query.order_by(Book.title.asc())
    elif sort == 'title_desc':
        query = query.order_by(Book.title.desc())
    elif sort == 'author_asc':
        query = query.order_by(Author.name.asc())
    elif sort == 'author_desc':
        query = query.order_by(Author.name.desc())

    books = query.all()
    return render_template('home.html', books=books)







#with app.app_context(): #data created ✅
  #db.create_all()




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)