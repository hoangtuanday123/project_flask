import db
from flask_login import current_user,login_user,login_required,logout_user
from flask import Blueprint, flash, redirect, render_template, request, url_for,session

clientmanager = Blueprint("clientmanager", __name__)
@clientmanager.route("/clientmanagerpage")
@login_required
def clientmanagerpage():
    return render_template("client_manager/clientmanagerpage.html",roleuser="client manager")