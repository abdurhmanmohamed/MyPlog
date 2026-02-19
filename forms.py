from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField,PasswordField
from flask_wtf.file import FileField , FileAllowed

from wtforms.validators import DataRequired, URL,Email
from email_validator import validate_email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
# WTForm for creating a blog post
class RegisterForm(FlaskForm):
    img = FileField('Image', validators=[
            DataRequired(),
            FileAllowed(["jpg", "png", "jpeg"], "Images only!")
        ])
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email(check_deliverability=True)])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: Create a LoginForm to login existing users
# WTForm for creating a blog post
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(check_deliverability=True)])

    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# TODO: Create a CommentForm so users can leave comments below posts
# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# TODO :Comment form
class CommentForm(FlaskForm):
    comment = StringField(label='Comment', validators=[DataRequired()])
    submit = SubmitField("Comment")
