from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import math

with open('config.json') as c:
    params = json.load(c)['params']

app = Flask(__name__)

app.secret_key = 'unique secret key'

app.config['UPLOAD_FOLDER'] = params['upload_location']

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/blog'

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    message = db.Column(db.String(), nullable=False)
    # date = db.Column(db.String(), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    tagline = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(), nullable=False)
    slug = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)


@app.route('/')
def index():

    posts = Posts.query.all()
    last = math.ceil(len(posts)/int(params['num_posts']))
    # [:params['num_posts']]
    
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    
    posts = posts[(page-1)*int(params['num_posts']):(page-1)*int(params['num_posts'])+int(params['num_posts'])]
    
    if page == 1:
        prev = '#'
        next = "/?page="+str(page+1)

    elif page == last:
        prev = "/?page="+str(page-1)
        next = "#"

    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)



    return render_template('index.html', posts=posts, prev=prev, next=next)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<string:post_slug>')
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', post=post)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file']
            f.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return 'Uploaded successfully'

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, email=email, phone=phone, message=message)
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == params['admin_user'] and password == params['admin_pass']:
            session['user'] = params['admin_user']
            # return render_template('dashboard.html')

    if 'user' in session and session['user'] == params['admin_user']:
        
        posts = Posts.query.all()

        return render_template('dashboard.html', posts=posts)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == params['admin_user'] and password == params['admin_pass']:
            session['user'] = params['admin_user']
            return redirect("/dashboard")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')


@app.route('/delete/<string:sno>')
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()

        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            slug = request.form.get('slug')
            f = request.files['image']
            image = f.filename
            if image:
                while True:

                    if image not in os.listdir('static/img/post'):
                        break
                    splitted = image.split('.')
                    image = splitted[0]+'0'+'.'+splitted[1]
                f.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], secure_filename(image)))
            
            if sno == '0':
                entry = Posts(title=title, tagline=tagline, content=content, slug=slug, image=image, date=datetime.now().strftime("%d %B %Y %I:%M %p"))
                db.session.add(entry)
            else:
                post.title = title
                post.tagline = tagline
                post.content = request.form.get('content')
                post.slug = slug
                post.image = image

            db.session.commit()
        
        return render_template('edit.html', post=post)


    else:
        return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)