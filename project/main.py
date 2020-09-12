from flask import Blueprint, render_template, request, redirect, send_file, url_for
from . import db
from .models import User, Post, Tag, tags
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
@main.route('/posts/<int:page>')
def posts(page=1):
    per_page = 2
    posts = Post.query.order_by(Post.date_modified.desc()).paginate(page,per_page,error_out=False)
    return render_template('index.html', posts=posts)


@main.route('/new_post', methods=['GET'])
@login_required
def new_post():
    return render_template('new_post.html')
 

@main.route('/new_post', methods=['POST'])
@login_required
def new_post_post(): # Lol

    title = request.form.get('title')
    content = request.form.get('content')
    tags = request.form.get('tags').split(',')
    f = request.files['image']
    image = f.filename
    filename = secure_filename(f.filename)
    f.save(os.path.join(os.getcwd(), 'project', 'static', 'uploads', filename))


    new_post = Post(title=title, content=content, author=current_user, image=filename)
    
    for tag in tags:
        if tag not in [tag.name for tag in Tag.query.all()]:
            new_tag = Tag(name=tag)
            db.session.add(new_tag)

    for tag in tags:
        temp_tag = Tag.query.filter_by(name=tag).first()
        # new_post.tags_list.append(temp_tag)
        temp_tag.posts.append(new_post)
        

    db.session.add(new_post)
    db.session.commit()

    return redirect('/posts')


@main.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        return redirect('/posts')
    for tag in post.tags_list:
        temp = Tag.query.get(tag.id)
        temp.posts.remove(post)

    db.session.delete(post)
    os.remove(os.path.join(os.getcwd(), 'project', 'static', 'uploads', post.image))
    db.session.commit()

    return redirect('/posts')


@main.route('/my_posts/<int:page>')
@login_required
def my_posts(page=1):
    per_page = 2
    posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.date_modified.desc()).paginate(page,per_page,error_out=False)
    return render_template('my_posts.html', posts=posts)


@main.route('/posts/edit/<int:id>', methods=['GET'])
@login_required
def edit_post(id):
    edit = True
    post = Post.query.get(id)

    if current_user != post.author:
        return redirect('/posts')
    
    tags = ','.join([tag.name for tag in post.tags_list])
    return render_template('new_post.html', post=post, tags=tags, edit=edit)


@main.route('/posts/edit/<int:id>', methods=['POST'])
@login_required
def edit_post_post(id): # Lol 2
    post = Post.query.get(id)
    title = request.form.get('title')
    content = request.form.get('content')
    tags = request.form.get('tags').split(',')

    for tag in tags:
        if tag not in Tag.query.all():
            new_tag = Tag(name=tag)
            db.session.add(new_tag)
        
    post.tags_list = []

    for tag in tags:
        temp_tag = Tag.query.filter_by(name=tag).first()
        temp_tag.posts.append(post)

    post.title = title
    post.content = content

    post.date_modified = datetime.utcnow()

    db.session.commit()

    return redirect('/posts')


@main.route('/post/<int:id>', methods=['GET'])
def post(id):
    post = Post.query.get(id)
    
    return render_template('post.html', post=post)


@main.route('/posts/search/<int:page>', methods=['POST'])
def posts_found(page=1):
    per_page = 2
    search = True
    tags = request.form.get('tags').split(',')
    if len(tags) == 1:
        posts = Tag.query.filter_by(name=tags[0]).first().posts.paginate(page,per_page,error_out=False)
        return render_template('index.html', posts=posts)
    else:
        posts = []
        for tag in tags:
            tag_posts = Tag.query.filter_by(name=tag).first().posts.paginate(page,per_page,error_out=False)
            for post in tag_posts:
                posts.append(post)
    return render_template('index.html', posts=list(set(posts)))

    # return render_template('index.html', posts=posts)