from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

app.secret_key = 'unique secret key'

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


with open('config.json') as c:
    params = json.load(c)['params']


@app.route('/')
def index():
    posts = Posts.query.all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<string:post_slug>')
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', post=post)


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
    if 'user' in session and session['user'] == params['admin_user']:

        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            slug = request.form.get('slug')
            image =request.form.get('image')

            entry = Posts(title=title, tagline=tagline, content=content, slug=slug, image=image, date=datetime.now().strftime("%d %B %Y %I:%M %p"))
            db.session.add(entry)
            db.session.commit()
        
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


if __name__ == '__main__':
    app.run(debug=True)