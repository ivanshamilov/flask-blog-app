from flask import Blueprint, render_template, request, redirect, send_file, url_for
from . import db
from .models import User, BlogPost
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64
from werkzeug.utils import secure_filename
import os



main = Blueprint('main', __name__)


@main.route('/')
def index():
    users = User.query.all()
    return render_template('about.html')


@main.route('/posts')
def posts():
    posts = BlogPost.query.order_by(BlogPost.date_modified.desc()).all()
    return render_template('index.html', posts=posts)


@main.route('/new_post', methods=['GET'])
@login_required
def new_post():
    return render_template('new_post.html')
 

@main.route('/new_post', methods=['POST'])
@login_required
def new_post_post(): # Lol
    edit = False
    title = request.form.get('title')
    content = request.form.get('content')
    f = request.files['image']
    image = f.filename
    filename = secure_filename(f.filename)
    f.save(os.path.join(os.getcwd(), 'project', 'static', 'uploads', filename))


    new_post = BlogPost(title=title, content=content, author=current_user.name, image=filename)

    db.session.add(new_post)
    db.session.commit()

    return redirect('/posts')


@main.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = BlogPost.query.get_or_404(id)


    if current_user.name != post.author:
        return redirect('/posts')

    db.session.delete(post)
    os.remove(os.path.join(os.getcwd(), 'project', 'static', 'uploads', post.image))
    db.session.commit()

    return redirect('/my_posts')


@main.route('/my_posts')
@login_required
def my_posts():
    posts = BlogPost.query.filter_by(author=current_user.name).order_by(BlogPost.date_modified.desc()).all() 
    return render_template('my_posts.html', posts=posts)


@main.route('/posts/edit/<int:id>', methods=['GET'])
@login_required
def edit_post(id):
    edit = True
    post = BlogPost.query.get(id)

    if current_user.name != post.author:
        return redirect('/posts')
    return render_template('new_post.html', title=post.title, content=post.content, id=post.id, edit=edit)


@main.route('/posts/edit/<int:id>', methods=['POST'])
@login_required
def edit_post_post(id): # Lol 2
    post = BlogPost.query.get(id)
    title = request.form.get('title')
    content = request.form.get('content')

    post.title = title
    post.content = content

    post.date_modified = datetime.utcnow()

    db.session.commit()

    return redirect('/my_posts')


@main.route('/posts/<int:id>', methods=['GET'])
def post(id):
    post = BlogPost.query.get(id)
    
    return render_template('post.html', post=post)


