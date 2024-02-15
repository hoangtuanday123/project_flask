import pyodbc

def connection():
    s = 'DESKTOP-KEFRDN4' #Your server name 
    d = 'project_flask' 
    u = '' #Your login
    p = '' #Your login password
    cstr = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={s};DATABASE={d};Trusted_Connection=yes;'
    conn = pyodbc.connect(cstr)
    return conn

