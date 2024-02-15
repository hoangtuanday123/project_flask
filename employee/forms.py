from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired


class Employeeinformation(FlaskForm):
    Bankaccount = StringField('Enter bankaccount' )
    bankname = StringField('Enter bankname' )
    Taxcode = StringField('Enter Taxcode')
    Socialinsurancecode = StringField('Enter Socialinsurancecode')
    Healthinsurancecardcode=StringField('Enter Healthinsurancecardcode')
    Registeredhospitalname=StringField('Enter Registeredhospitalname')
    Registeredhospitalcode=StringField('Enter Registeredhospitalcode')