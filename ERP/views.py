import db
from flask_login import current_user,login_required
from flask import Blueprint, flash, redirect, render_template, request, url_for,session
from config import Config
from datetime import datetime, timedelta

ERP = Blueprint("ERP", __name__)

def calendar(year):
    year=int(year)
    start_date = datetime(year, 1, 1)
    weeks_in_year = []

    while start_date.year == year:
        start_of_week = start_date - timedelta(days=start_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        weeks_in_year.append({
            "week_number": start_date.isocalendar()[1],
            "start_of_week": start_of_week.strftime("%Y-%m-%d"),
            "end_of_week": end_of_week.strftime("%Y-%m-%d"),
            "week_dates": week_dates
        })

        start_date += timedelta(days=7)
    return weeks_in_year

@ERP.route("/WeeklyTimesheet",methods=['GET','POST'])
def weeklytimesheet():
    current_datetime = datetime.now()
    year=current_datetime.year
    if request.method=='POST' and request.form.get('yearform')=='yearform':
        year=request.form['year']
    weeks_in_year=calendar(year)
    
    return render_template("ERP/WeeklyTimesheet.html",weeks_in_year=weeks_in_year,year=year)

# from fastapi import Header, APIRouter,HTTPException,Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.templating import Jinja2Templates
# from datetime import datetime, timedelta
# ERP=APIRouter()
# templates = Jinja2Templates(directory="templates")
# @ERP.get("/calendar/{year}", response_class=HTMLResponse)
# async def calendar(request: Request, year: int):
#     try:
#         start_date = datetime(year, 1, 1)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid year")

#     weeks_in_year = []

#     while start_date.year == year:
#         start_of_week = start_date - timedelta(days=start_date.weekday())
#         end_of_week = start_of_week + timedelta(days=6)
#         week_dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

#         weeks_in_year.append({
#             "week_number": start_date.isocalendar()[1],
#             "start_of_week": start_of_week.strftime("%Y-%m-%d"),
#             "end_of_week": end_of_week.strftime("%Y-%m-%d"),
#             "week_dates": week_dates
#         })

#         start_date += timedelta(days=7)
    
#     return templates.TemplateResponse("calender.html", {"request": request, "year": year, "weeks_in_year": weeks_in_year})
