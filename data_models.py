from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship('Book', backref='author', lazy=True)



    def __str__(self):
        return f'{self.id}: {self.name} - {self.birth_date}, {self.date_of_death}'


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Date, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)


    def __str__(self):
        return f'{self.id}: {self.title} - {self.publication_year} - {self.isbn}'

