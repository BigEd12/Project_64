from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import requests

API_KEY = 'YOUR-API-KEY'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR-SECRET-KEY'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-collection.db"
db = SQLAlchemy(app)


with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String, unique=True, nullable=False)
        rating = db.Column(db.Float, nullable=True)
        ranking = db.Column(db.Integer, nullable=True)
        review = db.Column(db.String, unique=True, nullable=True)
        img_url = db.Column(db.String, unique=True, nullable=False)
    db.create_all()

class FindForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')

class EditForm(FlaskForm):
    rating = StringField('Your Rating Out Of 10, eg. 6.5')
    review = StringField('Your Review')
    submit = SubmitField(label='Update Movie')

@app.route('/')
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route('/add', methods=['POST', 'GET'])
def add():
    form = FindForm()
    if form.validate_on_submit():
        movie_input = form.title.data
        movie = movie_input.replace(' ', '+')
        mdb_link = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie}'
        response = requests.get(mdb_link)
        data = response.json()['results']
        return render_template('select.html', movie_info=data)

    return render_template('add.html', form=form)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = request.form["rating"]
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/find', methods=['GET', 'POST'])
def find_film():
    movie_id = request.args.get('id')
    if movie_id:
        mdb_link = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        mdb_image_link = 'https://image.tmdb.org/t/p/w500'
        response = requests.get(mdb_link)
        data = response.json()
        title = data['title']
        img_url = f"{mdb_image_link}{data['poster_path']}"
        year = data["release_date"].split("-")[0]
        description = data['overview']
        new_movie = Movie(title=title, year=year, description=description, img_url=img_url)
        print(new_movie.id)
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
