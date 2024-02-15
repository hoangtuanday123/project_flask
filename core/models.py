from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired,InputRequired
import db
from pymongo import MongoClient
from config import Config


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
def allowed_attachment_file(filename):
    """Check if the given filename has an allowed extension (docx or pdf)."""
    allowed_extensions = {'docx', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions



class user_avatar():
    informationuserid=""
    pic_name=""

    def __init__(self, informationuserid, pic_name):
        self.informationuserid = informationuserid
        self.pic_name = pic_name
    
    def save(self):
        # Kết nối đến SQL Server
        conn = db.connection()
        cursor=conn.cursor()

        # insert data
        sql = "insert into user_avatar values(?,?)"
        cursor.execute(sql,self.informationuserid,self.pic_name)
        conn.commit()
        conn.close()     
        # Trả về ID của tài liệu đã chèn
        return True
    
    
    def find_picture_name_by_id(informationuserid):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Tìm kiếm theo informationuserid
        sql = "select* from user_avatar where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_avatar = cursor.fetchone()
        conn.commit()

        # Đóng kết nối
        conn.close() 

        # Trả về một đối tượng User hoặc None nếu không tìm thấy
        return user_avatar if user_avatar else None

    def update_pic_name(informationuserid, new_pic_name):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Cập nhật tài liệu dựa trên username
        sql = "update user_avatar set pic_name = ? where idinformationuser =?"
        cursor.execute(sql,new_pic_name,informationuserid)
        conn.commit()

        # Đóng kết nối
        conn.close() 

        return True 


class user_cccd():

    informationuserid=""
    front_pic_name=""
    back_pic_name=""

    def __init__(self, informationuserid, front_pic_name, back_pic_name):
        self.informationuserid = informationuserid
        self.front_pic_name = front_pic_name
        self.back_pic_name = back_pic_name
    
    def save(self):
        # Kết nối đến SQL Server
        conn = db.connection()
        cursor=conn.cursor()

        # insert data
        sql = "insert into user_cccd values(?,?,?)"
        cursor.execute(sql,self.informationuserid,self.front_pic_name, self.back_pic_name)
        conn.commit()
        conn.close()     
        # Trả về ID của tài liệu đã chèn
        return True
    
    
    def find_picture_name_by_id(informationuserid):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Tìm kiếm theo informationuserid
        sql = "select* from user_cccd where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_avatar = cursor.fetchone()
        conn.commit()

        # Đóng kết nối
        conn.close() 

        # Trả về một đối tượng User hoặc None nếu không tìm thấy
        return user_avatar if user_avatar else None

    def update_pic_name(informationuserid, new_front_pic_name, new_back_pic_name):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Cập nhật tài liệu dựa trên username
        sql = "update user_cccd set front_pic_name = ?, back_pic_name = ? where idinformationuser =?"
        cursor.execute(sql,new_front_pic_name,new_back_pic_name,informationuserid)
        conn.commit()

        # Đóng kết nối
        conn.close() 

        return True 

class user_healthyInsurance():

    informationuserid=""
    front_pic_name=""
    back_pic_name=""

    def __init__(self, informationuserid, front_pic_name, back_pic_name):
        self.informationuserid = informationuserid
        self.front_pic_name = front_pic_name
        self.back_pic_name = back_pic_name
    
    def save(self):
        # Kết nối đến SQL Server
        conn = db.connection()
        cursor=conn.cursor()

        # insert data
        sql = "insert into user_healthyInsurance values(?,?,?)"
        cursor.execute(sql,self.informationuserid,self.front_pic_name, self.back_pic_name)
        conn.commit()
        conn.close()     
        # Trả về ID của tài liệu đã chèn
        return True
    
    
    def find_picture_name_by_id(informationuserid):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Tìm kiếm theo informationuserid
        sql = "select* from user_healthyInsurance where idinformationuser=?"
        cursor.execute(sql,informationuserid)
        user_avatar = cursor.fetchone()
        conn.commit()

        # Đóng kết nối
        conn.close() 

        # Trả về một đối tượng User hoặc None nếu không tìm thấy
        return user_avatar if user_avatar else None

    def update_pic_name(informationuserid, new_front_pic_name, new_back_pic_name):
        # Kết nối đến SQL server
        conn = db.connection()
        cursor=conn.cursor()

        # Cập nhật tài liệu dựa trên username
        sql = "update user_healthyInsurance set front_pic_name = ?, back_pic_name = ? where idinformationuser =?"
        cursor.execute(sql,new_front_pic_name,new_back_pic_name,informationuserid)
        conn.commit()

        # Đóng kết nối
        conn.close() 
        return True 


class informationUserJob():
    EmployeeNo=0
    Companysitecode=""
    Department=""
    Directmanager=""
    Workforcetype=""
    Workingphone=""
    Workingemail=""
    Bankaccount=""
    Bankname=""
    Taxcode=""
    Socialinsurancecode=""
    Healthinsurancecardcode=""
    Registeredhospitalname=""
    Registeredhospitalcode=""
    
    def __init__(self,EmployeeNo,Companysitecode,Department,Directmanager,Workforcetype,Workingphone,Workingemail,Bankaccount, Bankname,
    Taxcode,Socialinsurancecode,Healthinsurancecardcode,Registeredhospitalname,
    Registeredhospitalcode):
        self.EmployeeNo=EmployeeNo
        self.Companysitecode = Companysitecode
        self.Department = Department
        self.Directmanager=Directmanager
        self.Workforcetype = Workforcetype
        self.Workingphone = Workingphone
        self.Workingemail=Workingemail
        self.Bankaccount=Bankaccount
        self.Bankname=Bankname
        
        self.Taxcode=Taxcode
        self.Socialinsurancecode=Socialinsurancecode
        self.Healthinsurancecardcode=Healthinsurancecardcode
        self.Registeredhospitalname=Registeredhospitalname
        self.Registeredhospitalcode=Registeredhospitalcode


class laborContract():
    idcontract=None
    LaborcontractNo=None
    Laborcontracttype=None
    Laborcontractterm=None
    Commencementdate=None
    Position=None
    Employeelevel=None
    
    def __init__(self,idcontract,LaborcontractNo,Laborcontracttype,Laborcontractterm,Commencementdate,Position,Employeelevel):
       
        self.idcontract=idcontract
        self.LaborcontractNo=LaborcontractNo
        self.Laborcontracttype=Laborcontracttype
        self.Laborcontractterm=Laborcontractterm
        self.Commencementdate=Commencementdate
        self.Position=Position
        self.Employeelevel=Employeelevel
class forexsalary():
    Forex=""
    Annualsalary=""
    Monthlysalary=""
    Monthlysalaryincontract=""
    Quaterlybonustarget=""
    Annualbonustarget=""
    
    def __init__(self ,Forex,Annualsalary,Monthlysalary,
    Monthlysalaryincontract,Quaterlybonustarget,Annualbonustarget):
       
        self.Forex=Forex
        self.Annualsalary=Annualsalary
        self.Monthlysalary=Monthlysalary
        self.Monthlysalaryincontract=Monthlysalaryincontract
        self.Quaterlybonustarget=Quaterlybonustarget
        self.Annualbonustarget=Annualbonustarget
        

class employeeRelative():
    id=""
    Relationship=""
    phone=""
    email=""
    contactaddress=""
    career=""
    citizenIdentificationNo=""
    fullname=""
    dateofbirth=""
    placeofbirth=""
    address=""
    issuedon=""
    def __init__(self ,id,Relationship,phone,
    email,contactaddress,career,citizenIdentificationNo,fullname,dateofbirth,placeofbirth,address,issuedon):
       
        self.id=id
        self.Relationship=Relationship
        self.phone=phone
        self.email=email
        self.contactaddress=contactaddress
        self.career=career
        self.citizenIdentificationNo=citizenIdentificationNo
        self.fullname=fullname
        self.dateofbirth=dateofbirth
        self.placeofbirth=placeofbirth
        self.address=address
        self.issuedon=issuedon
        



