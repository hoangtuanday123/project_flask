from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField,StringField,BooleanField,URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired,URL,Regexp

class roleForm(FlaskForm):
    role = StringField('Enter role', validators=[
                      InputRequired()])

class SelectionForm(FlaskForm):
    selection = BooleanField('Selection')

class groupuserForm(FlaskForm):
    group = StringField('Enter group', validators=[
                      InputRequired()])
    alias = StringField('Enter alias', validators=[
                      InputRequired()])
    email = StringField('Enter email', validators=[
                      InputRequired()])
    url = StringField('Enter URL', validators=[InputRequired()])
    description = StringField('Enter description', validators=[
                      InputRequired()])

    