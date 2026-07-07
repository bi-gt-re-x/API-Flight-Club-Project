from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager

data = DataManager()
flight_search = FlightSearch()
flight_data = FlightData()
notifier = NotificationManager()

sheet_data = data.prices
x_check = 0
y_check = 0

cheapest_price = 67
iata = "LAX"

users_data = data.get_customer_emails()

for x_check, item in enumerate(sheet_data["prices"]):

    iata = sheet_data["prices"][x_check]["iataCode"]

    if not iata or iata == "TESTING":
        city = sheet_data["prices"][x_check]["city"]
        flight_search.check_iata(iata, sheet_data, x_check)
        data.update_docs(sheet_data, x_check)
        iata = sheet_data["prices"][x_check]["iataCode"]

    token = flight_search.token
    flight_information = flight_data.find_cheapest_flight(sheet_data, x_check, token)
    if ":" in flight_information:
        cheapest_price, stops = flight_information.split(":")
    else:
        cheapest_price = flight_information
        stops = 0

    for item in users_data["users"]:
        email = item["email"]
        notifier.notify(cheapest_price, iata, stops, email)
        y_check += 1

    x_check += 1

