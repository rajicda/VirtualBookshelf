from datetime import date

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField
from wtforms import StringField, DateField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from wtforms.widgets.core import DateInput

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"


class Base(DeclarativeBase):
    pass


# Create the extension
db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)


# CREATE TABLE
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    read_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    # def __repr__(self):
    #     return f'<Book {self.title}>'


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


class BookForm(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    read_year = DateField()
    book_author = StringField('Book Author', validators=[DataRequired()])
    rating: int = SelectField('Rating', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    submit = SubmitField('Add Book!')


class BookFormUpdate(FlaskForm):
    rating: int = SelectField('New Rating', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    submit = SubmitField('Update Book Rating!')


@app.route('/')
def home():
    # READ RECORD
    with app.app_context():
        result = db.session.execute(db.select(Book).order_by(Book.id.asc()))
        all_books = result.scalars().fetchall()
    return render_template('index.html', all_books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = BookForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('add.html', form=form)
        elif form.is_submitted() and form.validate_on_submit():
            # CREATE RECORD
            with app.app_context():
                # Check if book already exists before executing the query
                if db.session.execute(db.select(Book).where(Book.title == form.book_name.data)).scalar():
                    error_message = "A book with that title already exists!"
                    # Show or raise the error as needed
                    return render_template("add.html", form=form,
                                           error_message=error_message)  # For displaying error in a template
                    # raise ValueError(error_message)  # For raising an exception
                new_book = Book(title=form.book_name.data, author=form.book_author.data,
                                read_year=form.read_year.data.strftime("%d - %b - %Y"), rating=form.rating.data)
                db.session.add(new_book)
                db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('add.html', form=form)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    edit_form = BookFormUpdate()
    with app.app_context():
        book_to_update = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
    if request.method == 'POST':
        if not edit_form.validate_on_submit():
            return render_template('edit.html', edit_form=edit_form)
        elif edit_form.is_submitted() and edit_form.validate_on_submit():
            # UPDATE RECORD
            with app.app_context():
                book_to_update = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
                # or book_to_update = db.get_or_404(Book, book_id)
                book_to_update.rating = Book(rating=edit_form.rating.data).rating
                db.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template('edit.html', edit_form=edit_form, book=book_to_update)


@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    # DELETE RECORD
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
