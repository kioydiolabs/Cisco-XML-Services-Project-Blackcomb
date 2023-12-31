from flask import Flask, request, jsonify, Response
import requests
import random
import openmeteo_requests
import requests_cache
import pandas as pd
import time
from retry_requests import retry
from unidecode import unidecode

app = Flask(__name__)

ipaddr = "XXX.XXX.XXX.XXX"
# Replace the XXX.XXX.XXX.XXX above with the ipv4 adress of the server you are deplying CXSPBPR.
stock_apikey = "XXXXXXXXXXXXXXXX"
# Replace the XXXXXXXXXXXXXXXX above with your Alpha Vantage API key. For help check GitHub repo or ask on Discord Server. Help articles coming soon.

@app.route("/stock-price/")
def get_stock():
    nsymb = request.args.get("symbol")
    out = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={nsymb}&apikey={stock_apikey}")
    out = out.json()
    # out = "{'Global Quote': {'01. symbol': 'MSFT', '02. open': '371.0400', '03. high': '371.9500', '04. low': '367.3454', '05. price': '370.2700', '06. volume': '26816841', '07. latest trading day': '2023-11-14', '08. previous close': '366.6800', '09. change': '-3.5900', '10. change percent': '0.9791%'}}"
    # out = ast.literal_eval(out)
    # print(out)
    price = round(float(out['Global Quote']['05. price']),2)
    change = round(float(out['Global Quote']['09. change']),2)
    change_percent = out['Global Quote']['10. change percent']
    # print(type(price))

    # print(price)

    if change > 0:
        up_or_down = "UP ^"
    else:
        up_or_down = "DOWN"

    output = f"<CiscoIPPhoneText>\n"
    output += f"<Title>Stock value for {nsymb.upper()}</Title>\n"
    output += f"<Text>\n"
    output += f"Symbol : {nsymb.upper()}\n"
    output += f"Value : {price}$\n"
    output += f"Change : {change}$ ({up_or_down})\n"
    output += f"Change (%) : {change_percent}\n"
    output += f"</Text>\n"
    output += f"</CiscoIPPhoneText>"

    return Response(output, mimetype='text/xml')


@app.route("/geocode-aqi/")
def geocode_aqi():
    name = request.args.get("name").upper()
    out = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=10&language=en&format=json")
    out = out.json()
    print(out)
    cities_data = out['results']
    city_info_list = [{'name': city['name'], 'admin1': city.get('admin1', ''), 'latitude': city['latitude'],
                       'longitude': city['longitude'], 'country_code': city['country_code']} for city in cities_data]

    # Print the result
    for city_info in city_info_list:
        print(
            f"{city_info['name']}, {city_info['admin1']}, {city_info['latitude']}, {city_info['longitude']}, {city_info['country_code']}")

    output = f"<CiscoIPPhoneMenu>\n"
    output += f"<Title>Results for your search</Title>\n"
    for city_info in city_info_list:
        city_name = city_info['name'].replace(" ", "_")
        city_name = unidecode(city_name)
        city_region = city_info['admin1'].replace(" ", "_")
        output += f"<MenuItem>"
        output += f"  <Name>{city_name}, {city_info['admin1']}, {city_info['country_code']}</Name>"
        output += f"  <URL>http://{ipaddr}:5000/air-quality/?latitude={city_info['latitude']}&amp;longtitude={city_info['longitude']}&amp;name={city_name}&amp;region={city_region}&amp;country={city_info['country_code']}</URL>"
        output += f"</MenuItem>"
    output += f"</CiscoIPPhoneMenu>"

    return Response(output, mimetype='text/xml')
    # return out, 200


@app.route("/geocode-weather/")
def geocode_weather():
    name = request.args.get("name").upper()
    out = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=10&language=en&format=json")
    out = out.json()
    print(out)
    cities_data = out['results']
    city_info_list = [{'name': city['name'], 'admin1': city.get('admin1', ''), 'latitude': city['latitude'],
                       'longitude': city['longitude'], 'country_code': city['country_code']} for city in cities_data]

    # Print the result
    for city_info in city_info_list:
        print(
            f"{city_info['name']}, {city_info['admin1']}, {city_info['latitude']}, {city_info['longitude']}, {city_info['country_code']}")

    output = f"<CiscoIPPhoneMenu>\n"
    output += f"<Title>Results for your search</Title>\n"
    for city_info in city_info_list:
        city_name = city_info['name'].replace(" ", "_")
        city_name = unidecode(city_name)
        city_region = city_info['admin1'].replace(" ", "_")
        output += f"<MenuItem>"
        output += f"  <Name>{city_name}, {city_info['admin1']}, {city_info['country_code']}</Name>"
        output += f"  <URL>http://{ipaddr}:5000/weather/?latitude={city_info['latitude']}&amp;longtitude={city_info['longitude']}&amp;name={city_name}&amp;region={city_region}&amp;country={city_info['country_code']}</URL>"
        output += f"</MenuItem>"
    output += f"</CiscoIPPhoneMenu>"

    return Response(output, mimetype='text/xml')
    # return out, 200


@app.route("/air-quality/")
def get_air_quality():    
    latitude = float(request.args.get("latitude"))
    longtitude = float(request.args.get("longtitude"))
    name = request.args.get("name").replace("_", " ")
    region = request.args.get("region").replace("_", " ")
    country = request.args.get("country")
    out = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longtitude}&current=us_aqi,dust")
    out = out.json()
    print(out)
    current = out['current']

    dust = current['dust']
    air_quality = current['us_aqi']

    print(dust)
    print(air_quality)

    output = f"<CiscoIPPhoneText>\n"
    output += f"<Title>Air Quality</Title>\n"
    output += f"<Text>\n"
    output += f"{name}, {region}, {country}\n\n"
    output += f"Dust : {dust}\n"
    output += f"Air Quality (US AQI) : {air_quality}"
    output += f"</Text>\n"
    output += f"</CiscoIPPhoneText>"


    return Response(output, mimetype='text/xml')
    # return out, 200


@app.route("/weather/")
def weather():
    latitude = float(request.args.get("latitude"))
    longtitude = float(request.args.get("longtitude"))
    name = request.args.get("name").replace("_", " ")
    region = request.args.get("region").replace("_", " ")
    country = request.args.get("country")
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
		"latitude": latitude,
		"longitude": longtitude,
		"current": ["temperature_2m", "precipitation", "wind_speed_10m", "wind_gusts_10m", "relative_humidity_2m"],
		"hourly": ["temperature_2m", "precipitation_probability", "precipitation", "wind_speed_10m", "wind_gusts_10m"],
		"wind_speed_unit": "ms",
		"timezone": "auto",
		"forecast_days": 1
	}
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()
    current_wind_speed_10m = current.Variables(2).Value()
    current_wind_gusts_10m = current.Variables(3).Value()
    current_relative_humidity_2m = current.Variables(4).Value()


    xml = f"<CiscoIPPhoneText>\n"
    xml += "<Title>Current Weather</Title>\n"
    xml += "<Text>\n"
    xml += f"{name}, {region}, {country}\n\n"
    xml += f"Temperature : {round(current_temperature_2m, 2)}C\n"
    xml += f"Precipitation : {current_precipitation}mm\n"
    xml += f"Wind speed : {round(current_wind_speed_10m, 2)}m/s\n"
    xml += f"Wind gusts : {round(current_wind_gusts_10m, 2)}m/s\n"
    xml += f"Humidity : {round(current_relative_humidity_2m, 2)}%\n"
    xml += f"</Text>\n"
    xml += f"</CiscoIPPhoneText>"

    return Response(xml, mimetype='text/xml')


@app.route("/rps/")
def rock_paper_scissors():
    user_input = request.args.get("user_input")
    global computer

    possible = ['rock','paper','scissors']
    computer = random.choice(possible)
    print(computer)

    if user_input == 'rock' and computer == 'paper':
        output = f"{computer}\n"
        output += "You loose!"
        return output, 200
    elif user_input == 'rock' and computer == 'scissors':
        output = f"{computer}\n"
        output += "You win!"
        return output, 200
    elif user_input == 'rock' and computer == 'rock':
        output = f"{computer}\n"
        output += "Tie"
        return output, 200
    elif user_input == 'paper' and computer == 'rock':
        output = f"{computer}\n"
        output += "You win!"
        return output, 200
    elif user_input == 'paper' and computer == 'scissors':
        output = f"{computer}\n"
        output += "You loose!"
        return output, 200
    elif user_input == 'paper' and computer == 'paper':
        output = f"{computer}\n"
        output += "Tie"
        return output, 200
    elif user_input == 'scissors' and computer == 'rock':
        output = f"{computer}\n"
        output += "You loose!"
        return output, 200
    elif user_input == 'scissors' and computer == 'paper':
        output = f"{computer}\n"
        output += "You win"
        return output, 200
    if user_input == 'scissors' and computer == 'scissors':
        output = f"{computer}\n"
        output += "Tie"
        return output, 200

    return 'knag', 200


@app.route("/stop-arrivals/")
def get_stop_arrivals():    
    stop = request.args.get("stop")
    
    
    # Pull data from OASA API for stop arrivals and format them in JSON
    data = requests.get(f"http://telematics.oasa.gr/api/?act=getStopArrivals&p1={stop}")
    final = data.json()

    # Extract only the "btime2" values from the api response
    try:
        btime2_values = [entry['btime2'] for entry in final]

        xml = f"<CiscoIPPhoneText>\n"
        xml += f"<Title>Arrivals for {stop}</Title>\n"
        xml += f"<Text>\n"
        for i in btime2_values:
            xml += f"{i} minutes\n"
        xml += f"</Text>\n"
        xml += f"</CiscoIPPhoneText>"
    except:
        xml = f"<CiscoIPPhoneText>\n"
        xml += f"<Title>Arrivals for {stop}</Title>\n"
        xml += f"<Text>No arrivals</Text>\n"
        xml += f"</CiscoIPPhoneText>"


    return Response(xml, mimetype='text/xml')
    # return out, 200


    return Response(xml, mimetype='text/xml')
    # return out, 200



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



# KIOYDIOLABS.org
# Stratos Thivaios
# admin@kioydiolabs.org
# developers@kioydiolabs.org
# 2023
# Build 9300
# Released on : Nov. 16 2023
# License : MIT
# GitHub Repository : https://github.com/kioydiolabs/Cisco-XML-Services-Project-Blackcomb

# To install required libraries run the following command in the terminal
#   > pip install flask requests openmeteo_requests requests_cache pandas retry_requests unidecode -y
#   (obviously wihtout the ">")

# Notice : The Geocoding, Air Quality, and Weather tools use the Open Meteo API. If you are
#   to use in a corporate environment, you will have to create your own API key and pay accordingly.
#   You can only use the API endpoints without an API key for personal purposes.
#   In short : get an OpenMeteo API key if you are using this in a company
heh
#test