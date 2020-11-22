import datetime

from app import app
from flask import render_template, request, redirect

import requests

NPSAPIKEY = "***REMOVED***"

global park_list
global selected_park
global forecasts

park_list = []
selected_park = {}
forecasts = []


# Returns list of weather forecasts for given coordinates
def get_forecasts(latitude, longitude):
    # Pulls data from weather API to convert coordinates to grid
    url = "https://api.weather.gov/points/" + latitude + "," + longitude
    r = requests.get(url)
    data = r.json()
    gridID = data["properties"]["gridId"]
    gridX = data["properties"]["gridX"]
    gridY = data["properties"]["gridY"]
    # Uses grid coordinates to get forecasts
    url2 = "https://api.weather.gov/gridpoints/" + gridID + "/" + str(gridX) + "," + str(gridY) + "/forecast"
    v = requests.get(url2)
    more_data = v.json()
    return more_data["properties"]["periods"]


# Returns url for weather icon for a given forecast string
def weather_icon(forecast):
    for word in forecast.split():
        word = word.lower()
        if word == "cloudy":
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-22-256.png"
        if word == "rain":
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-30-256.png"
        if word == "sunny" or word == "clear":
            return "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/sun-256.png"
        if word == "snow":
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-24-256.png"
        if word == "thunder" or word == "lightning" or word == "thunderstorm":
            return "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/flash-cloud-256.png"
        else:
            print(word)


# Gets next days of the week for a certain number of days of the week
def next_days(duration):
    today = datetime.datetime.today().weekday()


@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        return redirect("/parks")
    return render_template("login.html")


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
        endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode=" + str(state) + "&api_key=" + NPSAPIKEY
        req = requests.get(endpoint)
        data = req.json()
        # Error case if NPS data comes back empty
        if data['total'] == "0":
            return render_template("parks.html", park_list=["no parks found"])
        for park in data['data']:
            park_list.append(park)

            # Generate forecast for next three days

        # Pass data to HTML
        return render_template("parks.html", park_list=park_list)
    return render_template("parks.html", park_list=[])


@app.route("/park-handler", methods=["GET", "POST"])
def parkHandler():
    if request.method == "POST":
        global selected_park
        global forecasts
        # Stores the park chosen by user as global variable
        selected_park = park_list[int(request.form["park_index"])]
        lat = str(selected_park["latitude"])
        lon = str(selected_park["longitude"])
        if lat == "" or lon == "":
            forecasts = ["no data available"]
            return redirect("/display")
        # Gets weather forecast
        forecasts = get_forecasts(lat, lon)
        return redirect("/display")


@app.route("/display")
def display():
    # max number of things that will be displayed in the activities tab
    maxItems = 5
    # get a list of things to do for the selected park
    endpoint = "https://developer.nps.gov/api/v1/thingstodo?parkCode=" + selected_park["parkCode"] + "&limit=" + str(
        maxItems) + "&api_key=" + NPSAPIKEY
    req = requests.get(endpoint)
    data = req.json()
    thingstodo = []
    # if there are no listed activities, say so
    if data['total'] == "0":
        thingstodo=["No activities listed at this location"]
    # otherwise make a list of things to do and send relevant data to html
    else:
        for thing in data['data']:
            thingstodo.append(thing)
    # stuff for weather icons
    global forecasts
    icon_urls = []
    if forecasts[0] != "no data available":
        for forecast in forecasts:
            icon_urls.append(weather_icon(forecast['shortForecast']))
    return render_template("display.html", parkName=selected_park["name"],
                           parkDescription=selected_park["description"], thingstodo=thingstodo, forecasts=forecasts, icon_urls=icon_urls)
