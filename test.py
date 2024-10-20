"""Test elprisetjustnu.py!"""
from pathlib import Path
import elprisetjustnu

PRICE_ZONE = "SE3"
FOLDER = "./json/"
Path(FOLDER).mkdir(parents=True, exist_ok=True)

current_price = elprisetjustnu.get_current_energy_price(FOLDER, PRICE_ZONE)
min_price = elprisetjustnu.get_min_energy_price(FOLDER, PRICE_ZONE)
max_price = elprisetjustnu.get_max_energy_price(FOLDER, PRICE_ZONE)
avg_price = elprisetjustnu.get_avg_energy_price(FOLDER, PRICE_ZONE)

print("Current price is" , current_price,'kr', str(round(current_price*100,4)), 'öre')
print("Minimum price is" , min_price,'kr', str(round(min_price*100,4)), 'öre')
print("Maximum price is" , max_price,'kr', str(round(max_price*100,4)), 'öre')
print("Average price is" , avg_price,'kr', str(round(avg_price*100,4)), 'öre')

for hour in range(24):
    hour_price = elprisetjustnu.get_hour_energy_price(FOLDER, PRICE_ZONE, hour)
    print("Hour-"+str(hour),str(round(hour_price,2)),'kr', str(round(hour_price*100,2)), 'öre')
