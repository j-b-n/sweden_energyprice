"""This module uses eletrical prices from https://www.elprisetjustnu.se """
import os
import json
from datetime import datetime, timedelta, date, time
import requests
import pytz
from dateutil import parser

def write_to_file(filename, json_object):
    """Write json_object to filename"""
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

def load_file(filename):
    """load filename and return json_object."""
    try:
        with open(filename, 'r', encoding="utf-8") as openfile:
            json_object = json.load(openfile)
    except json.decoder.JSONDecodeError:
        json_object = []
    return json_object

def get_filename_today(foldername, price_zone):
    """get the filename for today"""
    d = datetime.today()
    filename = d.strftime("%m-%d")+"_"+price_zone+".json"
    filename = foldername + filename
    return filename

def clean_folder(foldername, price_zone):
    """Clean the foldername for old files."""
    filename_today = get_filename_today(foldername, price_zone)

    for f in os.listdir(foldername):
        filename = foldername+f
        if os.path.isfile(filename):
            if filename != filename_today:
                #os.remove(filename)
                print(filename)

def update_energy_price(folder, price_zone):
    """Update the energy price for price_zone."""
    #https://www.elprisetjustnu.se/api/v1/prices/2024/08-08_SE3.json

    filename = get_filename_today(folder, price_zone)

    if os.path.exists(filename):
        prices = load_file(filename)
    else:
        clean_folder(folder, price_zone)
        d = datetime.today()
        url = "https://www.elprisetjustnu.se/api/v1/prices/"
        url = url + d.strftime("%Y/%m-%d")
        url = url + "_" + price_zone + ".json"
        response = requests.get(url, timeout=10)
        prices = response.json()
        write_to_file(filename, json.dumps(prices, indent=4, sort_keys=True))

    return prices

def get_min_energy_price(folder, price_zone):
    """ Get the minimum eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    min = 1000000
    for price in prices:
        if price["SEK_per_kWh"] < min:
            min = price["SEK_per_kWh"]
    return min

def get_max_energy_price(folder, price_zone):
    """ Get the maxmimum eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    max = -1000000
    for price in prices:
        if price["SEK_per_kWh"] > max:
            max = price["SEK_per_kWh"]
    return max

def get_avg_energy_price(folder, price_zone):
    """ Get the average eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    avg = 0
    for price in prices:
        avg += price["SEK_per_kWh"]
    return round(avg/24,2)

def get_current_energy_price(folder, price_zone):
    """ Get the current eneregy price!"""

    prices = update_energy_price(folder, price_zone)

    local_timezone = pytz.timezone('CET')
    now = datetime.now(local_timezone)

    for price in prices:
        time_start = parser.parse(price["time_start"])
        time_end = parser.parse(price["time_end"])
        #time_start = datetime.strptime(price["time_start"], "%Y-%m-%dT%H:%M:%S%z")
        #time_end = datetime.strptime(price["time_end"], "%Y-%m-%dT%H:%M:%S%z")

        if time_start <= now < time_end:
            return price["SEK_per_kWh"]
    return 0

def get_hour_energy_price(folder, price_zone, hour):
    """ Get the current eneregy price!"""

    prices = update_energy_price(folder, price_zone)

    tz = pytz.timezone('CET')
    today = date.today()
    hour_datetime =  datetime.combine(today, time())
    hour_datetime = tz.localize(hour_datetime + timedelta(hours=hour))

    for price in prices:
        time_start = parser.parse(price["time_start"])
        time_end = parser.parse(price["time_end"])
        #time_start = datetime.strptime(price["time_start"], "%Y-%m-%dT%H:%M:%S%z")
        #time_end = datetime.strptime(price["time_end"], "%Y-%m-%dT%H:%M:%S%z")
        if time_start <= hour_datetime < time_end:
            return price["SEK_per_kWh"]
    return -1000
