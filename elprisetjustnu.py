"""This module uses electrical prices from https://www.elprisetjustnu.se """
from datetime import date, datetime, time, timedelta
import json
import logging
import os
from pathlib import Path

from dateutil import parser
import pytz
import requests

# library logger
logger = logging.getLogger(__name__)

def write_to_file(filename, json_object):
    """Write json_object to filename"""
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)
    os.chmod(filename, 0o644)

def load_file(filename):
    """load filename and return json_object."""
    try:
        with open(filename, 'r', encoding="utf-8") as openfile:
            json_object = json.load(openfile)
    except json.decoder.JSONDecodeError:
        logger.exception("Malformed json in %s", filename)
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
    try:
        for f in os.listdir(foldername):
            filename = os.path.join(foldername, f)
            try:
                if os.path.isfile(filename) and filename != filename_today:
                    os.remove(filename)
            except PermissionError:
                logger.warning("No permission to remove file %s", filename)
            except OSError:
                logger.exception("Failed to remove file %s", filename)
    except FileNotFoundError:
        # folder does not exist - nothing to clean
        return
    except PermissionError:
        logger.warning("No permission to list folder %s", foldername)
        return

def update_energy_price(folder, price_zone):
    """Update the energy price for price_zone."""
    #https://www.elprisetjustnu.se/api/v1/prices/2024/08-08_SE3.json

    filename = get_filename_today(folder, price_zone)

    Path(folder).mkdir(parents=True, exist_ok=True)

    if os.path.exists(filename):
        prices = load_file(filename)
    else:
        clean_folder(folder, price_zone)
        d = datetime.today()
        url = "https://www.elprisetjustnu.se/api/v1/prices/"
        url = url + d.strftime("%Y/%m-%d")
        url = url + "_" + price_zone + ".json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            prices = response.json()
            # write the raw response to file
            try:
                write_to_file(filename, json.dumps(prices, indent=4, sort_keys=True))
            except (PermissionError, OSError):
                logger.warning("Unable to write prices to %s", filename)
        except requests.RequestException:
            logger.exception("Failed to fetch prices from %s", url)
            prices = []
        except ValueError:
            logger.exception("Failed to parse JSON from %s", url)
            prices = []

    return prices

def get_min_energy_price(folder, price_zone):
    """ Get the minimum eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    if not prices:
        return 0
    _min = min((p.get("SEK_per_kWh", 0) for p in prices))
    return _min

def get_max_energy_price(folder, price_zone):
    """ Get the maxmimum eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    if not prices:
        return 0
    _max = max((p.get("SEK_per_kWh", 0) for p in prices))
    return _max

def get_avg_energy_price(folder, price_zone):
    """ Get the average eneregy price!"""
    prices = update_energy_price(folder, price_zone)
    if not prices:
        return 0
    total = sum((p.get("SEK_per_kWh", 0) for p in prices))
    count = len(prices)
    # if API returns fewer than 24 entries, divide by actual count
    return round(total / count, 2) if count else 0

def get_current_energy_price(folder, price_zone):
    """ Get the current eneregy price!"""

    prices = update_energy_price(folder, price_zone)
    if not prices:
        return 0

    # Prefer timezone-aware datetimes from the API entries; fall back to Swedish time
    now = datetime.now(pytz.timezone('Europe/Stockholm'))

    for price in prices:
        try:
            time_start = parser.parse(price["time_start"])
            time_end = parser.parse(price["time_end"])
        except (ValueError, TypeError):
            logger.exception("Failed to parse time range for price entry: %s", price)
            continue

        # ensure both are timezone-aware
        if time_start.tzinfo is None:
            time_start = pytz.timezone('Europe/Stockholm').localize(time_start)
        if time_end.tzinfo is None:
            time_end = pytz.timezone('Europe/Stockholm').localize(time_end)

        if time_start <= now < time_end:
            logger.debug(
                "Current time: %s, start: %s, end: %s, price: %s",
                now,
                time_start,
                time_end,
                price.get("SEK_per_kWh"),
            )
            return price.get("SEK_per_kWh", 0)
    return 0

def get_hour_energy_price(folder, price_zone, hour):
    """ Get the current eneregy price!"""

    prices = update_energy_price(folder, price_zone)

    if not prices:
        return 0

    tz = pytz.timezone('Europe/Stockholm')
    today = date.today()
    hour_datetime = datetime.combine(today, time()) + timedelta(hours=hour)
    hour_datetime = tz.localize(hour_datetime)

    for price in prices:
        try:
            time_start = parser.parse(price["time_start"])
            time_end = parser.parse(price["time_end"])
        except (ValueError, TypeError):
            logger.exception("Failed to parse time range for price entry: %s", price)
            continue

        if time_start.tzinfo is None:
            time_start = tz.localize(time_start)
        if time_end.tzinfo is None:
            time_end = tz.localize(time_end)

        if time_start <= hour_datetime < time_end:
            return price.get("SEK_per_kWh", 0)
    return 0
