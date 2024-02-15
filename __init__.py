from decouple import config
#from config.config import Config
from flask_session import Session
from flask_wtf import CSRFProtect 
from flask import Flask, redirect, request, url_for,render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import os
import requests
#import authentication.forms
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv,dotenv_values
import db

import facebook

from flask_mail import Mail


#def init_app():
app=Flask(__name__)
load_dotenv()
app.config.from_object(config("APP_SETTINGS"))
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
login_manager = LoginManager(app)
login_manager.init_app(app)
Session(app)
CSRFProtect(app) 
mail = Mail(app)

# default avatar image 
file_path_default = "MacBook.jpg"
#login by google authentication
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='151479368135-2nb4q149jlto3e2nraglmnl70c9kg0is.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
    
)
@app.route('/')
def index():
    #return '<a class="button" href="/register">register</a> <a class="button" href="/signin">sign in</a>'
    return redirect('/startPage')
    
@app.route('/signingoogle')
def logingoogle():
    google=oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google=oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()
    user_id = user_info.get('id')
    email_address = user_info.get('email')
    #session['profile'] = user_info
    #session.permanent = True
    # do something with the token and profile
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from user_account where id_other_app=?"
    value=(user_id)
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp is not None:
        
        user=User(id=int(user_temp[0]),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                    authenticated_by=user_temp[5],secret_token=user_temp[6],is_two_authentication_enabled=user_temp[7]
                    ,is_information_validate=user_temp[8],is_validate_email=user_temp[9],role_user=user_temp[10],
                    is_active=user_temp[11],idinformationuser=None,is_admin=None)

    else:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
                SET NOCOUNT ON;
                insert into user_account values(?,?,null,getdate(),'google',null,1,0,0,6,1)
                DECLARE @NewRowID INT;
                SET @NewRowID = SCOPE_IDENTITY();
                SELECT * from user_account where id=@NewRowID;
                """
        value=(user_id,email_address)
        cursor.execute(sql,value)
        id_user = cursor.fetchone()
        conn.commit()
        conn.close()
        user = User(id=id_user[0],email=id_user[2], password=id_user[3],created_date=id_user[4],
                    authenticated_by="google",secret_token=id_user[6],
                    is_two_authentication_enabled=id_user[7],is_information_validate=id_user[8],
                    is_validate_email=id_user[9],role_user=id_user[10],is_active=id_user[11],idinformationuser=None,is_admin=None)
    login_user(user)
    if not user.is_information_validate:
        return redirect(url_for("validation.informationuser"))
    return redirect('/home')

#login by facebook


# Facebook app credentials
app_id = '606096974979227'
app_secret = 'a797741083244d5cb216af35ee21c881'
authorization_base_url = 'https://www.facebook.com/v18.0/dialog/oauth'
token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
redirect_uri = 'http://localhost:5000/callback'  # Update with your own redirect URI

# Initialize Facebook Graph API with app credentials
graph = facebook.GraphAPI(access_token=None, version='3.0')
@app.route('/signinfacebook')
def loginfacebook():
    auth_url =graph.get_auth_url(app_id, redirect_uri)

    return redirect(auth_url)

@app.route('/callback')
def callback():
    global access_token
    
    graph = facebook.GraphAPI(access_token=None, version='3.0')

    code = request.args.get('code')
    access_token = graph.get_access_token_from_code(code, redirect_uri, app_id, app_secret)
    # Retrieve user's name and ID
    graph = facebook.GraphAPI(access_token['access_token'])
    me = graph.get_object('me',)
    user_id = me['id']
    name = me['name']
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from user_account where id_other_app=?"
    value=(user_id)
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp is not None:
        user=User(id=int(user_temp[0]),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                    authenticated_by=user_temp[5],secret_token=user_temp[6],is_two_authentication_enabled=user_temp[7],
                    is_information_validate=user_temp[8],is_validate_email=user_temp[9],role_user=user_temp[10],
                    is_active=user_temp[11],idinformationuser=None,is_admin=None)

    else:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
                SET NOCOUNT ON;
                insert into user_account values(?,?,null,getdate(),'facebook',null,1,0,0,6,1)
                DECLARE @NewRowID INT;
                SET @NewRowID = SCOPE_IDENTITY();
                SELECT * from user_account where id=@NewRowID;
                """
        value=(user_id,name)
        cursor.execute(sql,value)
        id_user = cursor.fetchone()
        conn.commit()
        conn.close()
        user = User(id=id_user[0],email=id_user[2], password=id_user[3],created_date=id_user[4],
                    authenticated_by="google",secret_token=id_user[6],is_two_authentication_enabled=id_user[7],
                    is_information_validate=id_user[8],is_validate_email=id_user[9],role_user=id_user[10],
                    is_active=id_user[11],idinformationuser=None,is_admin=None)
    login_user(user)
    if not user.is_information_validate:
        return redirect(url_for("validation.informationuser"))
    return  redirect('/home')

login_manager.login_view = "authentication.login"
login_manager.login_message_category = "danger"

from authentication.models import User
@login_manager.user_loader
def load_user(id):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from user_account where id=?"
    value=(id)
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    
    if user_temp is not None:
        user=User(id=int(user_temp[0]),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                    authenticated_by=user_temp[5],secret_token=user_temp[6],is_two_authentication_enabled=user_temp[7],
                    is_information_validate=user_temp[8],is_validate_email=user_temp[9],role_user=user_temp[10],
                    is_active=user_temp[11],idinformationuser=None,is_admin=None)
        if user.is_information_validate==True:
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
            value=(id)
            cursor.execute(sql,value)
            userinfor=cursor.fetchone()
            conn.commit()
            conn.close()
            user.idinformationuser=userinfor[0]
        
    else:
        user = User(
            id=0,
            email="",
            password="",
            created_date="",
            authenticated_by="",
            secret_token="",
            is_two_authentication_enabled=False,
            is_information_validate=False,
            is_validate_email=False,
            role_user=None,
            is_active=True,
            idinformationuser=None,
            is_admin=None
        )
    
    return user

with app.app_context():
    from authentication.views import auth
    app.register_blueprint(auth)
    from core.views import core_bp
    app.register_blueprint(core_bp)
    from validation.views import validate
    app.register_blueprint(validate)
    from admin.views import admin
    app.register_blueprint(admin)
    from client_manager.views import clientmanager
    app.register_blueprint(clientmanager)
    from employee.views import employee
    app.register_blueprint(employee)
    from employee_manager.views import employeemanager
    app.register_blueprint(employeemanager)
    from account_manager.views import accountmanager
    app.register_blueprint(accountmanager)

    from candidate.views import candidate
    app.register_blueprint(candidate)
