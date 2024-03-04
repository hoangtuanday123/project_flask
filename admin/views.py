from .forms import roleForm,SelectionForm,groupuserForm
import db
from core.forms import laborcontractForm,forexsalaryForm
from employee.forms import Employeeinformation
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session, send_file,send_from_directory,make_response,Response
import pandas as pd
from tkinter import Tk, filedialog
from flask_mail import Message
from io import BytesIO
import json
import pyotp
from validation.forms import informationUserForm
from core.models import informationUserJob
from __init__ import file_path_default,mail,app
import pdfkit
from io import BytesIO
import zipfile
admin = Blueprint("admin", __name__)
_role_user = ""
_roleadmin = "admin"
_image_path_admin = ""
_fullname_admin = ""
@admin.route('/adminpage/<image_path_admin>/<fullname_admin>')
@login_required
def adminpage(image_path_admin, fullname_admin):
    global _image_path_admin,_fullname_admin
    _image_path_admin=image_path_admin
    _fullname_admin = fullname_admin
    print("admin fullname is " + _fullname_admin)
    return render_template("admin/adminpage.html",image_path_admin=_image_path_admin,roleuser=_role_user,roleadmin = _roleadmin,fullname_admin=fullname_admin)

@admin.route('/adminpage/roles',methods=["GET", "POST"])
def displayRoles():
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    role_user=cursor.fetchall()
    conn.commit()
    conn.close()
    form=roleForm(request.form)
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into role_user values(?)"
        value=(form.role.data)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return redirect(url_for("admin.displayRoles"))
    role_names = [(role[0],role[1]) for role in role_user]
    return render_template("admin/manageRole.html",data=role_names,form=form,image_path_admin=_image_path_admin,roleadmin=_roleadmin,fullname_admin =  _fullname_admin,roleuser=session.get('roleuser'))

@admin.route("/adminpage/updatepage/<idrole>",methods=["GET", "POST"])
def rolepage(idrole):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(idrole)
    cursor.execute(sql,value)
    rolename=cursor.fetchone()
    conn.commit()
    conn.close()
    if request.method=="POST":
        conn=db.connection()
        cursor=conn.cursor()
        sql="update role_user set role_name=? where id=?"
        value=(request.form["user_role"],idrole)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return redirect(url_for("admin.displayRoles"))
    return render_template("admin/updatepagerole.html",rolename=rolename[0],idrole=idrole,image_path_admin=_image_path_admin,roleadmin=_roleadmin,fullname_admin =  _fullname_admin,roleuser=session.get('roleuser'))
@admin.route("/adminpage/deleterole/<idrole>")
def deleterole(idrole):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""SET NOCOUNT ON;
            EXEC deleteRole @role_id=?"""
    value=(idrole)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return redirect(url_for("admin.displayRoles"))

@admin.route("/adminpage/usersmanager",methods=["GET", "POST"])
def displayusers():  
    #list account
    global _image_path_admin,_fullname_admin
    totp=pyotp.TOTP('adminroles')
    totp=totp.now()
    session['is_admin']=str(totp)
    session['rolegroup']='admin'
    _roleadmin = "admin"
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.role_id is not null"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersrole=[(user[0],user[1],user[2],user[3]) for user in users]
    #list of blocked users
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.is_active=0"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersblock=[(user[0],user[1],user[2],user[3]) for user in users]

    roles=[]
    roles.append('ALL')
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user "
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    for type in roles_temp:
        roles.append(type[1])
    #roles=[role[1] for role in roles_temp]
    conn.commit()
    conn.close()
   
    table='ALL'
    #load all user 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select i.*,r.role_name,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
     
    selecttionitem=[]
    session['selectionItem']=selecttionitem
    
    if request.method=='POST' and request.form.get('fillter')=='fillter':
        table=request.form['roletype']
        if table=='candidate':
            session['table']='candidate'
            roles.remove('candidate')
            roles.insert(0, 'candidate')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i  join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate'"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
        elif table=='ALL':
            session['table']='ALL'
            roles.remove('ALL')
            roles.insert(0, 'ALL')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
        elif table=='employee':
            session['table']='employee'
            roles.remove('employee')
            roles.insert(0, 'employee')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i  join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='employee'"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
    elif request.form.get('exportexcel')=='exportexcel':
        for user in Alluser:
            selecttionitem.append(request.form.get(str(user[0])))
        table=session.get('table')
        if(table==None):
            table='ALL'
        check1=is_all_null(selecttionitem)
        if check1==False:
            #return str(table)
            return redirect(url_for("admin.exportfileexcel",typerole=table))
        else:
            session['selectionItem']=[]
            return redirect(url_for("admin.exportfileexcel",typerole=table))
    elif request.form.get('exportpdf')=='exportpdf':
        for user in Alluser:
            selecttionitem.append(request.form.get(str(user[0])))
        Selecttionitem=session.get('selectionItem', [])
        table=session.get('table')
        
        if(table==None):
            table='ALL'
        check= is_all_null(Selecttionitem)
        if check==False:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for id in Selecttionitem:
                    if(str(id)!='None'):
                        pdf_content = exportfilepdf(str(id),table)
            
                        zip_file.writestr(f'output'+id+'.pdf', pdf_content)
            zip_buffer.seek(0)
            response = Response(zip_buffer.read())
            response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_pdf.zip"
            response.headers["Content-Type"] = "application/zip"

            return response
        else:
            Selecttionitem=[]
            for user in Alluser:
                if user[12]==table :
                   Selecttionitem.append(str(user[0]))
                if table=='ALL':
                    Selecttionitem.append(str(user[0]))
            session['selectionItem']=Selecttionitem
            Selecttionitem=session.get('selectionItem', [])
            #return Selecttionitem
            #return table
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for id in Selecttionitem:
                    if(str(id)!='None'):
                        
                        pdf_content = exportfilepdf(str(id),table)
            
                        zip_file.writestr(f'output'+id+'.pdf', pdf_content)
            zip_buffer.seek(0)
            response = Response(zip_buffer.read())
            response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_pdf.zip"
            response.headers["Content-Type"] = "application/zip"

            return response
        #return redirect(url_for("admin.exportfilepdf"))
    return render_template("admin/manageusers.html",Alluser=Alluser,usersrole=usersrole,usersblock=usersblock,
                           roletype=roles,table=table,selecttionitem=selecttionitem,image_path_admin=_image_path_admin,roleadmin=_roleadmin,fullname_admin =  _fullname_admin,totp=totp,roleuser=session.get('roleuser'))

def is_all_null(array):
    for e in array:
        if e is not None:
            return False  # Nếu có ít nhất một phần tử không phải None, trả về False
    return True  # Nếu tất cả các phần tử đều là None, trả về True

@admin.route("/adminpage/usersmanager/assignrole/<idaccount>/<userrole>",methods=["GET", "POST"])
def assignrole(idaccount,userrole):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    value=(idaccount)
    cursor.execute(sql,value)
    idinformation_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    idinformationuser=idinformation_temp[0]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    roles=[(role[1]) for role in roles_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select  i.email from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
    value=idaccount
    cursor.execute(sql,value)
    email=cursor.fetchall()
    conn.commit()
    conn.close()
    a=None
    b=None
    if request.method=="POST":
        for role in roles_temp:
            if request.form["roles"]==role[1] or request.form["roles"]==None:
                a=role[0]
                b=role[1]
                break
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUserJob ij join informationUser i on ij.idinformationuser=i.id where id_useraccount=?"
        values=(idaccount)
        cursor.execute(sql,values)
        validate=cursor.fetchone()
        conn.commit()
        conn.close()
        if(b=='employee'and validate == None):
            flash('please enter information job employee before assign role employee')
            return redirect(url_for("admin.displayusers"))
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="update user_account set role_id=? where id=?"
            values=(a,idaccount)
            cursor.execute(sql,values)
            conn.commit()
            conn.close()
            return redirect(url_for("admin.displayusers"))
    #return userrole
    return render_template("admin/updatepageuserrole.html",roles=roles,email=email[0],idaccount=idaccount,roleuser=session.get('roleuser'),userrole=userrole,informationuserid=idinformationuser,image_path_admin=_image_path_admin,roleadmin=_roleadmin,fullname_admin =  _fullname_admin)

@admin.route('/adminpage/usersmanager/blockuser/<idaccount>')
def blockaccount(idaccount):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update user_account set is_active=0 where id=?"
    values=(idaccount)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()
    flash('block account '+ idaccount + ' successfully')
    return redirect(url_for('admin.displayusers')) 

@admin.route('/adminpage/usersmanager/openblock/<idaccount>')
def openblock(idaccount):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update user_account set is_active=1 where id=?"
    values=(idaccount)
    cursor.execute(sql,values)
    conn.commit()
    conn.close()
    flash('open account '+ idaccount + ' successfully')
    return redirect(url_for('admin.displayusers')) 

@admin.route('/adminpage/usersmanager/exportfileexcel/<typerole>',methods=['GET','POST'])
def exportfileexcel(typerole):
    Selecttionitem=session.get('selectionItem', [])
    if typerole=='ALL':
        usersrole=[]
         
        if Selecttionitem !=[]:
            
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id where i.id=?"
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]))
        else:
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id"
            cursor.execute(sql)
            users1=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) for user in users1]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','employer','jobtitle','annual salary','annual bonus','retention bonus'
                                              ,'retention bonus expired date','stock option','start date','end date'])
        file_path='information_All_Account_User.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        response=send_from_directory('.',file_path,as_attachment=True)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        flash("export file successfully")
        return response
        
    elif typerole=='candidate':
        usersrole=[]
        
        if Selecttionitem !=[]:
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate' and i.id=?"
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) )
            
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate'"
            cursor.execute(sql)
            users2=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) for user in users2]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','employer','jobtitle','annual salary','annual bonus','retention bonus'
                                              ,'retention bonus expired date','stock option','start date','end date'])
        file_path='information_candidates.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        response=send_from_directory('.',file_path,as_attachment=True)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        flash("export file successfully")
        return response
    elif typerole=='employee':
        usersrole=[]
        
        if Selecttionitem !=[]:
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="""select i.*,ij.*,l.*,f.*,ft.type,r.role_name from  informationUser i join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on
                        ij.id=l.idinformationUserJob join forexSalary f on i.id=f.idinformationUserJob join forextype ft on ft.id=f.forextypeid join user_account u on i.id_useraccount=u.id
                        join role_user r on u.role_id=r.id where r.role_name='employee' and ij.is_active=1 and l.is_active=1 and f.is_active=1 and i.id=?"""
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],
                        user[18],user[19],user[20],user[21],user[22],user[23],user[24],user[28],user[29],user[30],user[31],user[32],user[33],user[45],user[38],user[39],
                        user[40],user[41],user[42],user[46]))
            
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select i.*,ij.*,l.*,f.*,ft.type,r.role_name from  informationUser i join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on
                ij.id=l.idinformationUserJob join forexSalary f on i.id=f.idinformationUserJob join forextype ft on ft.id=f.forextypeid join user_account u on i.id_useraccount=u.id
                join role_user r on u.role_id=r.id where r.role_name='employee' and ij.is_active=1 and l.is_active=1 and f.is_active=1"""
            cursor.execute(sql)
            users3=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],
                        user[18],user[19],user[20],user[21],user[22],user[23],user[24],user[28],user[29],user[30],user[31],user[32],user[33],user[45],user[38],user[39],
                        user[40],user[41],user[42],user[46]) for user in users3]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','companysite','department',
                                              'directmanager','workfortype','bankaccount','bankname','taxcode','Socialinsurancecode','Healthinsurancecardcode','Registeredhospitalcode','Registeredhospitalname',
                                              'LaborcontractNo','Laborcontracttype','Laborcontractterm','Commencementdate','Position','Employeelevel','type','Annualsalary','Annualbonustarget','Monthlysalary','Monthlysalaryincontract',
                                              'Quaterlybonustarget','role_name'])
            
        file_path='information_employee.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        response=send_from_directory('.',file_path,as_attachment=True)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        flash("export file successfully")
        return response

def exportfilepdf(idinformationuser,type):
    _roleuser=""
    if type=='candidate':
    
    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id and r.role_name='candidate'  where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]

        html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
                            user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  
    elif type=='employee':

    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id and r.role_name='employee'  where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]

        html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
                            user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  
    elif type=='ALL':

    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id   where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]

        html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
                            user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  

@admin.route('/adminpage/usersmanager/createemployee/<idinformation>',methods=['GET','POST'])
def createemployeeinfor(idinformation):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUserJob where idinformationuser=? and is_active=1"
    value=(idinformation)
    cursor.execute(sql,value)
    informationjob=cursor.fetchone()
    conn.close()
    if informationjob is  None:
        form=Employeeinformation(request.form)
        userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
                    Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
        temp=(0,' ')
        companysitecode=[]
        companysitecode.append(temp)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from forextype "
        cursor.execute(sql)
        companysitecode_temp=cursor.fetchall()
        conn.close()
        for code in companysitecode_temp:
            temp=(code[0],code[1])
            companysitecode.append(temp)
        if form.validate_on_submit():
            code=request.form['companysitecode']
            conn=db.connection()
            cursor=conn.cursor()
            sql="insert into informationUserJob values(?,?,?,?,?,?,?,?,?,?,?,?,?)"
            value=(code,form.department.data,form.directmanager.data,
                form.workfortype.data,form.Bankaccount.data,form.bankname.data,form.Taxcode.data,
                form.Socialinsurancecode.data,form.Healthinsurancecardcode.data,form.Registeredhospitalname.data,
                form.Registeredhospitalcode.data,idinformation,1)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
            return redirect(url_for('admin.createlaborcontract',idinformation=idinformation)) 
    else:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select * from laborContract l join  informationUserJob ij on l.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
        where i.id=? and l.is_active=1 and ij.is_active=1"""
        value=(idinformation)
        cursor.execute(sql,value)
        labor=cursor.fetchone()  
        conn.close() 
        if labor is None:
            return redirect(url_for('admin.createlaborcontract',idinformation=idinformation)) 
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select * from forexSalary f join  informationUserJob ij on f.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
            where i.id=? and f.is_active=1 and ij.is_active=1"""
            value=(idinformation)
            cursor.execute(sql,value)
            forex=cursor.fetchone()  
            conn.close()
            if forex is None:
                return redirect(url_for('admin.createforexsalary',idinformation=idinformation,image_path=file_path_default,roleuser=_role_user,roleadmin = _roleadmin)) 
            else:
                flash('information job employee is exist')
                return redirect(url_for('admin.displayusers'))
    return render_template("admin/admininformationuser.html",userjob=userjob,informationuserid=idinformation,form=form,companysitecode=companysitecode,roleuser=session.get('roleuser'))
                            #,image_path=_image_path,Employeerelative=Employeerelative,temp1=temp1,temp2=temp2,temp3=temp3,temp4=temp4,temp5=temp5)    
    
@admin.route('/adminpage/usersmanager/createlaborcontract/<idinformation>',methods=['GET','POST'])
def createlaborcontract(idinformation):
    form=laborcontractForm(request.form)
    # form.Laborcontracttype.data=None
    # form.Laborcontractterm.data=None
    # form.Commencementdate.data=None
    # form.Position.data=None
    # form.Employeelevel.data=None
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUserJob where idinformationuser=? and is_active=1"
    value=(idinformation)
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into laborContract values(null,?,?,?,?,?,?,?)"
        value=(form.Laborcontracttype.data,form.Laborcontractterm.data,form.Commencementdate.data,form.Position.data,form.Employeelevel.data,idinformationuserjob[0],1)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return redirect(url_for('admin.createforexsalary',idinformation=idinformation))
    return render_template('admin/adminlaborcontract.html',informationuserid=idinformation,form=form,image_path=file_path_default,roleuser=session.get('roleuser'))

@admin.route('/adminpage/usersmanager/createforexsalary/<idinformation>',methods=['GET','POST'])
def createforexsalary(idinformation):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,companysitecode from informationUserJob where idinformationuser=? and is_active=1"
    value=(idinformation)
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    form=forexsalaryForm(request.form)
    form.forextype.data=idinformationuserjob[1]
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into forexSalary values(?,?,?,?,?,?,?,1)"
        value=(form.forextype.data,form.Annualsalary.data,form.Monthlysalary.data,
               form.Monthlysalaryincontract.data,form.Quaterlybonustarget.data,form.Annualbonustarget.data,idinformationuserjob[0])
        cursor.execute(sql,value)
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i.id=?"
        value=(idinformation)
        cursor.execute(sql,value)
        idaccount=cursor.fetchone()
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set role_id =1 where id=?"
        value=(idaccount[0])
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        flash('create information job employee is successful')
        return redirect(url_for('admin.displayusers'))
    return render_template('admin/adminforexsalary.html',idinformation=idinformation,form=form,image_path=file_path_default,roleuser=session.get('roleuser'))

@admin.route('/adminpage/groupuserpage',methods=['GET','POST'])
def groupuserpage():
    _roleadmin = "admin"
    session['rolegroup']='admin'
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser"
    cursor.execute(sql)
    grouptemp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1],group[2],'admin') for group in grouptemp]
    form =groupuserForm(request.form)
    if form.validate_on_submit():
        conn=db.connection()
        cursor=conn.cursor()
        sql="""SET NOCOUNT ON;
                DECLARE @id int;
                insert into groupuser(name,createddate) values(?,GETDATE())
                SET @id = SCOPE_IDENTITY();            
                SELECT @id AS the_output;"""
        value=(form.group.data)
        cursor.execute(sql,value)
        idgrouptemp=cursor.fetchone()
        conn.commit()
        conn.close()
        return redirect(url_for("admin.updategropuser",idgroup=idgrouptemp[0],rolegroup='admin'))
    return render_template('admin/groupuserpage.html',groups=groups,image_path=file_path_default,roleuser=session.get('roleuser'),form=form,rolegroup='admin',roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin)


@admin.route('/adminpage/groupuserpage/updategroupuser/<idgroup>/<rolegroup>',methods=['GET','POST'])
def updategropuser(idgroup,rolegroup):
    readrights(rolegroup)
    session['rolegroup']=rolegroup
    if session.get('rolegroup')!='admin':
        _roleadmin=""
    else:
        _roleadmin = "admin"
    form =groupuserForm(request.form)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser where id=?"
    value=(idgroup)
    cursor.execute(sql,value)
    group=cursor.fetchone()
    conn.commit()
    conn.close()

    usersSelect=[]
    usersSelect.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,email from informationUser"
    cursor.execute(sql)
    usersSelecttemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for user in usersSelecttemp:
        usersSelect.append((user[0],user[1]))


    grouprole=[]
    grouprole.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from rolegroupuser"
    cursor.execute(sql)
    grouproletemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for role in grouproletemp:
        grouprole.append((role[0],role[1]))

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select gd.id, i.Fullname,r.rolename,g.name,gd.createddate,u.id from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id join user_account u on u.id=i.id_useraccount where g.id=?"""
    value=(idgroup)
    cursor.execute(sql,value)
    userstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    users=[(user[0],user[1],user[2],user[3],user[4],user[5]) for user in userstemp]

    if form.validate_on_submit()  and request.form.get('updategroup')=='updategroup':
        groupuser = form.group.data
        if groupuser == '0':
            flash('input is space')
            return redirect(url_for('admin.updategropuser',idgroup=idgroup))
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
                    join groupuser g on gd.idgroupuser=g.id where g.id=?"""
            value=(idgroup)
            cursor.execute(sql,value)
            notifyemail=cursor.fetchall()
            conn.commit()
            conn.close()

            conn=db.connection()
            cursor=conn.cursor()
            sql="update groupuser set name=?,alias=?,email=?,url=?,description=? where id=?"
            value=(groupuser,form.alias.data,form.email.data,
                   form.url.data,form.description.data,idgroup)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
            flash('update group user  is successful')

            for notify in notifyemail:
                #send email notify
            
                html = "update group: "+ str(users[0][3]) 
                subject = "Group have been updated to group: "+ +str(groupuser) +",alias: " +str(form.alias.data)+",email: "+str(form.email.data)+",url: "+str(form.url.data)+",description: "+str(form.description.data)
                
                send_email(notify[0], subject, html)
            return redirect(url_for('admin.updategropuser',idgroup=idgroup,rolegroup=rolegroup))
    elif request.method=='POST' and request.form.get('adduser')=='adduser':
        usersSelect=request.form["usersSelect"]
        grouprole=request.form["grouprole"]
        if usersSelect == '0' or grouprole == '0':
            flash('please enter full information')
            return redirect(url_for('admin.updategropuser',idgroup=idgroup))
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
            SET NOCOUNT ON;
            DECLARE @id int;
            insert into groupuserdetail(iduser,idrolegroupuser,idgroupuser,createddate) values(?,?,?,GETDATE())
            SET @id = SCOPE_IDENTITY();            
            SELECT @id AS the_output;
            """
            value=(usersSelect,grouprole,idgroup)
            cursor.execute(sql,value)
            idgroupuserdetail=cursor.fetchone()
            conn.commit()
            conn.close()
            flash('add  user  is successful')

            conn=db.connection()
            cursor=conn.cursor()
            sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
                    join groupuser g on gd.idgroupuser=g.id where gd.id=?"""
            value=(idgroupuserdetail[0])
            cursor.execute(sql,value)
            notifyemail=cursor.fetchone()
            conn.commit()
            conn.close()
            #send email notify
            
            html = "You have been added to the group: "+ str(notifyemail[2]) +" with role: " +str(notifyemail[1])
            subject = "wellcome to "+ str(notifyemail[2])+" group"
            send_email(notifyemail[0], subject, html)

            return redirect(url_for('admin.updategropuser',idgroup=idgroup,rolegroup=rolegroup))
    elif request.method=='POST' and request.form.get('deletegroup')=='deletegroup':
        return redirect(url_for('admin.deletegroupuser',idgroup=idgroup))
    else:
        form.group.data=group[1]
        form.alias.data=group[4]
        form.email.data=group[5]
        form.url.data=group[6]
        form.description.data=group[7]

    
    totp=pyotp.TOTP('adminroles')
    totp=totp.now()
    session['is_admin']=str(totp)

    return render_template('admin/updategroupuser.html',idgroup=idgroup,image_path=file_path_default,roleuser=session.get('roleuser')
                           ,usersSelect=usersSelect,grouprole=grouprole,users=users,
                           rolegroup=rolegroup,totp=str(totp),form=form,roleadmin = _roleadmin,image_path_admin=_image_path_admin,fullname_admin = _fullname_admin)

@admin.route('/adminpage/groupuserpage/updategroupuser/deletegroupuser/<idgroup>',methods=['GET','POST'])
def deletegroupuser(idgroup):

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id where g.id=?"""
    value=(idgroup)
    cursor.execute(sql,value)
    notifyemail=cursor.fetchall()
    conn.commit()
    conn.close()

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
            delete groupuserdetail where idgroupuser=?
            delete groupuser where id=?"""
    value=(idgroup,idgroup)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    flash('removed  group user  is successful')

    #send email notify
    for notify in notifyemail:
        html = "You have been removed from the group: "+ str(notify[2]) +" with role: " +str(notify[1])
        subject = "notice of member deletion from "+ str(notify[2])+" group"
        send_email(notify[0], subject, html)

    return redirect(url_for('admin.groupuserpage'))

@admin.route('/adminpage/groupuserpage/updategroupuser/deleteuser/<idgroupuserdetail>/<idgroup>/<rolegroup>',methods=['GET','POST'])
def deleteuser(idgroupuserdetail,idgroup,rolegroup):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id where gd.id=?"""
    value=(idgroupuserdetail)
    cursor.execute(sql,value)
    notifyemail=cursor.fetchone()
    conn.commit()
    conn.close()

    conn=db.connection()
    cursor=conn.cursor()
    sql="delete groupuserdetail where id=?"
    value=(idgroupuserdetail)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    flash('delete  user  is successful')
    #send email notify
    
    html = "You have been removed from the group: "+ str(notifyemail[2]) +" with role: " +str(notifyemail[1])
    subject = "notice of member deletion from "+ str(notifyemail[2])+" group"
    send_email(notifyemail[0], subject, html)
    return redirect(url_for('admin.updategropuser',idgroup=idgroup,rolegroup=rolegroup))

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )
    mail.send(msg)

def readrights(rolegroup):
    if rolegroup=="manager" or rolegroup=="admin":
        session["readrights"]=4
        session['writerights']=1
    elif rolegroup=="leader":
        session["readrights"]=3
    elif rolegroup=="member" or rolegroup=="client":
        session["readrights"]=2
    else:
        session["readrights"]=5
        
