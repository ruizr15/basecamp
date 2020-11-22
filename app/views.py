from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
import datetime
import json, requests

NPSAPIKEY = "***REMOVED***"
GMAPSAPIKEY = "***REMOVED***"

global park_list
global selected_park
global forecasts

park_list = []
selected_park = {}
forecasts = []

# Returns latitude and longitude of a place
def get_coordinates(name):
    input = name.replace(" ", "%20")
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=%s&inputtype=textquery&fields=geometry&key=%s" % (input, GMAPSAPIKEY)
    r = requests.get(url)
    data = r.json()
    for item in data["candidates"]:
        for m in item:

# Returns list of weather forecasts for given coordinates
def get_forecasts(latitude, longitude):
    # Pulls data from weather API to convert coordinates to grid
    url = "https://api.weather.gov/points/" + latitude + "," + longitude
    r = requests.get(url)
    data = r.json()
    gridID = data["properties"]["gridId"]
    gridX = str(data["properties"]["gridX"])
    gridY = str(data["properties"]["gridY"])
    # Uses grid coordinates to get forecasts
    url2 = "https://api.weather.gov/gridpoints/"+gridID+"/"+gridX+","+gridY+"/forecast"
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
        if (word == "sunny" or word == "clear"):
            return "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/sun-256.png"
        if word == "snow":
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-24-256.png"
        if (word == "thunder" or word == "lightning" or word == "thunderstorm"):
            return "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/flash-cloud-256.png"
        if word == "unavailable":
            return "https://cdn0.iconfinder.com/data/icons/free-daily-icon-set/512/Wrong-256.png"

# Gets next days of the week for a certain number of days of the week
def next_days(duration):
    today_code = datetime.datetime.today().weekday()
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days = []
    for i in range(duration):
        if (today_code + i) > 6:
            today_code -= 7
        days.append(day_list[today_code + i])
    return days

# Gets a weather forecast for specified next days of the week
def get_weekday_forecasts(forecast_list, duration):
    days = next_days(duration)
    weekday_forecasts = {}
    for day in days:
        working_forecast = {}
        for forecast in forecast_list:
            if forecast["name"] == day:
                working_forecast = forecast
        working_forecast["iconUrl"] = weather_icon(working_forecast["shortForecast"])
        weekday_forecasts[day] = working_forecast
    return weekday_forecasts


@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/login")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        print("successfully logged in")
        return redirect("/parks")
    return render_template("login.html")

@app.route("/parks", methods=["GET", "POST"])
def parks():
    global park_list
    forecast_dict = {}
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
        else:
            for park in data['data']:
                next_forecasts = []
                print("")
                park_list.append(park)
                lat = str(park["latitude"])
                lon = str(park["longitude"])
                print(park["name"])
                if (lat == "" or lon == ""):
                    forecast_dict[park["name"]] = {}
                else:
                    forecasts = get_forecasts(lat, lon)
                    next_forecasts = get_weekday_forecasts(forecasts, 3)
                    forecast_dict[park["name"]] = next_forecasts
                    for day in forecast_dict[park["name"]]:
                        print (day + ": " + forecast_dict[park["name"]][day]["shortForecast"])
            # Pass data to HTML
            return render_template("parks.html", park_list=park_list, forecasts=forecast_dict)
    return render_template("parks.html", park_list=[])

@app.route("/park-handler", methods=["GET", "POST"])
def parkHandler():
    if request.method == "POST":
        global park_list
        global selected_park
        global forecasts
        forecasts = []
        # Stores the park chosen by user as global variable
        selected_park = park_list[int(request.form["park_index"])]
        lat = str(selected_park["latitude"])
        lon = str(selected_park["longitude"])
        if (lat == "" or lon == ""):
            forecasts = ["no data available"]
            return redirect("/display")
        # Gets weather forecast
        forecasts = get_forecasts(lat, lon)
        return redirect("/display")

@app.route("/display")
def display():
    global forecasts
    if forecasts[0] != "no data available":
        next_forecasts = get_weekday_forecasts(forecasts, 3)
        return render_template("display.html", forecasts=next_forecasts)

@app.route("/testing")
def testing():
    get_coordinates("Brickhill Bluff Wilderness Campsite")
    return "hello"