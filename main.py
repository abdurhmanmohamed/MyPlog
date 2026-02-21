from datetime import date
import os
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, login_required,logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# Import your forms from the forms.py
from forms import CreatePostForm,RegisterForm, LoginForm, CommentForm
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager  = LoginManager()
login_manager.init_app(app)
 
login_manager.login_view = 'login'
# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# TODO :making decorator to autharize the admin user
def is_admin(func):
    @wraps(func)
    def wropped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id > 2 :
            abort(code = 403)
        else:
            return func(*args , **kwargs)
    return wropped

# CONFIGURE TABLES

# TODO: Create a User table for all your registered users. 
class User(db.Model, UserMixin):
    # parent
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    img:Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    posts = relationship('BlogPost', back_populates='writer')



class BlogPost(db.Model):
    # child
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    writer = relationship('User', back_populates='posts')
    writer_id:Mapped[int] = mapped_column(ForeignKey('users.id'))
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    comments = relationship('Comment', back_populates='post')

class Comment(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name:Mapped[str] = mapped_column(String(250), nullable=False)
    body:Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    post = relationship('BlogPost', back_populates='comments')
    post_id:Mapped[int] = mapped_column(ForeignKey('blog_posts.id'))




with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method =='POST':
        email = form.email.data
        user = db.session.query(User).filter(User.email == email).first()
        if user:
            flash('We Found A User With This Email, Please Login.')
            return redirect(url_for('login'))
        else:
            password = generate_password_hash(form.password.data, 'pbkdf2:sha256', 8)
            name = form.name.data
            img = form.img.data
            filename = secure_filename(img.filename)
            img.save(os.path.join("static", "uploads", filename))
            new_user = User(email = email, name = name, password = password, img="uploads/" + filename)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
    else:

        return render_template("register.html",form = form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods = ['POST', 'GET'])

def login():
    form = LoginForm()
    if request.method == 'POST':
        email = form.email.data
        user = db.session.query(User).filter(User.email == email).first()
        if not user :
            flash('Sorry, User Not Found')
            return redirect(url_for('login'))
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('get_all_posts'))
            
        else:
            flash('Sorry, The Entered Password Is Wrong')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', form = form)
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods = ['POST', 'GET'])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if request.method =='POST' and form.validate_on_submit() and current_user.is_authenticated:
        new_comment = Comment(user_name=current_user.name, body = form.comment.data, post = requested_post, img_url = current_user.img)
        db.session.add(new_comment)
        db.session.commit()
        return redirect (url_for('show_post', post_id = post_id))
    return render_template("post.html", post=requested_post, form = form, comments = requested_post.comments)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@is_admin
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            writer = current_user
        )
        db.session.add(new_post)
        db.session.commit()
        print(current_user.posts)
        print(new_post.writer)
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@is_admin
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post

@app.route("/delete/<int:post_id>")
@is_admin
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    coments_to_delete = post_to_delete.comments
    for c in coments_to_delete:
        db.session.delete(c)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/author/<int:id>')
def show_work(id):
    writer = db.get_or_404(User, id)
    return render_template('writer_work.html' , posts = writer.posts)
if __name__ == "__main__":
    app.run(debug=False)
