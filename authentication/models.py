from datetime import datetime
from flask_login import UserMixin
from config import Config
import pyotp

class User(UserMixin):
    id=0
    email=""
    password=""
    created_date=""
    is_two_authentication_enabled=False
    secret_token=""
    authenticated_by=""
    is_information_validate=False,
    is_validate_email=False,
    role_user=None,
    is_active=True,
    idinformationuser=""
    is_admin=""
    
    def __init__(self,id, email, password,authenticated_by,created_date,secret_token
                 ,is_two_authentication_enabled,is_information_validate,is_validate_email,role_user,is_active,idinformationuser,is_admin):
        self.id=id
        self.email = email
        self.password = password
        self.authenticated_by=authenticated_by
        self.created_date = created_date
        self.secret_token = secret_token
        self.is_two_authentication_enabled=is_two_authentication_enabled
        self.is_information_validate=is_information_validate
        self.is_validate_email=is_validate_email
        self.role_user=role_user
        self.is_active=is_active
        self.idinformationuser=idinformationuser
        self.is_admin=is_admin

    def get_authentication_setup_uri(self):
        return pyotp.totp.TOTP(self.secret_token).provisioning_uri(
        name=str(self.email), issuer_name=Config.APP_NAME)
    
    def is_otp_valid(self, user_otp):
        #totp = pyotp.parse_uri(self.get_authentication_setup_uri())
        totp=pyotp.TOTP(self.secret_token)
        return totp.verify(user_otp)
        #return self.secret_token
    
    def __repr__(self):
        return f"<user {self.email}>"
    
class verifyPassword():
    email=""
    totp_temp=""
    def __init__(self,email,totp_temp):
        self.email=email
        self.totp_temp=totp_temp
