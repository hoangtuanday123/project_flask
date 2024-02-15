from .forms import roleForm,SelectionForm
import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session, send_file,send_from_directory,make_response,Response
import pandas as pd
from tkinter import Tk, filedialog
from io import BytesIO
import json
import pyotp
from validation.forms import informationUserForm
from __init__ import file_path_default
import pdfkit
from io import BytesIO
import zipfile
admin = Blueprint("admin", __name__)
@admin.route('/adminpage')
@login_required
def adminpage():
    
    return render_template("admin/adminpage.html",image_path=file_path_default,roleuser="admin")

@admin.route('/adminpage/roles',methods=["GET", "POST"])
def displayRoles():
    
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
    return render_template("admin/manageRole.html",data=role_names,form=form,image_path=file_path_default,roleuser="admin")

@admin.route("/adminpage/updatepage/<idrole>",methods=["GET", "POST"])
def rolepage(idrole):
    
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
    return render_template("admin/updatepagerole.html",rolename=rolename[0],idrole=idrole,image_path=file_path_default,roleuser="admin")
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
    #The user has been assigned a role
    totp=pyotp.TOTP('adminroles')
    totp=totp.now()
    session['is_admin']=str(totp)
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
                           roletype=roles,table=table,selecttionitem=selecttionitem,image_path=file_path_default,totp=totp,roleuser="admin")

def is_all_null(array):
    for e in array:
        if e is not None:
            return False  # Nếu có ít nhất một phần tử không phải None, trả về False
    return True  # Nếu tất cả các phần tử đều là None, trả về True

@admin.route("/adminpage/usersmanager/assignrole/<idaccount>",methods=["GET", "POST"])
def assignrole(idaccount):
    
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
    return render_template("admin/updatepageuserrole.html",roles=roles,email=email[0],idaccount=idaccount,roleuser="admin")

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

# @admin.route('/adminpage/usersmanager/exportfilepdf/all')
# def exportallfilepdf():
#     conn=db.connection()
#     cursor=conn.cursor()
#     sql="select id from informationUser "
#     cursor.execute(sql)
#     user_temp=cursor.fetchall()
#     conn.commit()
#     conn.close()
#     userpdf=[(user[0]) for user in user_temp]
#     zip_buffer = BytesIO()
#     with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
#         for user in userpdf:
#             pdf_content = exportfilepdf( str(user))
#             zip_file.writestr(f'output'+ str(user)+'.pdf', pdf_content)
#     zip_buffer.seek(0)
#     response = Response(zip_buffer.read())
#     response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_all_user_pdf.zip"
#     response.headers["Content-Type"] = "application/zip"

#     return response
