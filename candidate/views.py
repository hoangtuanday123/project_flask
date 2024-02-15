import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session
import pyotp
from __init__ import file_path_default
candidate = Blueprint("candidate", __name__)
@candidate.route("/candidate/<image_path>/<fullname>")
@login_required
def candidatepage(image_path, fullname):
    return render_template("candidate/candidatepage.html",roleuser="candidate",image_path=image_path,fullname=fullname)
