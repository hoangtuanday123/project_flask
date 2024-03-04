import db
from flask_login import current_user,login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for,session
from core.models import informationUserJob,laborContract,forexsalary,employeeRelative
from core.forms import EmployeeRelativeForm
from .forms import Employeeinformation
from flask import Blueprint, render_template,redirect,url_for,flash,get_flashed_messages
from flask_login import login_required, current_user
from authentication.models import verifyPassword
import img2pdf
from PIL import Image
from core.models import allowed_file, allowed_attachment_file
from core.forms import DriveAPI
from werkzeug.utils import secure_filename
from __init__ import app
import os
from config import Config

employee = Blueprint("employee", __name__)

_image_path = ""
_fullname = ""
_roleuser = "employee"
_informationuserjobid = ""
_roleadmin = ""
_image_path_admin = ""
_fullname_admin = ""
@employee.route("/employeepage/<image_path>/<fullname>", methods=["GET", "POST"])
@login_required
def employeepage(image_path,fullname):
    global _image_path, _fullname, _roleuser
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?  "
    value=(current_user.id)
    cursor.execute(sql,value)
    user=cursor.fetchone()
    conn.commit()
    conn.close()
    _image_path = image_path
    _fullname = fullname
    return render_template("employee/employeepage.html",roleuser=_roleuser,informationuserid=user[0],image_path = _image_path,fullname=_fullname,idinformationuser=user[0])


@employee.route("/employeepage/informationuserjob/<informationuserid>/<totp>",methods=['GET','POST'])
@login_required
def informationuserjob(informationuserid,totp):
    global _informationuserjobid, _image_path_admin,_fullname_admin,_fullname,_roleuser,_image_path
    
    if informationuserid==str(current_user.idinformationuser):
        session['readrights']=None

        form=Employeeinformation(request.form)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select e.id,e.fullname from employeeRelative e join informationUser i on e.idinformationuser=i.id where i.id=?  "
        value=(informationuserid)
        cursor.execute(sql,value)
        employeerelative_temp=cursor.fetchall()
        conn.commit()
        conn.close()
        Employeerelative=[(person[0],person[1]) for person in employeerelative_temp]

        if request.method=='POST' and request.form.get('Privateinsurance')=='Privateinsurance':
            
            result=addlist(informationuserid,request.form['Employeerelative1'],'Privateinsurance')
        
        if request.method=='POST' and request.form.get('Additionalprivateinsurance')=='Additionalprivateinsurance':
            
            result=addlist(informationuserid,request.form['Employeerelative2'],'Additionalprivateinsurance')

        if request.method=='POST' and request.form.get('Dependant')=='Dependant':
            result=addlist(informationuserid,request.form['Employeerelative3'],'Dependant')

        if request.method=='POST' and request.form.get('Emergencycontact')=='Emergencycontact':
            result=addlist(informationuserid,request.form['Employeerelative4'],'Emergencycontact')
        
        if request.method=='POST' and request.form.get('Beneficiarycontact')=='Beneficiarycontact':
            result=addlist(informationuserid,request.form['Employeerelative5'],'Beneficiarycontact')

        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            select ei.id,e.fullname,e.Relationship,ei.col_Privateinsurance,ei.col_Additionalprivateinsurance,ei.col_Dependant,ei.col_Emergencycontact ,ei.col_Beneficiarycontact,e.id
            from employeerelative_informationuser ei join employeeRelative e on ei.idemployeerelative=e.id join informationUser i on i.id=ei.idinformationuser where i.id=?"""
        value=informationuserid
        cursor.execute(sql,value)
        temp=cursor.fetchall()
        conn.commit()
        conn.close() 
        temp1=[(user[0],user[1],user[2],user[3],user[8]) for user in temp if user[3]==True]
        temp2=[(user[0],user[1],user[2],user[4],user[8]) for user in temp if user[4]==True]
        temp3=[(user[0],user[1],user[2],user[5],user[8]) for user in temp if user[5]==True]
        temp4=[(user[0],user[1],user[2],user[6],user[8]) for user in temp if user[6]==True]
        temp5=[(user[0],user[1],user[2],user[7],user[8]) for user in temp if user[7]==True]

        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            select i.*,iu.Email,iu.phone,u.id from informationUserJob i join informationUser 
            iu on i.idinformationuser=iu.id join user_account u on
            u.id=iu.id_useraccount where i.idinformationuser=? and i.is_active=1"""
        value=(informationuserid)
        cursor.execute(sql,value)
        user=cursor.fetchone()
        conn.commit()
        conn.close()

        if user is not None:
            form.Bankaccount.data=str(user[5])
            form.bankname.data=str(user[6])
            form.Taxcode.data=str(user[8])
            form.Socialinsurancecode.data=str(user[9])
            form.Healthinsurancecardcode.data=str(user[10])
            form.Registeredhospitalcode.data=str(user[12])
            form.Registeredhospitalname.data=str(user[11])
            userjob=informationUserJob(EmployeeNo=user[0],Companysitecode=user[1],Department=user[2],Directmanager=user[3],Workforcetype=user[4],Workingphone=user[15],Workingemail=user[14],
                Bankaccount=user[5],Bankname=user[6],Taxcode=user[8],Socialinsurancecode=user[9],Healthinsurancecardcode=user[10],Registeredhospitalname=user[11],Registeredhospitalcode=user[12])
            _informationuserjobid = user[0]
        else:
            userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
                Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
        print("id information user before redirect:" + str(informationuserid))     
        return render_template("core/informationuserjob.html",userjob=userjob,informationuserid=informationuserid,image_path=_image_path,fullname=_fullname,
                               form=form,Employeerelative=Employeerelative,temp1=temp1,temp2=temp2,
                               temp3=temp3,temp4=temp4,temp5=temp5,roleuser=_roleuser
                               ,totp='None',idaccount=user[16],readrights=session.get('readrights'))
    
    elif str(totp)==session.get('is_admin'):
        
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        form=Employeeinformation(request.form)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select e.id,e.fullname from employeeRelative e join informationUser i on e.idinformationuser=i.id where i.id=?  "
        value=(informationuserid)
        cursor.execute(sql,value)
        employeerelative_temp=cursor.fetchall()
        conn.commit()
        conn.close()
        Employeerelative=[(person[0],person[1]) for person in employeerelative_temp]

        if request.method=='POST' and request.form.get('Privateinsurance')=='Privateinsurance':
            
            result=addlist(informationuserid,request.form['Employeerelative1'],'Privateinsurance')
        
        if request.method=='POST' and request.form.get('Additionalprivateinsurance')=='Additionalprivateinsurance':
            
            result=addlist(informationuserid,request.form['Employeerelative2'],'Additionalprivateinsurance')

        if request.method=='POST' and request.form.get('Dependant')=='Dependant':
            result=addlist(informationuserid,request.form['Employeerelative3'],'Dependant')

        if request.method=='POST' and request.form.get('Emergencycontact')=='Emergencycontact':
            result=addlist(informationuserid,request.form['Employeerelative4'],'Emergencycontact')
        
        if request.method=='POST' and request.form.get('Beneficiarycontact')=='Beneficiarycontact':
            result=addlist(informationuserid,request.form['Employeerelative5'],'Beneficiarycontact')

        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            select ei.id,e.fullname,e.Relationship,ei.col_Privateinsurance,ei.col_Additionalprivateinsurance,ei.col_Dependant,ei.col_Emergencycontact ,ei.col_Beneficiarycontact,e.id
            from employeerelative_informationuser ei join employeeRelative e on ei.idemployeerelative=e.id join informationUser i on i.id=ei.idinformationuser where i.id=?"""
        value=informationuserid
        cursor.execute(sql,value)
        temp=cursor.fetchall()
        conn.commit()
        conn.close() 
        temp1=[(user[0],user[1],user[2],user[3],user[8]) for user in temp if user[3]==True]
        temp2=[(user[0],user[1],user[2],user[4],user[8]) for user in temp if user[4]==True]
        temp3=[(user[0],user[1],user[2],user[5],user[8]) for user in temp if user[5]==True]
        temp4=[(user[0],user[1],user[2],user[6],user[8]) for user in temp if user[6]==True]
        temp5=[(user[0],user[1],user[2],user[7],user[8]) for user in temp if user[7]==True]

        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            select i.*,iu.Email,iu.phone,u.id from informationUserJob i join informationUser 
            iu on i.idinformationuser=iu.id join user_account u on
            u.id=iu.id_useraccount where i.idinformationuser=? and i.is_active=1"""
        value=(informationuserid)
        cursor.execute(sql,value)
        user=cursor.fetchone()
        conn.commit()
        conn.close()

        if user is not None:
            form.Bankaccount.data=str(user[5])
            form.bankname.data=str(user[6])
            form.Taxcode.data=str(user[8])
            form.Socialinsurancecode.data=str(user[9])
            form.Healthinsurancecardcode.data=str(user[10])
            form.Registeredhospitalcode.data=str(user[12])
            form.Registeredhospitalname.data=str(user[11])
            userjob=informationUserJob(EmployeeNo=user[0],Companysitecode=user[1],Department=user[2],Directmanager=user[3],Workforcetype=user[4],Workingphone=user[15],Workingemail=user[14],
                Bankaccount=user[5],Bankname=user[6],Taxcode=user[8],Socialinsurancecode=user[9],Healthinsurancecardcode=user[10],Registeredhospitalname=user[11],Registeredhospitalcode=user[12])
            _informationuserjobid = user[0]
        else:
            userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
                Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
        print("id information user before redirect:" + str(informationuserid))     
        return render_template("core/informationuserjob.html",userjob=userjob,informationuserid=informationuserid,image_path=_image_path,fullname=_fullname,
                               form=form,Employeerelative=Employeerelative,temp1=temp1
                               ,temp2=temp2,temp3=temp3,temp4=temp4,temp5=temp5
                               ,roleuser=_roleuser,totp=totp,idaccount=user[16],roleadmin = _roleadmin,image_path_admin=session.get('_image_path_admin'),fullname_admin = _fullname_admin,readrights=session.get('readrights'))
    
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))
    
def addlist(informationuserid,employeerelativeid,type):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        SET NOCOUNT ON;
        DECLARE @result int;
        exec pr_employeerelative_informationuser @idinformationuser=?,@idemployeerelative=?,@type=?,@result=@result OUTPUT;
        SELECT @result AS the_output;
        """
    value=(informationuserid,employeerelativeid,type)
    cursor.execute(sql,value)
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]

@employee.route("/employeepage/informationuserjob/deleterelative/<informationuserid>/<employeerelativeid>/<type>/<totp>",methods=['GET','POST'])
@login_required
def deleterelative(informationuserid,employeerelativeid,type,totp):
    #return str(employeerelativeid+type)
    if informationuserid==str(current_user.idinformationuser):
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            SET NOCOUNT ON;
            exec pr_delete_employeerelative_informationuser @idinformationuser=?,@idemployeerelative=?,@type=?;
            """
        value=(informationuserid,employeerelativeid,str(type))
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return redirect(url_for("employee.informationuserjob",informationuserid=informationuserid,totp='None'))
    elif str(totp)==session.get('is_admin'):
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            SET NOCOUNT ON;
            exec pr_delete_employeerelative_informationuser @idinformationuser=?,@idemployeerelative=?,@type=?;
            """
        value=(informationuserid,employeerelativeid,str(type))
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return redirect(url_for("employee.informationuserjob",informationuserid=informationuserid,totp=totp))

@employee.route("/edit_employeeinformation/<col>/<informationuserid>", methods=["GET", "POST"])
@login_required
def edit_employeeinformation(col,informationuserid):
    global _fullname,_roleuser
    conn= db.connection()
    cursor = conn.cursor()
    sql = f"UPDATE informationUserJob SET {col} = ? WHERE idinformationuser = ?"
    new_value = request.form.get(col)
    cursor.execute(sql,new_value,informationuserid)
    cursor.commit()
    cursor.close()
    return redirect(url_for('employee.informationuserjob', informationuserid = informationuserid,fullname=_fullname,roleuser= _roleuser))
    
@employee.route("/employeepage/informationuserjob/laborcontract/<informationuserjobid>/<informationuserid>/<totp>")
@login_required
def laborcontract(informationuserjobid,informationuserid,totp):
    global _image_path,_fullname,_roleuser,_informationuserjobid
    conn=db.connection()
    cursor=conn.cursor()
    print("job id is " + str(informationuserjobid))
    sql="select ij.id from user_account u join informationUser i on u.id=i.id_useraccount join informationUserJob ij on i.id=ij.idinformationuser where u.id=? and ij.id=?"
    value=(current_user.id,informationuserjobid)
    cursor.execute(sql,value)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if str(totp)==session.get('is_admin'):
        
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn=db.connection()
        cursor=conn.cursor()
        sql="select l.*,i.id_useraccount from laborContract l join informationUserJob ij on ij.id=l.idinformationUserJob join informationUser i on i.id=ij.idinformationuser  where l.idinformationUserJob=? and l.is_active=1 and ij.is_active=1"
        value=(informationuserjobid)
        cursor.execute(sql,value)
        contract=cursor.fetchone()
        conn.commit()
        conn.close()
        if contract is not None:
            contracttemp=laborContract(idcontract=contract[0],LaborcontractNo=contract[1],Laborcontracttype=contract[2],Laborcontractterm=contract[3],
                                Commencementdate=contract[4],Position=contract[5],Employeelevel=contract[6])
        else:
            contracttemp=laborContract(idcontract=None,LaborcontractNo=None,Laborcontracttype=None,Laborcontractterm=None,
                                Commencementdate=None,Position=None,Employeelevel=None)
        
        return render_template("core/contract.html",contract=contracttemp,informationuserid=informationuserid
                               ,image_path = _image_path,fullname =_fullname,image_path_admin=session.get('_image_path_admin'),fullname_admin = _fullname_admin,
                               roleuser=_roleuser,informationuserjobid = _informationuserjobid,idaccount=contract[9],totp=totp,roleadmin = _roleadmin)
    elif informationuserjobid==str(verify_user[0]) :
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from laborContract where idinformationUserJob=? and is_active=1"
        value=(informationuserjobid)
        cursor.execute(sql,value)
        contract=cursor.fetchone()
        conn.commit()
        conn.close()
        if contract is not None:
            contracttemp=laborContract(idcontract=contract[0],LaborcontractNo=contract[1],Laborcontracttype=contract[2],Laborcontractterm=contract[3],
                                Commencementdate=contract[4],Position=contract[5],Employeelevel=contract[6])
        else:
            contracttemp=laborContract(idcontract=None,LaborcontractNo=None,Laborcontracttype=None,Laborcontractterm=None,
                                Commencementdate=None,Position=None,Employeelevel=None)
        
        return render_template("core/contract.html",contract=contracttemp,informationuserid=informationuserid
                               ,image_path = _image_path,fullname =_fullname,
                               roleuser=_roleuser,informationuserjobid = _informationuserjobid,
                               idaccount=current_user.id,totp='None')
    
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

@employee.route("/employeepage/informationuserjob/forexsalary/<informationuserjobid>/<informationuserid>/<totp>")
@login_required
def forexsalaryfunction(informationuserjobid,informationuserid,totp):
    global _image_path,_fullname,_roleuser,_informationuserjobid
    conn=db.connection()
    cursor=conn.cursor()
    sql="select ij.id from user_account u join informationUser i on u.id=i.id_useraccount join informationUserJob ij on i.id=ij.idinformationuser where u.id=? and ij.id=?"
    value=(current_user.id,informationuserjobid)
    cursor.execute(sql,value)
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn=db.connection()
        cursor=conn.cursor()
        sql="select f.*,ft.type,i.id_useraccount from forexsalary f join forextype ft on f.forextypeid=ft.id join informationUserJob ij on ij.id=f.idinformationUserJob join informationUser i on i.id=ij.idinformationuser where f.idinformationUserJob=? and f.is_active=1 and ij.is_active=1"
        value=(informationuserjobid)
        cursor.execute(sql,value)
        forexsalarytemp=cursor.fetchone()
        conn.commit()
        conn.close()
        if forexsalarytemp is not None:
            forexSalary=forexsalary(Forex=forexsalarytemp[9],Annualsalary=forexsalarytemp[2],Monthlysalary=forexsalarytemp[3],Monthlysalaryincontract=forexsalarytemp[4],
                                    Quaterlybonustarget=forexsalarytemp[5],Annualbonustarget=forexsalarytemp[6])
        else:
            forexSalary=forexsalary(Forex=None,Annualsalary=None,Monthlysalary=None,Monthlysalaryincontract=None,
                                    Quaterlybonustarget=None,Annualbonustarget=None)
        return render_template("core/forexsalary.html",forexSalary=forexSalary
                               ,informationuserid=informationuserid,
                               image_path = _image_path,fullname =_fullname,
                               roleuser=_roleuser,informationuserjobid = _informationuserjobid,
                               idaccount=forexsalarytemp[10],totp=totp,roleadmin = _roleadmin,image_path_admin=session.get('_image_path_admin'),fullname_admin = _fullname_admin)
    elif informationuserjobid==str(verify_user[0]):

        conn=db.connection()
        cursor=conn.cursor()
        sql="select f.*,ft.type from forexsalary f join forextype ft on f.forextypeid=ft.id where idinformationUserJob=? and is_active=1"
        value=(informationuserjobid)
        cursor.execute(sql,value)
        forexsalarytemp=cursor.fetchone()
        conn.commit()
        conn.close()
        if forexsalarytemp is not None:
            forexSalary=forexsalary(Forex=forexsalarytemp[9],Annualsalary=forexsalarytemp[2],Monthlysalary=forexsalarytemp[3],Monthlysalaryincontract=forexsalarytemp[4],
                                    Quaterlybonustarget=forexsalarytemp[5],Annualbonustarget=forexsalarytemp[6])
        else:
            forexSalary=forexsalary(Forex=None,Annualsalary=None,Monthlysalary=None,Monthlysalaryincontract=None,
                                    Quaterlybonustarget=None,Annualbonustarget=None)
        return render_template("core/forexsalary.html",forexSalary=forexSalary
                               ,informationuserid=informationuserid,
                               image_path = _image_path,fullname =_fullname,
                               roleuser=_roleuser,informationuserjobid = _informationuserjobid,
                               idaccount=current_user.id,totp='None')
    
    else:
        flash("You are logging in illegally")
        return redirect(url_for("authentication.logout"))

@employee.route("/employeepage/informationuserjob/employeerelativelist/<informationuserid>/<totp>")
@login_required
def employeerelativelist(informationuserid,totp):
    #print("id in ers is " + str(informationuserid))
    if informationuserid==str(current_user.idinformationuser):
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from employeeRelative where idinformationuser=?"
        value=(informationuserid)
        cursor.execute(sql,value)
        employeerelativetemp=cursor.fetchall()
        conn.commit()
        conn.close()
        employeerelativelist=[(relative[0],relative[8],relative[1]) for relative in employeerelativetemp ]
        if employeerelativelist is None:
            employeerelativelist =[]
        return render_template("core/employeeRelativeList.html",employeerelativelist=employeerelativelist,informationuserid=informationuserid,
                            image_path = _image_path,fullname =_fullname,roleuser=_roleuser,totp='None',idaccount=current_user.id,readrights=session.get('readrights'))
    elif str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from employeeRelative where idinformationuser=?"
        value=(informationuserid)
        cursor.execute(sql,value)
        employeerelativetemp=cursor.fetchall()
        conn.commit()
        conn.close()
        employeerelativelist=[(relative[0],relative[8],relative[1]) for relative in employeerelativetemp ]
        if employeerelativelist is None:
            employeerelativelist =[]
        
        conn=db.connection()
        cursor=conn.cursor()
        sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i .id=?"
        value=(informationuserid)
        cursor.execute(sql,value)
        idaccounttemp=cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("core/employeeRelativeList.html",employeerelativelist=employeerelativelist,informationuserid=informationuserid,
                            image_path = _image_path,fullname =_fullname,
                            roleuser=_roleuser,totp=totp,idaccount=idaccounttemp[0],
                            readrights=4,roleadmin = _roleadmin,image_path_admin=session.get('_image_path_admin'),fullname_admin = _fullname_admin)

@employee.route("/employeepage/informationuserjob/employeerelativelist/addemployeerelationship/<informationuserid>/<totp>", methods=['GET', 'POST'])
@login_required
def addemployeerelative(informationuserid,totp):
    global _image_path, _fullname, _roleuser
    if informationuserid == str(current_user.idinformationuser):
        form = EmployeeRelativeForm(request.form)
        print("Form data:", form.data)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i .id=?"
        value=(informationuserid)
        cursor.execute(sql,value)
        idaccounttemp=cursor.fetchone()
        conn.commit()
        conn.close()
        if form.validate_on_submit():
            print("Form data1:", form.data)
            if form.errors:
                print("Form validation errors:", form.errors)
            conn = db.connection()
            cursor = conn.cursor()
            sql = """
                INSERT INTO employeeRelative(Relationship, phone, email, contactaddress, career, idinformationuser, critizenIdentìicationNo,
                fullname, dateofbirth, placeofbirth, issuedon, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            value = (
                form.Relationship.data, form.phone.data, form.email.data, form.contactaddress.data, form.career.data, informationuserid,
                form.citizenIdentificationNo.data, form.fullname.data, form.dateofbirth.data, form.placeofbirth.data, form.issued.data, form.address.data,
                )
            cursor.execute(sql, value)
            conn.commit()
            conn.close()
            flash("Insert employee relationship is successful")
            return redirect(url_for("employee.employeerelativelist", informationuserid=informationuserid, image_path=_image_path, fullname=_fullname, roleuser=_roleuser,totp='None'))
        
        return render_template("core/addEmployeeRelationship.html", form=form, informationuserid=informationuserid, image_path=_image_path,
                                fullname=_fullname, roleuser=_roleuser,totp='None',idaccount=idaccounttemp[0])

    else:
        flash("You are logging in illegally")
 

    
    


@employee.route("/employeepage/informationuserjob/employeerelative/<employeerelativeid>/<informationuserid>/<totp>/<idaccount>")
@login_required
def employeerelative(employeerelativeid,informationuserid,totp,idaccount):
    
    global _image_path,_fullname,_roleuser
    if str(totp)==session.get('is_admin'):
        if session.get('rolegroup')!='admin':
            _roleadmin=""
        else:
            _roleadmin = "admin"
        print("employeerelativeid is: " +employeerelativeid)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select e.id from user_account u join informationUser i on u.id=i.id_useraccount join employeeRelative e on e.idinformationuser=i.id  where u.id=? and e.id=?"
        value=(idaccount,employeerelativeid)
        cursor.execute(sql,value)
        verify_user=cursor.fetchone()
        conn.commit()
        conn.close()
        if employeerelativeid==str(verify_user[0]):
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="select e.*,i.id_useraccount from employeeRelative e join informationUser i on e.idinformationuser=i.id where e.id=?"
            value=(employeerelativeid)
            cursor.execute(sql,value)
            employeerelativetemp=cursor.fetchone()

            # cursor1 = conn.cursor()
            # sql1="select* from employeeDocument where employeerelativeid=?"
            # cursor1.execute(sql1,employeerelativeid)
            # temp = cursor1.fetchall()
            # conn.commit()
            # conn.close()
            form=EmployeeRelativeForm(request.form)
            if employeerelativetemp is not None:
                employeerelative=employeeRelative(id=employeerelativetemp[0],Relationship=employeerelativetemp[1],phone=employeerelativetemp[2],email=employeerelativetemp[3],
                                            contactaddress=employeerelativetemp[4],career=employeerelativetemp[5],citizenIdentificationNo=employeerelativetemp[7],
                                            fullname=employeerelativetemp[8],dateofbirth=employeerelativetemp[9],placeofbirth=employeerelativetemp[10],
                                            issuedon=employeerelativetemp[11],address=employeerelativetemp[12])
            else:
                employeerelative=employeeRelative(id=None,Relationship=None,phone=None,email=None,
                                            contactaddress=None,career=None,citizenIdentificationNo=None,
                                            fullname=None,dateofbirth=None,placeofbirth=None,
                                            issuedon=None,address=None)
            return render_template("core/employeerelative.html",informationuserid=informationuserid,employeerelative=employeerelative,
                                image_path = _image_path,fullname =_fullname, roleuser=_roleuser
                                ,employeerelativeid=employeerelativeid,totp=totp,
                                idaccount=employeerelativetemp[13],readrights=4,roleadmin = _roleadmin,image_path_admin=session.get('_image_path_admin'),fullname_admin = _fullname_admin)#, temp=temp)
    elif informationuserid==str(current_user.idinformationuser):
        print("employeerelativeid is: " +employeerelativeid)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select e.id from user_account u join informationUser i on u.id=i.id_useraccount join employeeRelative e on e.idinformationuser=i.id  where u.id=? and e.id=?"
        value=(current_user.id,employeerelativeid)
        cursor.execute(sql,value)
        verify_user=cursor.fetchone()
        conn.commit()
        conn.close()
        if employeerelativeid==str(verify_user[0]):
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="select * from employeeRelative where id=?"
            value=(employeerelativeid)
            cursor.execute(sql,value)
            employeerelativetemp=cursor.fetchone()

            # cursor1 = conn.cursor()
            # sql1="select* from employeeDocument where employeerelativeid=?"
            # cursor1.execute(sql1,employeerelativeid)
            # temp = cursor1.fetchall()
            # conn.commit()
            # conn.close()
            form=EmployeeRelativeForm(request.form)
            if employeerelativetemp is not None:
                employeerelative=employeeRelative(id=employeerelativetemp[0],Relationship=employeerelativetemp[1],phone=employeerelativetemp[2],email=employeerelativetemp[3],
                                            contactaddress=employeerelativetemp[4],career=employeerelativetemp[5],citizenIdentificationNo=employeerelativetemp[7],
                                            fullname=employeerelativetemp[8],dateofbirth=employeerelativetemp[9],placeofbirth=employeerelativetemp[10],
                                            issuedon=employeerelativetemp[11],address=employeerelativetemp[12])
            else:
                employeerelative=employeeRelative(id=None,Relationship=None,phone=None,email=None,
                                            contactaddress=None,career=None,citizenIdentificationNo=None,
                                            fullname=None,dateofbirth=None,placeofbirth=None,
                                            issuedon=None,address=None)
            return render_template("core/employeerelative.html",informationuserid=informationuserid,employeerelative=employeerelative,
                                image_path = _image_path,fullname =_fullname, roleuser=_roleuser
                                ,employeerelativeid=employeerelativeid,totp='None',
                                idaccount=current_user.id,readrights=session.get('readrights'))#, temp=temp)
    
        
    else:
            flash("You are logging in illegally")
            return redirect(url_for("authentication.logout"))   
    
@employee.route("/uploadDocument/<employeerelativeid>/<informationuserid>" ,methods=['post','get'])
@login_required
def uploadDocument(employeerelativeid,informationuserid):
        driver = DriveAPI()
        print("employee relative id is: %s" % employeerelativeid)
        if request.method == 'POST':
            if 'document_notarized' not in request.files:
                flash('no file part')

            file = request.files['document_notarized']
            
            if file.filename == '':
                flash('No selected file')
                
            # Check if the file has an allowed extension
            if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # check if the file is image
                type = filename.split('.')[-1].lower()
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
                conn=db.connection()
                cursor =conn.cursor()
                sql = 'INSERT INTO employeeDocument VALUES ( ?, ?,?)'
                cursor.execute(sql,filename, _driver_file_url, employeerelativeid)
                cursor.commit()
                conn.close()
                return redirect(url_for("employee.employeerelative",informationuserid=informationuserid,  image_path=_image_path, fullname=_fullname, roleuser=_roleuser,employeerelativeid=employeerelativeid))

            else:
                flash(' Only Allowed media types are docx,pdf, please try again!!!')
                return redirect(url_for("employee.employeerelative",informationuserid=informationuserid, image_path=_image_path, fullname=_fullname, roleuser=_roleuser,employeerelativeid=employeerelativeid))
        else:
            flash('Invalid request method')
            idaccount= (current_user.id)
            return redirect(url_for('core.userinformation',idaccount = idaccount))
        
@employee.route("/employeepage/informationuserjob/employeerelativelist/delete/<employeerelativeid>/<informationuserid>/<totp>",methods=['GET','POST'])
@login_required
def delete(employeerelativeid,informationuserid,totp):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    SET NOCOUNT ON;
    exec sp_delete_employeerelative @idemployeerelative=?;"""
    value=(employeerelativeid)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return redirect(url_for("employee.employeerelativelist",informationuserid=informationuserid,totp=totp))