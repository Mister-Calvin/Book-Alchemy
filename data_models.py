from enum import unique

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Author(db.Model):
    """Represents an author entity in the database.

       Stores basic biographical information about each author,
       including their name, date of birth, and optional date of death.
       Each author can be associated with multiple books through a
       one-to-many relationship.

       Attributes:
           id (int): Primary key identifying the author.
           name (str): The full name of the author.
           birth_date (date): The author's birth date.
           date_of_death (date, optional): The author's date of death.
           books (list): Relationship linking to the author's Book entries."""
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship('Book', backref='author', lazy=True)



    def __str__(self):
        return f'{self.id}: {self.name} - {self.birth_date}, {self.date_of_death}'


class Book(db.Model):
    """Represents a book entity in the database.

       Contains bibliographic information for each book and defines
       a relationship to its author. Includes validation constraints
       such as a unique ISBN and a required foreign key reference.

       Attributes:
           id (int): Primary key identifying the book.
           title (str): The title of the book.
           isbn (str): The book's ISBN number (must be unique).
           publication_year (date): The publication date of the book.
           author_id (int): Foreign key referencing the associated author.
           author (Author): Relationship object linking the book to its author."""
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String,unique=True ,nullable=False)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Date, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)


    def __str__(self):
        return f'{self.id}: {self.title} - {self.publication_year} - {self.isbn}'

