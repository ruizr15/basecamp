from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
import json, requests

global park_list
park_list = []

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("stateButton"):
            state=request.form["state"]
            if state != "":
                endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode="+ str(state) + "&api_key=***REMOVED***"
                HEADERS = {"Authorization": "***REMOVED***"}
                req = requests.get(endpoint)
                return render_template("index.html", info=req.text)
            else:
                return render_template("index.html", info="Input your state to begin")
        elif request.form.get("coordinatesButton"):
            return redirect("/coordinates")
    else:
        return render_template("index.html", info="Input your state to begin")



@app.route("/login")
def login():
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
    if request.method == "POST":
        park_list.clear()
        state = request.form["state"]
        if state == "00":
            return render_template("parks.html", park_list=[])
        endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode="+ str(state) + "&api_key=***REMOVED***"
        HEADERS = {"Authorization": "***REMOVED***"}
        req = requests.get(endpoint)
        data = req.json()
        if data['total'] == "0":
            return render_template("parks.html", park_list=["no parks found"])
        for park in data['data']:
            park_list.append(park['name'])
        return render_template("parks.html", park_list=park_list)
    return render_template("parks.html", park_list=[])