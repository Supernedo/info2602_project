from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Movie_Review(db.Model):
    __tablename__ = 'movie_review'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    movie_id = db.Column(db.Integer(), db.ForeignKey('movie.id'), nullable=False)
    review_id = db.Column(db.Integer(), db.ForeignKey('review.id'), nullable=False)