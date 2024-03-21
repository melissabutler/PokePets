from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FileField, SubmitField
from flask_wtf.file import  FileRequired, FileAllowed 
from wtforms.validators import DataRequired, Length


class UserAddForm(FlaskForm):
    """Form for adding User."""
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editting a user."""
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class PetForm(FlaskForm):
    """Pet form"""
    nickname = StringField('Nickname', validators=[DataRequired(), Length(max=30)])

class ReleasePet(FlaskForm):
    """ Release pet confirmation button"""
    release = SubmitField('Release Pet', validators=[DataRequired()])

class ForageForm(FlaskForm):
    """Pick a pet to go foraging with"""
    forage = SubmitField('Go foraging!', validators=[DataRequired()])

class DeleteUser(FlaskForm):
    """Delete account confirmation"""
    delete = SubmitField('Delete account', validators=[DataRequired()])