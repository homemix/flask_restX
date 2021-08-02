from datetime import datetime

import params as params
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app, doc='/doc',title="A book API",description="A simple REST API for books")
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_restx.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    author = db.Column(db.String(40), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow())

    def __repr__(self):
        return 'self.title'


book_model = api.model('Book',
                       {
                           'id': fields.Integer(),
                           'title': fields.String(),
                           'author': fields.String(),
                           'date_added': fields.DateTime(),
                       })


@api.route('/books')
class Books(Resource):

    @api.marshal_list_with(book_model, code=200, envelope="books")
    def get(self):
        ''' Get all books '''
        books = Book.query.all()
        return books

    @api.marshal_list_with(book_model, code=200, envelope='book')
    @api.doc(params={'title':'a book title','author':'a book author'})
    @api.expect(book_model)
    def post(self):
        ''' Create a book '''
        data = request.get_json()

        title = data.get('title')
        author = data.get('author')

        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return new_book


@api.route('/book/<int:id>')
class BookResource(Resource):

    @api.marshal_list_with(book_model, code=200, envelope='book')
    def get(self, id):
        ''' get a book by id '''
        book = Book.query.get_or_404(id)
        return book

    @api.marshal_list_with(book_model, code=200, envelope='book')
    def put(self, id):
        ''' update a book '''
        book_to_update = Book.query.get_or_404(id)
        data = request.get_json()

        book_to_update.title = data['title']
        book_to_update.author = data['author']
        db.session.commit()
        return book_to_update, 200

    @api.marshal_list_with(book_model, code=200, envelope='book_deleted')
    def delete(self, id):
        ''' delete a book '''
        book_to_delete = Book.query.get_or_404(id)
        db.session.delete(book_to_delete)
        db.session.commit()
        return book_to_delete, 200


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Book': Book
    }


if __name__ == '__main__':
    app.run(debug=True)
