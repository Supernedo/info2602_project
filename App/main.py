import os
from flask import Flask, render_template, jsonify
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from App.database import init_db
from App.config import load_config

from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views

#Temp imports
from App.models import Movie, User, Review, Movie_Review
from flask import request, redirect, url_for
from sqlalchemy import func
import random, json
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, unset_jwt_cookies, set_access_cookies


def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401

    # =================Temp Routes================

    # Home Page
    @app.route('/home', methods=['GET'])
    def home_page():
        movieSearch = request.args.get('s')
        per_page = 25
        
        if movieSearch:
            movies = Movie.query.filter(Movie.title.ilike(f'%{movieSearch}%')).paginate(page=1, per_page=per_page)
        else:
            movies = Movie.query.paginate(page=1, per_page=per_page)
        
        # Variables for template
        page = request.args.get('page', 1, type=int)
        random_movie = Movie.query.order_by(func.random()).first()

        while (random_movie.thumbnail == "Movie_Thumbnail_Link"):
            random_movie = Movie.query.order_by(func.random()).first()

        total = movies.total

        return render_template('home_page.html', movies=movies, random_movie=random_movie, total=total, page_count=per_page, current_page=page)

    # Movies Page
    @app.route('/movies', methods=['GET'])
    def movies_page_view ():
        movieSearch = request.args.get('s')
        page = request.args.get('page', 1, type=int)
        
        per_page = 25
        
        if movieSearch:
            movies = Movie.query.filter(Movie.title.ilike(f'%{movieSearch}%')).paginate(page=page, per_page=per_page)
        else:
            movies = Movie.query.paginate(page=page, per_page=per_page)
        
        total = movies.total

        return render_template('movies_page.html', movies=movies, total=total, page_count=per_page, current_page=page)
    
    # Movie Review Page
    @app.route('/<href>/review')
    @jwt_required()
    def review_page_view(href):
        current_movie = Movie.query.filter_by(href=href).first()

        if current_movie:
            all_movies = Movie.query.all()
            movie_data = []

            # Find the index of current_movie in the list of all movies
            current_movie_index = all_movies.index(current_movie)

            # Slice the list to get the next 25 movies starting from the index of current_movie
            next_movies = all_movies[current_movie_index + 1: current_movie_index + 26]

            for movie in next_movies:
                # Add movies to the list
                movie_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'release_date': movie.release_date,
                    'thumbnail': movie.thumbnail,
                    'href': movie.href
                })

            return render_template('review_page.html', movies=movie_data, current_movie=current_movie)
        else:
            return jsonify({'error': 'Movie not found!'}) 

    # Route allowing the user to submit and save their review to their account
    @app.route('/submit_review', methods=['POST'])
    @jwt_required()
    def submit_review_view():
        user = User.query.filter_by(username=current_user.username).first()

        if user:
            try:
                rating = request.form['rating']
                text = request.form['text']
                movie_id = request.form['movie_id']
                
                if not all([rating, text, movie_id]):
                    return jsonify(message="Missing Value(s)"), 400
                else:
                    user.add_movie_review(rating, text, movie_id)
                    return redirect(url_for('movie_reviews_page_view'))

            except KeyError as e:
                # Change this to return you back to the previous page and flash a message instead
                return jsonify(error=f"Missing required field: {e.args[0]}"), 400

    # Review Page showing the listing of reviews from the user
    @app.route('/reviews')
    @jwt_required()
    def movie_reviews_page_view():
        user = User.query.filter_by(username=current_user.username).first()

        if user:
            reviews = user.reviews

            # Variables for page numbers
            page = request.args.get('page', 1, type=int)
            per_page = 25

            total = len(reviews)

        return render_template('user_reviews_page.html', reviews=reviews, total=total, page_count=per_page, current_page=page)

    # Review Page showing the list of all reviews for a particular movie
    @app.route('/<href>/reviews')
    def all_reviews_view(href):
        return jsonify(message="All Movie Reviews Page")

    # Wishlist Page
    @app.route('/wishlist')
    @jwt_required()
    def wishlist_page_view():
        return jsonify(message="Watchlist Page")
    
    app.app_context().push()
    return app

