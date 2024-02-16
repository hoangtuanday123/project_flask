from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField,StringField,BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired

class roleForm(FlaskForm):
    role = StringField('Enter role', validators=[
                      InputRequired()])

class SelectionForm(FlaskForm):
    selection = BooleanField('Selection')

class groupuserForm(FlaskForm):
    group = StringField('Enter group', validators=[
                      InputRequired()])