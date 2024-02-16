from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired
import pickle
import os.path
import io
import shutil
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse, parse_qs

class uploadFile(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Upload File')

class EmployeeRelativeForm(FlaskForm):
    Relationship = StringField('Enter Relationship', validators=[
                      InputRequired()])
    phone = StringField('Enter phone', validators=[
                      InputRequired()])
    email = StringField('Enter email')
    contactaddress=StringField('Enter contactaddress', validators=[
                      InputRequired()])
    career=StringField('Enter career', validators=[
                      InputRequired()])
    citizenIdentificationNo=StringField('Enter citizenIdentificationNo', validators=[
                      InputRequired()])
    fullname=StringField('Enter fullname', validators=[
                      InputRequired()])
    dateofbirth=DateTimeField('Enter date of birth (year/month/day)', format='%Y/%m/%d', validators=[DataRequired()])
    placeofbirth=StringField('Enter placeofbirth', validators=[
                      InputRequired()])
    address=StringField('Enter address', validators=[
                      InputRequired()])
    issued=DateTimeField('enter issued (year/month/day)', format='%Y/%m/%d', validators=[DataRequired()])

class laborcontractForm(FlaskForm):
    
    Laborcontracttype = StringField('Enter Laborcontracttype', validators=[
                      InputRequired()])
    Laborcontractterm=StringField('Enter Laborcontractterm', validators=[
                      InputRequired()])
    Commencementdate=DateTimeField('Enter Commencementdate (year/month/day)', format='%Y/%m/%d', validators=[DataRequired()])
    Position=StringField('Enter Position', validators=[
                      InputRequired()])
    Employeelevel=StringField('Enter Employeelevel', validators=[
                      InputRequired()])

class forexsalaryForm(FlaskForm):
    forextype=StringField('Enter forextype', validators=[
                      InputRequired()])
    Annualsalary = StringField('Enter Annualsalary', validators=[
                      InputRequired()])
    Monthlysalary = StringField('Enter Monthlysalary', validators=[
                      InputRequired()])
    Monthlysalaryincontract = StringField('Enter Monthlysalaryincontract', validators=[
                      InputRequired()])
    Quaterlybonustarget = StringField('Enter Quaterlybonustarget', validators=[
                      InputRequired()])
    Annualbonustarget = StringField('Enter Annualbonustarget', validators=[
                      InputRequired()])
class DriveAPI:
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    file_id = ""

    def __init__(self):
        """Initialize the DriveAPI instance."""
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

        # Request a list of first N files or folders with name and id from the API.
        # results = self.service.files().list(pageSize=100, fields="files(id, name)").execute()
        # self.files = results.get('files', [])

    def authenticate(self):
        """Authenticate and authorize the user."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        # It is created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials are available, request the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def print_files(self):
        """Print a list of files."""
        print("Here's a list of files:")
        for file in self.files:
            print(f"File Name: {file['name']}, File ID: {file['id']}")

    def download_file(self, file_id, file_name):
        """Download a file from Google Drive."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        # Initialize a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)

            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)

            print("File Downloaded")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def upload_file(self, filepath):
        """Upload a file to Google Drive."""
        global file_id
        # Extract the file name out of the file path
        name = os.path.basename(filepath)

        # Find the MimeType of the file
        mime_type, _ = MimeTypes().guess_type(name)
        mime_type = mime_type or 'application/octet-stream'

        # Create file metadata
        file_metadata = {'name': name}

        media = MediaFileUpload(filepath, mimetype=mime_type)

        try:
            # Create a new file in the Drive storage
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file['id']
            print(f"File uploaded. File ID: {file['id']}")
        except Exception as e:
            print(f"Error: {e}")

    def get_link_file_url(self):
        global file_id
        print("file id is:" + file_id)
        file_url = self.service.files().get(fileId=file_id, fields="webContentLink").execute()
        # # Find the index of ':' and '}'
        # start_index = file_url.find(':') + 1
        # end_index = file_url.rfind('}')
        # file_url=file_url[start_index:end_index].strip()
        return file_url
