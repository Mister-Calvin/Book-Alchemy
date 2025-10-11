from flask import Flask, request, render_template, redirect, flash
import os
from data_models import db, Author, Book
from datetime import datetime, date


app = Flask(__name__)
app.secret_key = 'dein_geheimer_key'  # darf ein beliebiger String sein
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/libary.sqlite')}"
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Handles adding a new author to the database.

        Validates input fields for logical date order and ensures that
        the author does not already exist. Converts date strings to
        Python date objects, checks for invalid or future dates, and
        provides appropriate error messages for invalid input or
        database errors.

        Returns:
            Rendered HTML template (add_author.html) with success or
            error messages."""
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        date_of_death_str = request.form.get('date_of_death')

        # String → date konvertieren
        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date() if birth_date_str else None
            date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date() if date_of_death_str else None

            today = date.today()

            if birth_date and birth_date > today:
                return render_template('add_author.html', error="Birth date cannot be in the future")

            if date_of_death and date_of_death > today:
                return render_template('add_author.html', error="Date of death cannot be in the future")

            if date_of_death and birth_date and date_of_death < birth_date:
                return render_template('add_author.html', error="Date of death cannot be before birth date")

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

            try:
                db.session.add(author)
                db.session.commit()
                return render_template('add_author.html', message="Added new author")
            except Exception as e:
                db.session.rollback()
                return render_template('add_author.html', error=f"Database error: {e}")

        return render_template('add_author.html', error="Invalid input")

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Handles adding a new book to the database.

        Validates ISBN format (10 or 13 digits), prevents duplicate
        ISBNs, and ensures that the same author does not have duplicate
        book titles. Includes error handling for invalid input and
        database exceptions.

        Returns:
            Rendered HTML template (add_book.html) with success or
            error messages and list of authors. """
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
            # ISBN format check
            if not isbn.isdigit() or len(isbn) not in [10, 13]:
                return render_template('add_book.html', authors=authors,
                                       error="Invalid ISBN format (must be 10 or 13 digits)")

            # Check if ISBN already exists
            existing_isbn = Book.query.filter_by(isbn=isbn).first()
            if existing_isbn:
                return render_template('add_book.html', authors=authors, error="ISBN already exists in the database")

            # Check if the same author already has a book with this title
            existing_title = Book.query.filter_by(title=title, author_id=author_id).first()
            if existing_title:
                return render_template('add_book.html', authors=authors,
                                       error="This author already has a book with this title")

            book = Book(
                title=title,
                isbn=isbn,
                publication_year=publication_year,
                author_id=int(author_id)
            )

            try:
                db.session.add(book)
                db.session.commit()
                return render_template('add_book.html', authors=authors, message=f"Added {book.title}")
            except Exception as e:
                db.session.rollback()
                return render_template('add_book.html', authors=authors, error=f"Database error: {e}")

        return render_template('add_book.html',authors=authors,  error= 'Invalid input')

    return render_template('add_book.html', authors=authors)


@app.route('/')
def home():
    """Displays the main home page with a list of all books.

       Allows sorting by title or author (ascending/descending) and
       filtering via a search term. Joins Author and Book tables for
       combined display.

       Returns:
           Rendered HTML template (home.html) showing filtered and/or
           sorted book data."""
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


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Deletes a book entry from the database.

       Deletes the book by its ID and removes the associated author
       if they no longer have any remaining books. Displays status
       messages via Flask's flash system.

       Args:
           book_id (int): The ID of the book to delete.

       Returns:
           Redirect to the home page after deletion."""
    book = Book.query.get(book_id)
    if book:
        # zuerst die author_id merken
        author_id = book.author_id

        # dann das Buch löschen
        db.session.delete(book)
        db.session.commit()

        # Prüfen, ob der Autor noch Bücher hat
        remaining_books = Book.query.filter_by(author_id=author_id).count()
        if remaining_books == 0:
            author = Author.query.get(author_id)
            if author:
                db.session.delete(author)
                db.session.commit()
                flash(
                    f"'{book.title}' was deleted and the author '{author.name}' was also removed because no books remain.")
            else:
                flash(f"'{book.title}' was deleted.")
        else:
            flash(f"'{book.title}' was deleted.")
    return redirect('/')


def initialize_database_if_missing():
    """Initializes the SQLite database if it does not exist.

        Checks for the existence of the database file and creates
        all required tables if missing. Logs a message when the
        database is newly created."""
    db_path = os.path.join(basedir, 'data/libary.sqlite')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print("Database created!")
initialize_database_if_missing()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)