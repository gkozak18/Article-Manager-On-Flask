from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500))
    text = db.Column(db.String(16000), nullable=False)
    date = db.Column(db.Date, default=datetime.now)
    author = db.Column(db.String(250), nullable=False)
    last_update = db.Column(db.Date)
    likes = db.Column(db.Integer)
    views = db.Column(db.Integer)
    image = db.Column(db.String(500))

    def __repr__(self):
        return f"{self.title} was created on {self.date}"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    article = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    date_in_seconds = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.text}"


class User(db.Model):
    __table_name__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(500))
    phone_number = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id
