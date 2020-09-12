from . import db
from flask_login import UserMixin
from datetime import datetime



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author')


tags = db.Table('tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False) # yep
    content = db.Column(db.Text, nullable=False) # yep
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # yep
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # yep
    image = db.Column(db.String(100), nullable=False) # yep 
    tags_list = db.relationship('Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


