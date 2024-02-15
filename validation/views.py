from .forms import informationUserForm
from validation.models import informationUser
from flask import Blueprint, flash, redirect, render_template, request, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_login import current_user,login_user,login_required,logout_user
import db

from flask_mail import Message

from __init__ import app,mail ,file_path_default

validate = Blueprint("validation", __name__)

@validate.route("/infomationuser", methods=["GET", "POST"])
@login_required 
def informationuser():
    form = informationUserForm(request.form)
    
    if form.validate_on_submit():
        email=""
        if current_user.authenticated_by=="normal" or current_user.authenticated_by=="google":
            email=current_user.email
        else:
            email=form.Email.data
            current_user.email=email
        
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser where id_useraccount=?"
        value=(current_user.id)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp is None:

            conn=db.connection()
            cursor=conn.cursor()
            sql="""SET NOCOUNT ON;
                    insert into informationUser(Fullname,Nickname,Email,Contactaddress,id_useraccount) values(?,?,?,?,?)
                    DECLARE @id int;
                    SET @id = SCOPE_IDENTITY();    
                    insert into latestEmployment(idinformationuser) values (@id)"""
            value=(form.Fullname.data,form.Nickname.data,email,form.Contactaddress.data,current_user.id)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        token = generate_token(email)
        confirm_url = url_for("validation.confirm_email", token=token, _external=True)
        html = render_template("validation/confirm_email.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)
        flash("A confirmation email has been sent via email.", "success")
        return redirect(url_for("validation.inactive"))
    return render_template("validation/informationUserValidate.html",image_path=file_path_default, form=form)

@validate.route("/inactiveEmail")
@login_required
def inactive():
    if current_user.is_information_validate:
        return redirect(url_for("core.home"))
    return render_template("validation/inactiveEmail.html",image_path=file_path_default)
@login_required
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])

@login_required
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
        return email
    except Exception:
        return False
    
@validate.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_information_validate:
        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(id)
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=userinfor[0]
        flash("Account already confirmed.", "success")
        return redirect(url_for("core.home"))
    email = confirm_token(token)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?"
    value=(current_user.id)
    cursor.execute(sql,value)
    information=cursor.fetchone()
    conn.commit()
    conn.close()
    if information[3] == email:
        current_user.is_information_validate = True
        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set infor_validate=1 where id=?"
        value=(current_user.id)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(id)
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=userinfor[0]
        flash("You have confirmed your account. Thanks!", "success")
    else:
        # conn=db.connection()
        # cursor=conn.cursor()
        # sql="update informationUser where id_useraccount=?"
        # value=(current_user.id)
        # cursor.execute(sql,value)
        # conn.commit()
        # conn.close()
        flash("The confirmation link is invalid or has expired.", "danger")
        redirect(url_for("validation.informationuser"))
    if current_user.role_user == None:
        logout_user()
        flash("waiting for admin assign role")
        return redirect('/')
    return redirect(url_for("core.home"))

@validate.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_information_validate:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("core.home"))
    token = generate_token(current_user.email)
    confirm_url = url_for("validation.confirm_email", token=token, _external=True)
    html = render_template("validation/confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("validation.inactive"))

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )
    mail.send(msg)

