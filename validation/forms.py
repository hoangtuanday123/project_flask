from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField,StringField,IntegerField,DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired, Regexp

from validation.models import informationUser


class informationUserForm(FlaskForm):
    Fullname = StringField("Fullname", validators=[InputRequired(message='Fullname is required')])
    Nickname = StringField("Nickname")
    Email = EmailField("Email", validators=[DataRequired(), Email()])
    Contactaddress = StringField("Contactaddress")
    IdUserAccount = IntegerField("IdUserAccount")
    Phone = StringField("Phone")
    LinkedIn = StringField("LinkedIn")
    Years = IntegerField("Years")
    Location = StringField("Location")
    Maritalstatus = StringField("Maritalstatus")
    Ethnicgroup = StringField("Ethnicgroup")
    Religion = StringField("Religion")

class latestEmploymentForm(FlaskForm):
    Employer = StringField("Employer", validators=[InputRequired(message='Employer name is required')])
    Jobtittle = StringField("Jobtittle")
    AnnualSalary = IntegerField("AnnualSalary")
    AnnualBonus = IntegerField("AnnualBonus")
    RetentionBonus = IntegerField("RetentionBonus")
    RetentionBonusExpiredDate = DateTimeField("RetentionBonusExpiredDate")
    StockOption = IntegerField("StockOption")
    StartDate = DateTimeField("StartDate")
    EndDate = DateTimeField("EndDate")
    IdInformationUser = IntegerField("IdInformationUser")

class usercccdForm(FlaskForm):
    No = IntegerField("No", validators=[InputRequired(message='Citizen Identification No is required')])
    FullName = StringField("Full Name", validators=[InputRequired(message='Full Name is required')])
    DateOfbirth = DateTimeField("Date Of Birth")
    PlaceOfBirth = StringField("Place Of Birth")
    Address = StringField("Address")
    IssueOn = DateTimeField("Issue On")
    IdInformationUser = IntegerField("IdInformationUser")




