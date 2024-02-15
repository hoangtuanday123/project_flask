import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session

employeemanager = Blueprint("employeemanager", __name__)
@employeemanager.route("/employeemanagerpage")
@login_required
def employeemanagerpage():
    return render_template("employee_manager/employeemanagerpage.html",roleuser="employee manager")