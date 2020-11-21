from app import app
from flask import render_template, request, redirect, url_for, flash
import requests
#import urllib.request
import json

@app.route("/")
def index():
    return redirect("/coordinates")
    # return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/coordinates", methods=["GET", "POST"])
def coordinates():
    return render_template("coordinates.html")

@app.route("/weather", methods=["GET", "POST"])
def weather():
    forecast_today = "today's weather: "
    if request.method == "POST":
        lat = request.form["latitude"]
        lon = request.form["longitude"]
        url = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
        r = requests.get(url)
        data = r.json()
        gridID = data['properties']['gridId']
        gridX = data['properties']['gridX']
        gridY = data['properties']['gridY']
        url2 = "https://api.weather.gov/gridpoints/"+gridID+"/"+str(gridX)+","+str(gridY)+"/forecast"
        v = requests.get(url2)
        more_data = v.json()
        forecast_today += more_data['properties']['periods'][0]['shortForecast']
        return forecast_today


@app.route("/json", methods=["POST"])
def json():
    req = request.get_json()
