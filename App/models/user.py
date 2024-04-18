from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

#Temp Imports
from .movie import *
from .review import *

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    # Relationships
    reviews = db.relationship('Review', backref='user', lazy=True)

    def add_movie_review(self, rating, text, movie_id):
        # Check if movie exists
        movie = Movie.query.get(movie_id)

        if movie:
            # Check if a review was already added for the given movie
            # By having the review id the same as the movie id, we can ensure that the movie is only referenced once per user

            for review in self.reviews:
                if review.id == movie_id:
                    return None  # As a review exists with the same ID as the movie

            new_review = Review(id=movie_id, rating=rating, text=text)
            self.reviews.append(new_review)

            db.session.add(new_review)
            db.session.commit()
        else:
            print({"error": 'Movie not found.'})


    # **********************

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

