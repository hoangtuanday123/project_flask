from .forms import ForgotPasswordForm, RegisterForm,TwoFactorForm,LoginForm,ChangePasswordForm
from authentication.models import User,verifyPassword
import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session
import qrcode
from PIL import Image
from io import BytesIO
import base64
import pyotp
from datetime import datetime
from flask_mail import Message
from validation.views import send_email

from __init__ import app,mail,file_path_default
auth = Blueprint("authentication", __name__)

HOME_URL = "core.home"
SETUP_2FA_URL = "authentication.setup_two_factor_auth"
VERIFY_2FA_URL = "authentication.verify_two_factor_auth"


@auth.route("/register", methods=["GET", "POST"])
def register():
    
    if current_user.is_authenticated:
        if current_user.is_two_authentication_enabled:
            flash("You are already registered.", "info")
            return redirect(url_for(HOME_URL))
        else:
            flash("You have not enabled 2-Factor Authentication. Please enable first to login.", "info")
            return redirect(url_for(SETUP_2FA_URL))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        secret=pyotp.random_base32()
        created_date=datetime.now()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            SET NOCOUNT ON;
            DECLARE @out int;
            EXEC register_user @email=?,@password=?,@created_date=?,@authenticated_by=?,@secret_token=?,@id = @out OUTPUT;
            SELECT @out AS the_output;
            """
        value=(form.email.data,form.password.data,created_date,'normal',secret)
        cursor.execute(sql,value)
        id_user = cursor.fetchone()
        conn.commit()
        conn.close()
        if(id_user[0]!=0):
            
            user = User(id=id_user[0],email=form.email.data, password=form.password.data,
                        created_date=created_date,authenticated_by="normal",
                        secret_token=secret,is_two_authentication_enabled=False,is_information_validate=False,
                        is_validate_email=False,role_user=None,is_active=True,idinformationuser=None,is_admin=None)
            login_user(user)
            flash("You are registered. You have to enable 2-Factor Authentication first to login.", "success")
            
            return redirect(url_for(SETUP_2FA_URL))
        else:
            flash("email is exist", "fail")
        

    return render_template("authentication/register.html", form=form)

# <!-- <p class="text-center mt-3">Already registered? <a href="{{ url_for('accounts.login') }}">Login now</a></p> -->

from utils import get_b64encoded_qr_image

@auth.route("/setup-2fa")
@login_required
def setup_two_factor_auth():
    secret = current_user.secret_token
    uri = current_user.get_authentication_setup_uri()
    base64_qr_image = get_b64encoded_qr_image(uri)
    return render_template("authentication/setup-2fa.html",image_path=file_path_default, secret=secret, qr_image=base64_qr_image)


@auth.route("/verify-2fa", methods=["GET", "POST"])
@login_required
def verify_two_factor_auth():
    form = TwoFactorForm(request.form)
    if form.validate_on_submit():
        #return current_user.is_otp_valid(form.otp.data)
        if current_user.is_otp_valid(form.otp.data):
            if current_user.is_two_authentication_enabled:
                flash("2FA verification successful. You are logged in!", "success")
                if not current_user.is_information_validate:
                    return redirect(url_for("validation.informationuser"))
                if current_user.role_user == None:
                    flash("waiting for admin assign role")
                    logout_user()
                    return redirect('/')
                return redirect(url_for(HOME_URL))
            else:
                current_user.is_two_authentication_enabled = True
                conn=db.connection()
                cursor=conn.cursor()
                sql="update user_account set enabled_authentication=1 where id=?"
                value=(current_user.id)
                cursor.execute(sql,value)
                conn.commit()
                conn.close()
                #db.session.commit()
                flash("2FA setup successful", "success")
                if not current_user.is_information_validate:
                    return redirect(url_for("validation.informationuser"))
                if current_user.role_user == None:
                    flash("waiting for admin assign role")
                    logout_user()
                    return redirect('/')
                return redirect(url_for(HOME_URL))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for(VERIFY_2FA_URL))
    else:
        if not current_user.is_two_authentication_enabled:
            flash(
                "You have not enabled 2-Factor Authentication. Please enable it first.", "info")
        return render_template("authentication/verify-2fa.html", form=form,image_path=file_path_default)
    

@auth.route("/signin", methods=["GET", "POST"])
def login():
    session['is_admin']="None"
    if current_user.is_authenticated:
        if current_user.is_two_authentication_enabled:
            flash("You are already logged in.", "info")
            if not current_user.is_information_validate:
                return redirect(url_for("validation.informationuser"))
            if current_user.role_user == None :
                flash("waiting for admin assign role")
                logout_user()
                return redirect('/')
            return redirect(url_for(HOME_URL))
        else:
            flash("You have not enabled 2-Factor Authentication. Please enable first to login.", "info")
            return redirect(url_for(SETUP_2FA_URL))
        
    form = LoginForm(request.form)
    if form.validate_on_submit():
        #user = User.query.filter_by(username=form.username.data).first()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            SET NOCOUNT ON;
            DECLARE @out int;
            EXEC login_user @email=?,@password=?,@id = @out OUTPUT;
            SELECT @out AS the_output;
            """
        value=(form.email.data,form.password.data)
        cursor.execute(sql,value)
        id_user = cursor.fetchone()
        conn.commit()
        conn.close()
        if id_user[0]!=0:
            

            conn=db.connection()
            cursor=conn.cursor()
            sql="select * from user_account where id=?"
            value=(id_user[0])
            cursor.execute(sql,value)
            user_temp=cursor.fetchone()
            conn.commit()
            conn.close()
            user=User(id=int(user_temp[0]),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                      authenticated_by=user_temp[5],secret_token=user_temp[6],
                      is_two_authentication_enabled=user_temp[7],is_information_validate=user_temp[8],
                      is_validate_email=user_temp[9],role_user=user_temp[10],is_active=user_temp[11],idinformationuser=None,is_admin=None)
            if user.role_user is None :
                flash("waiting for admin assign role")
                
                return redirect('/')
            if not user.is_active:
                flash("account is not active")
                
                return redirect('/')
            login_user(user)
            if not current_user.is_two_authentication_enabled:
                flash(
                    "You have not enabled 2-Factor Authentication. Please enable first to login.", "info")
                return redirect(url_for(SETUP_2FA_URL))
            return redirect(url_for(VERIFY_2FA_URL))
        # elif not user:
        #     flash("You are not registered. Please register.", "danger")
        else:
            flash("Invalid username and/or password.", "danger")
    return render_template("authentication/login.html", form=form)


@auth.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    form = ForgotPasswordForm(request.form)
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser i join user_account u on i.id_useraccount=u.id where i.Email=?"
        value=(form.email.data)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp is not None:
            if(user_temp[11]=='normal'):
                secret=pyotp.random_base32()
                totp=pyotp.TOTP(secret)
                verify=verifyPassword(email=form.email.data,totp_temp=totp.now())
                session['verify_password']=verify
                flash("A confirmation email has been sent via email.", "success")
                return redirect(url_for("authentication.verifypassword"))
            else:
                flash("account have not set password")
                return redirect(url_for("authentication.login"))

        else:
            flash("You have not confirmed your account or have not register, please sign in or register and confirm your account ")
            return redirect(url_for("core.startPage"))

    return render_template("authentication/forgotpassword.html",form=form)

@auth.route("/verifypassword",methods=["GET", "POST"])
def verifypassword():
    verify_password=session.get('verify_password')
    subject = "this is otp :"
    html=verify_password.totp_temp
    send_email(verify_password.email, subject, html)
    form = TwoFactorForm(request.form)
    if form.validate_on_submit():
        if verify_password.totp_temp==form.otp.data:
            if current_user.is_authenticated:
                session['id_useraccount']=current_user.id
            else:
                conn=db.connection()
                cursor=conn.cursor()
                sql="select * from informationUser where Email=?"
                value=(verify_password.email)
                cursor.execute(sql,value)
                user_temp=cursor.fetchone()
                conn.commit()
                conn.close()
                session['id_useraccount']=user_temp[5]
                
            return redirect(url_for("authentication.changepassword"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for("authentication.verifypassword"))


    return render_template("authentication/verify-2fa.html", form=form)

@auth.route("/changepassword",methods=["GET", "POST"])
def changepassword():
    id_user=session.get('id_useraccount')
    form=ChangePasswordForm(request.form)
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set password=? where id=?"
        value=(form.password.data,id_user)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        flash("change password is success")
        if current_user.is_authenticated:
            return redirect(url_for("core.home"))
        return redirect(url_for("authentication.login"))
    return render_template("authentication/changepassword.html",form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("authentication.login"))