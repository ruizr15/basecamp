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
    coordinates = []
    input = name.replace(" ", "%20")
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=%s&inputtype=textquery&fields=geometry&key=%s" % (input, GMAPSAPIKEY)
    r = requests.get(url)
    data = r.json()
    for item in data["candidates"]:
        coordinates.append(float(item["geometry"]["location"]["lat"]))
        coordinates.append(float(item["geometry"]["location"]["lng"]))
    return coordinates

# Gets icon for a weather forecast
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

# Gets a forecast for a specified number of days at a specified location
def get_forecasts(name, coordinates, days):
    # Instantiate important variables
    lat = str(coordinates[0])
    lng = str(coordinates[1])
    forecast_list = []
    forecast = {}
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']

    # If lat and long are empty, use GMaps to try to resolve
    if (lat == "" or lng == ""):
        coords = get_coordinates(name)
        if len(coords) == 0: 
            return False
        else:
            lat = str(coords[0])
            lng = str(coords[1])

    # Use weather API to turn lat, long into grid
    coordinate_url = "https://api.weather.gov/points/%s,%s" % (lat, lng)
    coordinate_request = requests.get(coordinate_url)
    coordinate_data = coordinate_request.json()
    
    # Check if proper formatting is present
    if ("properties" in coordinate_data):
        gridID = coordinate_data["properties"]["gridId"]
        gridX = str(coordinate_data["properties"]["gridX"])
        gridY = str(coordinate_data["properties"]["gridY"])
    else:
        return False

    # Use grid data to get forecast from weather API
    grid_url = "https://api.weather.gov/gridpoints/%s/%s,%s/forecast" % (gridID, gridX, gridY)
    grid_request = requests.get(grid_url)
    weather_data = grid_request.json()

    # Format incoming data into usable dictionary
    special_case = True
    if "properties" in weather_data:
        if "periods" in weather_data["properties"]:
            for period in weather_data["properties"]["periods"]:
                if (period["name"] in weekdays) or ((special_case) and (period["name"] == "Today" or "Tonight")):
                    if (period["name"] == "Today" or "Tonight"): 
                        special_case = False
                    # Creates a new forecast dict to append to the list, then deletes it
                    forecast = {}
                    forecast["day"] = period["name"]
                    forecast["shortForecast"] = period["shortForecast"]
                    forecast["longForecast"] = period["detailedForecast"]
                    forecast["temperature"] = period["temperature"]
                    forecast["iconUrl"] = weather_icon(period["shortForecast"])
                    forecast_list.append(forecast)
                    del(forecast)
        else:
            return False
    else:
        return False
    if days == "max":
        return forecast_list
    return forecast_list[0:days]

"""
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
    try: return more_data["properties"]["periods"]
    except KeyError:
        return "data unavailable"

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
"""
# Gets next days of the week for a certain number of days of the week
def next_days(duration):
    today_code = datetime.datetime.today().weekday()
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days = []
    for i in range(duration):
        if (today_code + i) > 6:
            today_code -= 7
        days.append(day_list[today_code + i])
    days[0] = "Today"
    return days

"""
# Gets a weather forecast for specified next days of the week
def get_weekday_forecasts(forecast_list, duration):
    days = next_days(duration)
    days[0] = "Today"
    weekday_forecasts = {}
    for day in days:
        working_forecast = {}
        for forecast in forecast_list:
            if forecast["name"] == day:
                working_forecast = forecast
        try: working_forecast["iconUrl"] = weather_icon(working_forecast["shortForecast"])
        except KeyError:
            working_forecast["iconUrl"] = "https://cdn0.iconfinder.com/data/icons/free-daily-icon-set/512/Wrong-256.png"
        weekday_forecasts[day] = working_forecast
    return weekday_forecasts
"""

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
    park_forecasts = {}
    # Pulls NPS list of campsites from user-inputted state
    if request.method == "POST":
        # Formats user input
        park_list.clear()
        state = request.form["state"]
        if state == "00":
            return render_template("parks.html", park_list=[], days=next_days(3))
        # Pulls data from NPS
        endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode="+ str(state) + "&api_key=" + NPSAPIKEY
        req = requests.get(endpoint)
        data = req.json()
        # Error case if NPS data comes back empty
        if data['total'] == "0":
            return render_template("parks.html", park_list=["no parks found"])
        else:
            for park in data['data']:
                forecasts = {}
                forecasts = get_forecasts(park["name"], [park["latitude"], park["longitude"]], 3)
                if forecasts == False:
                    park_forecasts[park["name"]] = "no weather data available"
                else:
                    park_forecasts[park["name"]] = forecasts
                park_list.append(park)
                del(forecasts)
            # Pass data to HTML
            return render_template("parks.html", park_list=park_list, forecasts=park_forecasts, days=next_days(3))
    return render_template("parks.html", park_list=[], days=next_days(3))

@app.route("/park-handler", methods=["GET", "POST"])
def parkHandler():
    if request.method == "POST":
        global park_list
        global selected_park
        global forecasts
        forecasts = []
        # Stores the park chosen by user as global variable
        selected_park = park_list[int(request.form["park_index"])]
        # Gets weather forecast
        forecasts = get_forecasts(selected_park["name"], [selected_park["latitude"], selected_park["longitude"]], 3)
        return redirect("/display")


@app.route("/display")
def display():
    global selected_park

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
    selected_park = selected_park
    forecasts = get_forecasts(selected_park["name"], [selected_park["latitude"], selected_park["longitude"]], "max")

    if forecasts != "no data available":
        weekend_forecast = ""
        for forecast in forecasts:
            if forecast["day"] == "Saturday":
                weekend_forecast = forecast
            elif (weekend_forecast == "" and forecast["day"] == "Sunday"):
                weekend_forecast = forecast

    packingList = {"Clothing": [], "Personal Gear": []}

    temperature = weekend_forecast["temperature"]
    if weekend_forecast["iconUrl"] == "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-30-256.png":
        rainy = True
    else:
        rainy = False
    
    if weekend_forecast["iconUrl"] == "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/sun-256.png":
        clear = True
    else:
        clear = False

    if temperature > 60:
        packingList["Clothing"].append("Shorts")
        packingList["Clothing"].append("T-shirts")
    elif 40 < temperature < 60:
        packingList["Clothing"].append("Long-sleeve shirts")
        packingList["Clothing"].append("Pants")
        packingList["Clothing"].append("Sweater/hoodie")
    elif temperature < 40:
        packingList["Clothing"].append("Long-sleeve shirts")
        packingList["Clothing"].append("Pants")
        packingList["Clothing"].append("Sweater/hoodie")
        packingList["Clothing"].append("Warm hat")
        packingList["Clothing"].append("Gloves/mittens")
        packingList["Clothing"].append("Heavy winter coat")
    if rainy:
        packingList["Clothing"].append("Rain jacket")
        packingList["Clothing"].append("Rain pants")
        packingList["Personal Gear"].append("Pack cover")
    if clear:
        packingList["Clothing"].append("Sunglasses")
        if temperature > 60:
            packingList["Personal Gear"].append("Sunscreen")
    try:
        imgsrc = selected_park["images"][0]["url"]
    except IndexError:
        imgsrc = url_for('static', filename='logo.png')
    return render_template("display.html", parkName=selected_park["name"], parkDescription=selected_park["description"], thingstodo=thingstodo, forecasts=forecasts[0:5], days=next_days(5), packingList=packingList, imgsrc=imgsrc)
