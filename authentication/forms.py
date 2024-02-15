from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField,StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired

from authentication.models import User


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )



    # def validate(self, extra_validators):
    #     initial_validation = super(RegisterForm, self).validate(extra_validators)
    #     if not initial_validation:
    #         return False
    #     user = User.query.filter_by(username=self.username.data).first()
    #     if user:
    #         self.username.errors.append("Username already registered")
    #         return False
    #     if self.password.data != self.confirm.data:
    #         self.password.errors.append("Passwords must match")
    #         return False
    #     return True

class TwoFactorForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[
                      InputRequired(), Length(min=6, max=6)])
    
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class ForgotPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
