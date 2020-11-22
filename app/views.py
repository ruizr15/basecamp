from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
import json, requests

global park_list
park_list = []
global selected_park
selected_park = {}
NPSAPIKEY = "***REMOVED***"

@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/login")

@app.route("/login")
def login():
    if request.method == "POST":
        return redirect("/coordinates")
    return render_template("login.html")

@app.route("/coordinates", methods=["GET", "POST"])
def coordinates():
    return render_template("coordinates.html")

@app.route("/weather", methods=["GET", "POST"])
def weather():
    forecast_today = "Today's weather: "
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


@app.route("/parks", methods=["GET", "POST"])
def parks():
    global park_list
    # Pulls NPS list of campsites from user-inputted state
    if request.method == "POST":
        # Formats user input
        park_list.clear()
        state = request.form["state"]
        if state == "00":
            return render_template("parks.html", park_list=[])
        # Pulls data from NPS
        endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode="+ str(state) + "&api_key=" + NPSAPIKEY
        req = requests.get(endpoint)
        data = req.json()
        # Error case if NPS data comes back empty
        if data['total'] == "0":
            return render_template("parks.html", park_list=["no parks found"])
        for park in data['data']:
            park_list.append(park)
        # Pass data to HTML
        return render_template("parks.html", park_list=park_list)
    return render_template("parks.html", park_list=[])

@app.route("/park-handler", methods=["GET", "POST"])
def parkHandler():
    if request.method == "POST":
        global selected_park
        selected_park = park_list[int(request.form["park_index"])]
        return redirect("/")

@app.route("/display")
def display():
    return render_template("display.html")