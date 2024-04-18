from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Movie(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    #cast = db.Column(db.String(1000))
    genres = db.Column(db.String(1000))
    description = db.Column(db.String(1000), nullable=False)
    thumbnail = db.Column(db.String(120))  # Poster image
    backdrop = db.Column(db.String(120))  # Background image
    href = db.Column(db.String(255))  # Formatted title for use in the HTML

    has_video = db.Column(db.Boolean(), default=False)
    video_URL = db.Column(db.String(255))
    video_name = db.Column(db.String(255))

    # Relationships
    reviews = db.relationship('Review', secondary='movie_review', backref=db.backref('movies'), lazy=True)

    # Separate the list of casts and genres into its own arrays
    @property
    def cast_arr(self):
        return self._cast.split(',') if self.cast else []

    @cast_arr.setter
    def cast_arr(self, value):
        self._cast = ','.join(value)

    @property
    def genres_arr(self):
        return self._genres.split(',') if self.genres else []

    @genres_arr.setter
    def genres_arr(self, value):
        self._genres = ','.join(value)

    def __init__(self, id, title, release_date, language, description, thumbnail, backdrop, hasVideo):
        self.id = id
        self.title = title
        self.release_date = release_date
        #self.cast_arr = cast_arr
        self.language = language
        #self.genres_arr = genres_arr
        self.description = description
        self.thumbnail = thumbnail
        self.backdrop = backdrop
        self.hasVideo = hasVideo
