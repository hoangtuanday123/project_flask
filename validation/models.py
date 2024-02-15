from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired
class informationUser():
    id=0,
    Fullname="",
    Nickname="",
    Email="",
    Contactaddress="",
    id_useraccount=""
    Phone =""
    LinkedIn =""
    Years =""
    Location =""
    Maritalstatus =""
    Ethnicgroup =""
    Religion =""



    def __init__(self,id,Fullname,Nickname,Email,Contactaddress,id_useraccount,Phone,LinkedIn,Years,Location,Maritalstatus,Ethnicgroup,Religion):
        self.id=id
        self.Fullname = Fullname
        self.Nickname = Nickname
        self.Email=Email
        self.Contactaddress = Contactaddress
        self.id_useraccount = id_useraccount
        self.Phone = Phone
        self.LinkedIn = LinkedIn
        self.Years = Years
        self.Location = Location
        self.Maritalstatus = Maritalstatus
        self.Ethnicgroup = Ethnicgroup
        self.Religion = Religion

class latestEmployment():
    id=0
    Employer=""
    Jobtittle = ""
    AnnualSalary = ""
    AnnualBonus = ""
    RetentionBonus = ""
    RetentionBonusExpiredDate = ""
    StockOption = ""
    StartDate = ""
    EndDate = ""
    IdInformationUser = ""

    def __init__(self,id,Employer,Jobtittle,AnnualSalary,AnnualBonus,RetentionBonus,RetentionBonusExpiredDate,StockOption,StartDate,EndDate,IdInformationUser):
        self.id= id
        self.Employer =Employer
        self.Jobtittle =Jobtittle
        self.AnnualBonus =AnnualBonus
        self.AnnualSalary = AnnualSalary
        self.RetentionBonus =RetentionBonus
        self.RetentionBonusExpiredDate =RetentionBonusExpiredDate
        self.StockOption =StockOption
        self.StartDate =StartDate
        self.EndDate =EndDate
        self.IdInformationUser = IdInformationUser
    

class usercccd():
    No = ""
    FullName = ""
    DateOfbirth = ""
    PlaceOfBirth = ""
    Address = ""
    IssueOn = ""
    IdInformationUser = ""

    def __init__(self, No, FullName, DateOfbirth, PlaceOfBirth, Address, IssueOn, IdInformationUser):
        self.No = No
        self.FullName = FullName
        self.DateOfbirth = DateOfbirth
        self.PlaceOfBirth = PlaceOfBirth
        self.Address = Address
        self.IssueOn = IssueOn
        self.IdInformationUser = IdInformationUser

