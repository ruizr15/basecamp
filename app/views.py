from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
import json, requests


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("stateButton"):
            state=request.form["state"]
            if state != "":
                endpoint = "https://developer.nps.gov/api/v1/campgrounds?stateCode="+ str(state) + "&api_key=obuJbz67KmzxqsJAANbZ7Aem40o9jXusUJwtuHwe"
                HEADERS = {"Authorization": "obuJbz67KmzxqsJAANbZ7Aem40o9jXusUJwtuHwe"}
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
    if request.method == "POST":
        lat = request.form["latitude"]
        lon = request.form["longitude"]
        r = requests.get('https://api.weather.gov/points/32.8427,-83.9577')
        return jsonify(r.json())


@app.route("/get", methods=["POST"])
def test():
    r = requests.get('https://api.weather.gov/points/32.8427,-83.9577')
    return jsonify(r.json())

