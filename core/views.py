from flask import Blueprint, render_template,redirect,url_for,session,flash
from flask_login import login_required, current_user
from authentication.models import verifyPassword
import db
import pyotp
import pyodbc
import re
import pandas as pd
import img2pdf
from PIL import Image
from validation.forms import informationUserForm, latestEmploymentForm, usercccdForm
from .models import allowed_file,user_avatar, user_cccd, user_healthyInsurance, allowed_attachment_file
from .forms import  uploadFile,DriveAPI
from flask import Blueprint, flash, redirect, render_template, request, url_for
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
import os
import io
from config import Config
import db
from __init__ import app,file_path_default
import pytesseract
from PIL import Image
from admin.forms import groupuserForm




core_bp = Blueprint("core", __name__)

# global variables
_front_cccd= ''
_back_cccd= ''
_image_path = ""#avatar default
_front_healthyInsurance = ""
_back_healthyInsurance =""
_driver_file_url = ""
_attachedFileName = ""
_fullname =""
_roleuser = ""
_roleadmin = ""
_image_path_admin = ""
_fullname_admin = ""
@login_required
def authorizationUser():
    global _image_path,_fullname,_roleuser,_image_path_admin 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(current_user.role_user)
    cursor.execute(sql,value)
    user_role=cursor.fetchone()
    session['roleuser']=user_role[0]

    cursor1=conn.cursor()
    sql1="select * from informationUser where id_useraccount=?"
    value1=(current_user.id)
    cursor1.execute(sql1,value1)
    user_temp=cursor1.fetchone()
    _roleuser=user_role[0]
    
    # set image path
    found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
    if found_avatar and found_avatar[2] != "":
        _image_path = found_avatar[2]
    else:
        _image_path = file_path_default
    #session['_image_path']=_image_path
    _fullname = user_temp[1]
    #session['_fullname']=_fullname
    # conn=db.connection()
    # cursor=conn.cursor()
    # sql="""
    #     select g.id, r.rolename from rolegroupuser r join groupuserdetail gd on r.id=gd.idrolegroupuser join
    #     groubuser g on g.id=gd.idgroupuser where gd.iduser=?"""
    # value=(user_temp[0])
    # cursor.execute(sql,value)
    # rolegrouptemp=cursor.fetchall()
    # conn.commit()
    # conn.close()
    # rolegroup=[]
    # if rolegrouptemp is not None:
    #     rolegroup=[(role[0],role[1]) for role in rolegroup]
    # session['rolegroup']=rolegroup
    # if session.get('roleuser')=='admin':
    #     session['rolegroup']='admin'
    session['rolegroup']=""
    
    session['readrights']=None
    session['writerights']=None

    if user_role[0]=="candidate":
        return redirect(url_for("candidate.candidatepage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="employee":
        return redirect(url_for("employee.employeepage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="employee_manager":
        return redirect(url_for("employeemanager.employeemanagerpage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="client_manager":
        return redirect(url_for("clientmanager.clientmanagerpage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="account_manager":
        return redirect(url_for("accountmanager.accountmanagerpage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="admin":
        
        # _image_path = "url_for('static',filename='source/avatar_admin.jpg')"
        _roleadmin = "admin"
        _roleuser = ""
        _image_path_admin = _image_path
        #session['_image_path_admin']=_image_path_admin
        _fullname_admin = _fullname
        #session['_fullname_admin']=_fullname_admin
        # _fullname = ""
        #duoc write neu value=1 

        session['writerights']=1

        return redirect(url_for("admin.adminpage",image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,roleadmin = _roleadmin))
        
    else:
        return "You have not been granted access to the resource"

@core_bp.route("/startPage")
def startPage():
    return render_template("core/startPage.html")


@core_bp.route("/home")
@login_required
def home(): 
    return authorizationUser()
    #return render_template("core/home.html")
    #return "hello"

@core_bp.route("/getcodechangepassword")
@login_required
def getcodechangepassword():
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
        value=(current_user.id)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if(user_temp[18]=='normal'):
            secret=pyotp.random_base32()
            totp=pyotp.TOTP(secret)
            verify=verifyPassword(email=user_temp[15],totp_temp=totp.now())
            session['verify_password']=verify
            flash("A confirmation email has been sent via email.", "success")
            return redirect(url_for("authentication.verifypassword"))
        else:
            flash("account have not set password")
            return redirect(url_for("core.startPage"))
        

# user profile page
@core_bp.route('/userinformation/<idaccount>/<totp>', methods=['post', 'get'])
@login_required
def userinformation(idaccount,totp):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    
    if idaccount==str(current_user.id) and totp=='None':
        
        session['readrights']=None
        
        form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser where id_useraccount=?"
        value=(idaccount)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.Fullname.data=user_temp[1]
            form.Nickname.data=user_temp[2]
            form.Email.data=user_temp[3]
            form.Contactaddress.data=user_temp[4]
            form.Phone.data=user_temp[6]
            form.LinkedIn.data=user_temp[7]
            form.Years.data=user_temp[8]
            form.Location.data = user_temp[9]
            form.Maritalstatus.data=user_temp[10]
            form.Ethnicgroup.data=user_temp[11]
            form.Religion.data=user_temp[12]

            found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
            if found_avatar and found_avatar[2] != "":
                _image_path = found_avatar[2]
            else:
                _image_path = file_path_default
            # if user_temp[13] == "admin":
            #    _roleadmin = "admin"
            #    _fullname_admin = user_temp[1]
        return render_template("core/user_information.html", form=form, image_path = _image_path,image_path_admin=_image_path_admin,informationuserid =  user_temp[0],
                            fullname = user_temp[1], roleuser=_roleuser ,idaccount=current_user.id,totp='None',readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin') and str(totp)!='None':
        
        # conn=db.connection()
        # cursor=conn.cursor()
        # sql="select r.role_name from role_user r join user_account u on u.role_id=r.id where u.id=?"
        # value=(idaccount)
        # cursor.execute(sql,value)
        # user_role=cursor.fetchone()
        # _roleuser=user_role[0]
        # _roleuser=""
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"

        
        session['idaccountadminmanager']=idaccount
        form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.*,r.role_name from informationUser i join user_account u on u.id=i.id_useraccount join role_user r on r.id=u.role_id  where i.id_useraccount=?"
        value=(idaccount)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        if user_temp:
            form.Fullname.data=user_temp[1]
            form.Nickname.data=user_temp[2]
            form.Email.data=user_temp[3]
            form.Contactaddress.data=user_temp[4]
            form.Phone.data=user_temp[6]
            form.LinkedIn.data=user_temp[7]
            form.Years.data=user_temp[8]
            form.Location.data = user_temp[9]
            form.Maritalstatus.data=user_temp[10]
            form.Ethnicgroup.data=user_temp[11]
            form.Religion.data=user_temp[12]

            _roleuser= user_temp[13]
            found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
            if found_avatar and found_avatar[2] != "":
                _image_path = found_avatar[2]
            else:
                _image_path = file_path_default
            _fullname=user_temp[1]
            
            session['_image_path_admin']=_image_path_admin
        return render_template("core/user_information.html", form=form, image_path = _image_path,informationuserid =  user_temp[0],
                            fullname = user_temp[1], roleuser=_roleuser,roleadmin = _roleadmin,idaccount=idaccount,totp=totp,readrights=session.get('readrights'),image_path_admin=_image_path_admin,fullname_admin = _fullname_admin)
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))


# user lastest employment
@core_bp.route('/latestEmployment/<informationuserid>/<totp>', methods=['post', 'get'])
@login_required
def latestEmployment(informationuserid,totp):
 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin,_fullname_admin
    if informationuserid==str(verify_user[0]) :
        
        
        form = latestEmploymentForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from latestEmployment where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.Employer.data=user_temp[1]
            form.Jobtittle.data=user_temp[2]
            form.AnnualSalary.data=user_temp[3]
            form.AnnualBonus.data=user_temp[4]
            form.RetentionBonus.data=user_temp[5]
            form.RetentionBonusExpiredDate.data=user_temp[6]
            form.StockOption.data=user_temp[7]
            form.StartDate.data = user_temp[8]
            form.EndDate.data=user_temp[9]
            
            return render_template("core/latestEmployment.html", form=form,
                image_path = _image_path,fullname=_fullname,informationuserid=informationuserid,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,
                 roleuser=_roleuser,totp='None',idaccount=current_user.id,readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        #global _image_path,_fullname,_roleuser
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        form = latestEmploymentForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from latestEmployment where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.Employer.data=user_temp[1]
            form.Jobtittle.data=user_temp[2]
            form.AnnualSalary.data=user_temp[3]
            form.AnnualBonus.data=user_temp[4]
            form.RetentionBonus.data=user_temp[5]
            form.RetentionBonusExpiredDate.data=user_temp[6]
            form.StockOption.data=user_temp[7]
            form.StartDate.data = user_temp[8]
            form.EndDate.data=user_temp[9]
            return render_template("core/latestEmployment.html", form=form,
                image_path = _image_path,fullname=_fullname,informationuserid=informationuserid,
                  roleuser=_roleuser,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,totp=totp,idaccount=session.get('idaccountadminmanager'),readrights=session.get('readrights'))
    else:
        flash("You are logging in illegally")
        return redirect('core/startPage.html')
    

# user lastest employment
@core_bp.route('/usercccd/<informationuserid>/<totp>', methods=['post', 'get'])
@login_required
def usercccd(informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    global _image_path,_front_cccd,_fullname,_roleuser
    if informationuserid==str(verify_user[0]):
        # global _image_path,_front_cccd,_fullname,_roleuser
        form = usercccdForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from information_cccd where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.No.data=user_temp[1]
            form.FullName.data=user_temp[2]
            form.DateOfbirth.data=user_temp[3]
            form.PlaceOfBirth.data=user_temp[4]
            form.Address.data=user_temp[5]
            form.IssueOn.data=user_temp[6]
        if user_temp is None:
            id = 0
        else:
            id = user_temp[0]
        print("id user is %d" % id)
        found_cccd = user_cccd.find_picture_name_by_id(id)
        if found_cccd and found_cccd[2] != "":
            _front_cccd = found_cccd[2]
        else:
            _front_cccd = ""

        if found_cccd and found_cccd[3] != "":
            _back_cccd = found_cccd[3]

        else:
            _back_cccd = ""
        print("front image is: "+ _front_cccd)
        print("back image is: "+ _front_cccd)
        return render_template("core/user_cccd.html", form=form, image_path = _image_path,fullname=_fullname,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,
                           informationuserid=informationuserid,front_cccd =_front_cccd,back_cccd =_back_cccd, roleuser=_roleuser ,totp='None'
                           ,idaccount=current_user.id,readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        form = usercccdForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from information_cccd where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.No.data=user_temp[1]
            form.FullName.data=user_temp[2]
            form.DateOfbirth.data=user_temp[3]
            form.PlaceOfBirth.data=user_temp[4]
            form.Address.data=user_temp[5]
            form.IssueOn.data=user_temp[6]
        if user_temp is None:
            id = 0
        else:
            id = user_temp[0]
        print("id user is %d" % id)
        found_cccd = user_cccd.find_picture_name_by_id(id)
        if found_cccd and found_cccd[2] != "":
            _front_cccd = found_cccd[2]
        else:
            _front_cccd = ""

        if found_cccd and found_cccd[3] != "":
            _back_cccd = found_cccd[3]

        else:
            _back_cccd = ""
        print("front image is: "+ _front_cccd)
        print("back image is: "+ _front_cccd)
        return render_template("core/user_cccd.html", form=form, image_path = _image_path,fullname=_fullname,
                           informationuserid=informationuserid,front_cccd =_front_cccd,back_cccd =_back_cccd,
                             roleuser=_roleuser,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin ,totp=totp,idaccount=session.get('idaccountadminmanager'),readrights=4)
    else:
        flash("You are logging in illegally")
        
        return redirect(url_for("authentication.logout"))
# upload CCCD image
@core_bp.route('/uploadCCCD/<informationuserid>', methods=['POST', 'get'])
@login_required
def uploadCCCD(informationuserid):
    global _front_cccd, _back_cccd,_fullname,_roleuser
    if request.method == 'POST':

        file_front = request.files['fileCCCD_front']
        file_back = request.files['fileCCCD_back']

        # Check if the file is empty
        if file_front.filename == '' and file_back.filename == '':
            flash('No selected file')
            return redirect(url_for('core.usercccd', informationuserid=informationuserid, fullname=_fullname, roleuser=_roleuser,roleadmin = _roleadmin))

        # Check if the file has an allowed extension
        if  allowed_file(file_front.filename) or allowed_file(file_back.filename):

            found_cccd = user_cccd.find_picture_name_by_id(informationuserid)

            if file_front.filename != '':
                filename_front = secure_filename(file_front.filename)
                file_front.save(os.path.join(Config.UPLOAD_FOLDER, filename_front))
            else:
                if found_cccd and  found_cccd[2] != '':
                    
                    file_front.filename = found_cccd[2]

                else:
                    file_front.filename = ""
            
            if file_back.filename != '':
                filename_back = secure_filename(file_back.filename)
                file_back.save(os.path.join(Config.UPLOAD_FOLDER, filename_back))
            else:
                if found_cccd and found_cccd[3] != '':
                    file_back.filename = found_cccd[3]
                    
                else:
                    file_back.filename = ""

            if found_cccd:
                user_cccd.update_pic_name(informationuserid,file_front.filename,file_back.filename)
                return redirect(url_for('core.usercccd', informationuserid=informationuserid, fullname=_fullname, roleuser=_roleuser,roleadmin = _roleadmin))
            else:
                new_cccd = user_cccd(informationuserid = informationuserid, front_pic_name= file_front.filename,back_pic_name= file_back.filename)
                id_pic = new_cccd.save()
            
            _front_cccd = file_front.filename
            _back_cccd = file_back.filename
            return redirect(url_for('core.extractCCCD', informationuserid=informationuserid, fullname=_fullname, roleuser=_roleuser,roleadmin = _roleadmin))
        else:
            flash('Allowed media types are - png, jpg, jpeg, gif')
            return redirect(url_for('core.home'))
    else:
        flash('Invalid request method')
        return redirect(url_for('core.home'))


# extract the CCCD file
@core_bp.route('/extractCCCD/<informationuserid>', methods=['GET','post'])
@login_required
def extractCCCD(informationuserid):
    global _front_cccd,_fullname,_roleuser
    # Ensure that _filename is not an empty string
    if not _front_cccd:
        flash('No file uploaded')
        return redirect(url_for('core.startPage'))
    img_path = os.path.join(Config.UPLOAD_FOLDER, _front_cccd)
    img = Image.open(img_path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img, lang='vie')
    print(text)
    return redirect(url_for('core.usercccd', informationuserid=informationuserid, fullname=_fullname, roleuser=_roleuser,roleadmin = _roleadmin))

# upload Healthy Insurance image
@core_bp.route('/upload_healthyInsurance/<informationuserid>', methods=['POST', 'get'])
@login_required
def upload_healthyInsurance(informationuserid):
    global _front_healthyInsurance, _back_healthyInsurance,_fullname
    if request.method == 'POST':

        file_front = request.files['fileHI_front']
        file_back = request.files['fileHI_back']

        # Check if the file is empty
        if file_front.filename == '' and file_back.filename == '':
            flash('No selected file')
            idaccount= (current_user.id)
            return redirect(url_for('core.userinformation',idaccount = idaccount))

        # Check if the file has an allowed extension
        if  allowed_file(file_front.filename) or allowed_file(file_back.filename):

            
            found_HI = user_healthyInsurance.find_picture_name_by_id(informationuserid)

            if file_front.filename != '':
                filename_front = secure_filename(file_front.filename)
                file_front.save(os.path.join(Config.UPLOAD_FOLDER, filename_front))
            else:
                if found_HI and found_HI[2]!= '':
                    file_front.filename = found_HI[2]
                else:
                    file_front.filename = ""
            
            if file_back.filename != '':
                filename_back = secure_filename(file_back.filename)
                file_back.save(os.path.join(Config.UPLOAD_FOLDER, filename_back))
            else:
                if found_HI and found_HI[3] != '':
                    file_back.filename = found_HI[3]
                else:
                    file_back.filename = ""
    
            if found_HI:
                user_healthyInsurance.update_pic_name(informationuserid,file_front.filename,file_back.filename)
                idaccount= (current_user.id)
                return redirect(url_for('core.userinformation',idaccount = idaccount))
            else:
                new_HI = user_healthyInsurance(informationuserid = id, front_pic_name= file_front.filename,back_pic_name= file_back.filename)
                id_pic = new_HI.save()
            
            _front_healthyInsurance = file_front.filename
            _back_healthyInsurance = file_back.filename
            
            return redirect('/extract_healthyInsurance')
        else:
            flash('Allowed media types are - png, jpg, jpeg, gif')
            return redirect(url_for('core.startPage'))
    else:
        flash('Invalid request method')
        return redirect(url_for('core.home'))
    


@core_bp.route('/extract_healthyInsurance', methods=['GET','post'])
@login_required
def extract_healthyInsurance():
    global _front_healthyInsurance
    # Ensure that _filename is not an empty string
    if not _front_healthyInsurance:
        flash('No file uploaded')
        return redirect(url_for('core.startPage'))
    img_path = os.path.join(Config.UPLOAD_FOLDER, _front_healthyInsurance)
    img = Image.open(img_path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img, lang='vie')
    print(text)
    idaccount= (current_user.id)
    return redirect(url_for('core.userinformation',idaccount = idaccount))


# update avatar image
@core_bp.route('/update_avatar/<informationuserid>/<totp>/<idaccount>', methods=['POST','get'])
@login_required
def upload_avatar(informationuserid,totp,idaccount):
    global _image_path
    if request.method == 'POST':
        # Check if the 'avatar' key is in the files of the request
        if 'avatar' not in request.files:
            flash('No file part')
            return redirect(url_for('core.startPage'))

        file = request.files['avatar']

        # Check if the file is empty
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('core.home'))

        # Check if the file has an allowed extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            id = informationuserid
            found_avatar = user_avatar.find_picture_name_by_id(id)
            if found_avatar:
                user_avatar.update_pic_name(informationuserid,file.filename)
                flash('update avatar successfully')
                _image_path = filename
                idaccount= (idaccount)
                return redirect(url_for('core.userinformation',idaccount = idaccount,totp=totp))
            else:
                new_avatar = user_avatar(informationuserid = id, pic_name= file.filename)
                id_pic = new_avatar.save()
                flash(
                    'save image successfully'
                )
                idaccount= idaccount
                return redirect(url_for('core.userinformation',idaccount = idaccount,totp=totp))
        else:
            flash('Allowed media types are - png, jpg, jpeg, gif')
            return redirect(url_for('core.startPage'))
    else:
        flash('Invalid request method')
        return redirect(url_for('core.home'))
# remove avatar
@core_bp.route('/remove_avatar/<informationuserid>/<totp>', methods = ['post','get'])
@login_required
def remove_avatar(informationuserid,totp):
    global file_path_default,_image_path
    print(file_path_default)
    _image_path = file_path_default
    user_avatar.update_pic_name(informationuserid,file_path_default)

    idaccount= (current_user.id)
    return redirect(url_for('core.userinformation',idaccount = idaccount,totp=totp))

# display image 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='source/' + filename), code=301)

# edit information user profile
@core_bp.route('/edit_userInformation/<col>/<informationuserid>/<totp>', methods = ['post','get'])
@login_required
def edit_userInformation(col,informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if informationuserid==str(verify_user[0]):
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = request.form.get(col)
        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()

        idaccount= (current_user.id)
        return redirect(url_for('core.userinformation',idaccount = idaccount,totp=totp))
    elif session.get('writerights')==1:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = request.form.get(col)
        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()

        idaccount= session.get('idaccountadminmanager')
        return redirect(url_for('core.userinformation',idaccount = idaccount,totp=totp))
    else:
        flash("You are logging in illegally")
        #return redirect(url_for("authentication.logout"))


# edit information user profile
@core_bp.route('/edit_latestEmployment/<col>/<informationuserid>', methods = ['post','get'])
@login_required
def edit_latestEmployment(col,informationuserid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if informationuserid==str(verify_user[0]):
        global _fullname
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE latestEmployment SET {col} = ? WHERE idinformationuser = ?"
        new_value = request.form.get(col)

        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()
        print("123456")
        return redirect(url_for('core.latestEmployment', informationuserid=informationuserid, fullname=_fullname))
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

# edit information user profile
@core_bp.route('/edit_informationcccd/<col>/<informationuserid>', methods = ['post','get'])
@login_required
def edit_informationcccd(col,informationuserid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if informationuserid==str(verify_user[0]):
        global _fullname
        conn= db.connection()
        cursor = conn.cursor()

        sql = f"UPDATE information_cccd SET {col} = ? WHERE idinformationuser = ?"
        new_value = request.form.get(col)
        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()

        return redirect(url_for('core.usercccd', informationuserid=informationuserid, fullname=_fullname, roleuser=_roleuser,roleadmin = _roleadmin))
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

# upload file in gg driver
# install: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

@core_bp.route('/upload_HCC/<informationuserid>', methods = ['post','get'])
@login_required
def upload_HCC(informationuserid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if informationuserid==str(verify_user[0]):
        global _driver_file_url,_attachedFileName,_fullname
        driver = DriveAPI()
        if request.method == 'POST':
            if 'filehcc' not in request.files:
                flash('no file part')
                return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
            
            file = request.files['filehcc']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))

            
                
            # Check if the file has an allowed extension
            if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # check if the file is image
                type = filename.split('.')[-1].lower()
                print("type is: %s" % type)
                if type not in ['docx', 'pdf']:
                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                    image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename ))
                    pdf_bytes = img2pdf.convert(image.filename)
                    document_name = request.form.get('documentname')
                    filename = f"{document_name}.pdf"
                    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(pdf_bytes)
                    image.close()
                    file.close()
                    print("Successfully made pdf file")
                else:
                    filename = request.form.get('documentname') +'.'+ filename.split('.')[-1].lower()
                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename)) 
                
                file_path = "static/source/" + filename
                driver.upload_file(file_path)
                # Delete the file from the server after uploading to Google Drive
                os.remove(file_path)
                _driver_file_url = driver.get_link_file_url()
                _driver_file_url=_driver_file_url.get('webContentLink')
                _attachedFileName = filename
                conn = db.connection()
                cursor = conn.cursor()
                sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
                cursor.execute(sql,informationuserid)
                temp = cursor.fetchall()
                cursor1 = conn.cursor()
                sql="""
                DECLARE @out int;
                EXEC CountHealthCheckCertificates @IdInformationUser=?,@count = @out OUTPUT;
                SELECT @out AS the_output;
                """
                cursor1.execute(sql,informationuserid)
                count = cursor1.fetchval()
                conn.commit()
                
                print("count is: " + str(count))
                print("HealthCheck 3")
                if count < 3 and count > 0:
                    for record in temp:
                        if record[1] == request.form.get('documentno') and record[2] != request.form.get('documentname'):
                            flash("Documnent No and document Name are existing, please try again")
                            return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname))
                    notarized_value = 1 if request.form.get('notarized') == 'Yes' else 'No'
                    print("Document No:", request.form.get('documentno'))
                    print("Document Name:", filename)
                    print("Notarized:", notarized_value)
                    print("Driver File URL:", _driver_file_url)
                    print("ID Information User:", informationuserid)
                    sql = 'INSERT INTO healthCheckCertificates VALUES (?, ?, ?, ?, ?)'
                    cursor.execute(sql, request.form.get('documentno'), filename, notarized_value, _driver_file_url, informationuserid)
                    cursor.commit()
                    conn.close()
                    print("HealthCheck 4")
                    flash("Uploaded document successfully")
                    return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
                elif count ==0:
                    notarized_value = "Yes" if request.form.get('notarized') == 'Yes' else "No"
                    sql = 'INSERT INTO healthCheckCertificates VALUES (?, ?, ?, ?, ?)'
                    cursor.execute(sql, request.form.get('documentno'), filename, 'Yes', _driver_file_url, informationuserid)
                    cursor.commit() 
                    conn.close()
                    print("HealthCheck 5")
                    flash("Uploaded document successfully")
                    return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
                else:
                    print("HealthCheck 6")
                    flash("The maximum total number of documents is 3. Please try again.")
                    return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))

            else:
                flash(' Only Allowed media types are docx,pdf, please try again!!!')
                return redirect(url_for('upload_HCC',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
        else:
            flash('Invalid request method')
            idaccount= (current_user.id)
            return redirect(url_for('core.userinformation',idaccount = idaccount))
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

@core_bp.route('/healthCheckCertificates/<informationuserid>/<totp>', methods = ['post','get'])
@login_required
def healthCheckCertificates(informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    global _fullname
    if informationuserid==str(verify_user[0]):
        # global _fullname
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()    
        return render_template("core/healthCheckCertificates.html",
                            image_path = _image_path,fullname=_fullname,
                            informationuserid=informationuserid, temp = temp,
                              roleuser=_roleuser,totp=totp,idaccount=current_user.id,
                              readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()    
        return render_template("core/healthCheckCertificates.html",
                            image_path = _image_path,fullname=_fullname,
                            informationuserid=informationuserid, temp = temp,
                              roleuser=_roleuser,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,totp=totp,
                              idaccount=session.get('idaccountadminmanager'),readrights=4)
    else:
        flash("You are logging in illegally")
    
        return redirect(url_for("authentication.logout"))

# upload Education background
@core_bp.route('/upload_education/<informationuserid>', methods = ['post','get'])
@login_required
def upload_education(informationuserid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if informationuserid==str(verify_user[0]):
        global _driver_file_url,_attachedFileName,_fullname
        driver = DriveAPI()
        if request.method == 'POST':
            if 'fileeducation' not in request.files:
                flash('no file part')
                return redirect(url_for('core.educationbackground',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
            
            file = request.files['fileeducation']
            if file.filename == '':
                flash('No selected file')
                return redirect(url_for('core.educationbackground',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
            # Check if the file has an allowed extension
            if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # check if the file is image
                type = filename.split('.')[-1].lower()
                print("type is: %s" % type)
                if type not in ['docx', 'pdf']:
                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                    image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename ))
                    pdf_bytes = img2pdf.convert(image.filename)
                    dot_position = filename.find('.')
                    document_name = filename[:dot_position]
                    filename = f"{document_name}.pdf"
                    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(pdf_bytes)
                    image.close()
                    file.close()
                    print("Successfully made pdf file")
                else:
                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename)) 
                file_path = "static/source/" + filename
                driver.upload_file(file_path)
                # Delete the file from the server after uploading to Google Drive
                os.remove(file_path)
                _driver_file_url = driver.get_link_file_url()
                _driver_file_url=_driver_file_url.get('webContentLink')
                _attachedFileName = filename
                conn = db.connection()
                cursor = conn.cursor()
                sql = "SELECT * from educationbackground where idinformationuser = ?"
                cursor.execute(sql,informationuserid)
                temp = cursor.fetchall()
                cursor1 = conn.cursor()
                sql="""
                DECLARE @out int;
                EXEC CountEducationBackground @IdInformationUser=?,@count = @out OUTPUT;
                SELECT @out AS the_output;
                """
                
                cursor1.execute(sql,informationuserid)
                count = cursor1.fetchval()
                print("Count is: " + str(count))
                conn.commit()
                if  count < 3:
                    sql = 'INSERT INTO educationbackground VALUES (?, ?, ?, ?)'
                    cursor.execute(sql, request.form.get('typeDegree'), filename, _driver_file_url, informationuserid)
                    cursor.commit()
                    conn.close()
                    flash("Uploaded document successfully")
                    return redirect(url_for('core.educationbackground',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
                else:
                    flash("The maximum total number of documents is 3. Please try again.")
                    return redirect(url_for('core.educationbackground',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))

            else:
                flash(' Only Allowed media types are docx,pdf, please try again!!!')
                return redirect(url_for('core.upload_education',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
        else:
            flash('Invalid request method')
            idaccount= (current_user.id)
            return redirect(url_for('core.userinformation',idaccount = idaccount))
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

@core_bp.route('/educationbackground/<informationuserid>/<totp>', methods = ['post','get'])
@login_required
def educationbackground(informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    global _fullname
    if informationuserid==str(verify_user[0]):
        # global _fullname
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from educationbackground where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()   
        return render_template("core/educationbackground.html",
                            image_path = _image_path,fullname=_fullname
                            ,informationuserid=informationuserid,
                              temp = temp, roleuser=_roleuser,totp='None',
                              idaccount=current_user.id,readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from educationbackground where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()    
        return render_template("core/educationbackground.html",
                            image_path = _image_path,fullname=_fullname,
                            informationuserid=informationuserid, temp = temp, 
                            roleuser=_roleuser,totp=totp,
                            idaccount=session.get('idaccountadminmanager'),readrights=4,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin)
    else:
        flash("You are logging in illegally")
        return totp
        #return redirect(url_for("authentication.logout"))
    
# upload Qualification background
@core_bp.route('/upload_qualification/<informationuserid>', methods = ['post','get'])
@login_required
def upload_qualification(informationuserid):
    global _driver_file_url,_attachedFileName,_fullname
    driver = DriveAPI()
    if request.method == 'POST':
        if 'filequalification' not in request.files:
            flash('no file part')
            return redirect(url_for('core.qualification',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
        
        file = request.files['filequalification']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('core.qualification',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
        # Check if the file has an allowed extension
        if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # check if the file is image
            type = filename.split('.')[-1].lower()
            print("type is: %s" % type)
            if type not in ['docx', 'pdf']:
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename ))
                pdf_bytes = img2pdf.convert(image.filename)
                dot_position = filename.find('.')
                document_name = filename[:dot_position]
                filename = f"{document_name}.pdf"
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)
                image.close()
                file.close()
                print("Successfully made pdf file")
            else:
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename)) 
            file_path = "static/source/" + filename
            driver.upload_file(file_path)
            # Delete the file from the server after uploading to Google Drive
            os.remove(file_path)
            _driver_file_url = driver.get_link_file_url()
            _driver_file_url=_driver_file_url.get('webContentLink')
            _attachedFileName = filename
            conn = db.connection()
            cursor = conn.cursor()
            sql = "SELECT * from qualification where idinformationuser = ?"
            cursor.execute(sql,informationuserid)
            temp = cursor.fetchall()
            cursor1 = conn.cursor()
            sql="""
            DECLARE @out int;
            EXEC CountQualification @IdInformationUser=?,@count = @out OUTPUT;
            SELECT @out AS the_output;
            """
            
            cursor1.execute(sql,informationuserid)
            count = cursor1.fetchval()
            print("Count is: " + str(count))
            conn.commit()
            if  count < 3:
                sql = 'INSERT INTO qualification VALUES (?, ?, ?, ?)'
                cursor.execute(sql, request.form.get('typeQualification'), filename, _driver_file_url, informationuserid)
                cursor.commit()
                conn.close()
                flash("Uploaded document successfully")
                return redirect(url_for('core.qualification',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
            else:
                flash("The maximum total number of documents is 3. Please try again.")
                return redirect(url_for('core.qualification',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))

        else:
            flash(' Only Allowed media types are docx,pdf, please try again!!!')
            return redirect(url_for('core.upload_qualification',informationuserid = informationuserid, fullname = _fullname, roleuser=_roleuser,roleadmin = _roleadmin))
    else:
        flash('Invalid request method')
        idaccount= (current_user.id)
        return redirect(url_for('core.userinformation',idaccount = idaccount))

@core_bp.route('/qualification/<informationuserid>/<totp>', methods = ['post','get'])
@login_required
def qualification(informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,current_user.id)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    global _fullname
    if informationuserid==str(verify_user[0]):
        # global _fullname
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from qualification where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()    
        return render_template("core/qualification.html",
                            image_path = _image_path,fullname=_fullname,
                            informationuserid=informationuserid, temp = temp,
                              roleuser=_roleuser,idaccount=current_user.id,totp='None',readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from qualification where idinformationuser = ?"
        cursor.execute(sql,informationuserid)
        temp = cursor.fetchall()
        df = pd.DataFrame()
        for record in temp:
            df2 = pd.DataFrame(list(record)).T
            df = pd.concat([df,df2])
        conn.close()    
        return render_template("core/qualification.html",
                            image_path = _image_path,fullname=_fullname,informationuserid=informationuserid,
                              temp = temp, roleuser=_roleuser,totp=totp,
                              idaccount=session.get('idaccountadminmanager'),readrights=4,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin)
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))    
    
@core_bp.route('/groupuserpage/<idinformationuser>', methods = ['post','get'])
def groupuserpage(idinformationuser):
    #return idinformationuser
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select g.*,r.rolename from groupuser g join groupuserdetail gd on g.id=gd.idgroupuser join informationUser i
    on i.id=gd.iduser join rolegroupuser r on r.id=gd.idrolegroupuser where i.id=?"""
    value=(str(idinformationuser))
    cursor.execute(sql,value)
    grouptemp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1],group[2],group[8]) for group in grouptemp]
    form =groupuserForm(request.form)
    # if form.validate_on_submit():
    #     conn=db.connection()
    #     cursor=conn.cursor()
    #     sql="""SET NOCOUNT ON;
    #             DECLARE @id int;
    #             insert into groupuser(name,createddate) values(?,GETDATE())
    #             SET @id = SCOPE_IDENTITY();            
    #             SELECT @id AS the_output;"""
    #     value=(form.group.data)
    #     cursor.execute(sql,value)
    #     idgrouptemp=cursor.fetchone()
    #     conn.commit()
    #     conn.close()
    #     return redirect(url_for("admin.updategropuser",idgroup=idgrouptemp[0]))
    return render_template('admin/groupuserpage.html',groups=groups,image_path=file_path_default,roleuser=_roleuser,form=form)
