import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session

accountmanager = Blueprint("accountmanager", __name__)
@accountmanager.route("/accountmanager")
@login_required
def accountmanagerpage():
    return render_template("account_manager/accountmanagerpage.html",roleuser="account manager")