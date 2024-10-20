import elprisetjustnu
from datetime import datetime, timedelta

price_zone = "SE3"
folder = "./json/"

current_price = elprisetjustnu.get_current_energy_price(folder, price_zone)
min_price = elprisetjustnu.get_min_energy_price(folder, price_zone)
max_price = elprisetjustnu.get_max_energy_price(folder, price_zone)
avg_price = elprisetjustnu.get_avg_energy_price(folder, price_zone)

print("Current price is" , current_price)
print("Minimum price is" , min_price)
print("Maximum price is" , max_price)
print("Average price is" , avg_price)

for hour in range(24):
    hour_price = elprisetjustnu.get_hour_energy_price(folder, price_zone, hour)
    print("Hour-"+str(hour)+" "+str(round(hour_price,2)))
