import os
import requests
from datetime import datetime

class FlightData:
    def __init__(self):
        #My 3 brain cells tell me Nitesh or Bhasvat will try and steal it.
        self.api_key = os.environ["AMADEUS_API_KEY"]
        self.api_secret = os.environ["AMADEUS_API_SECRET"]

    def find_cheapest_flight(self, sheet_data, x_check, token, is_direct=True):
        city_iatacode = sheet_data["prices"][x_check]["iataCode"]
        max_price = sheet_data["prices"][x_check]["lowestPrice"]

        date = datetime.now().strftime("%Y-%m-%d")

        self.headers = {
            "Authorization": f"Bearer {token}"
        }

        self.url = (
            f"https://test.api.amadeus.com/v2/shopping/flight-offers"
            f"?originLocationCode=LAX"
            f"&destinationLocationCode={city_iatacode}"
            f"&departureDate={date}"
            f"&adults=1"
            f"&maxPrice={max_price}"
            f"&travelClass=ECONOMY"
            f"&nonstop={str(is_direct).lower()}"
        )


        response = requests.get(url=self.url, headers=self.headers)


        try:
            cheapest_price = response.json()["data"][0]["price"]["total"]
            data = response.json().get("data", [])
            if not data:
                is_direct = False

                self.url = (
                    f"https://test.api.amadeus.com/v2/shopping/flight-offers"
                    f"?originLocationCode=LAX"
                    f"&destinationLocationCode={city_iatacode}"
                    f"&departureDate={date}"
                    f"&adults=1"
                    f"&maxPrice={max_price}"
                    f"&travelClass=ECONOMY"
                    f"nonstop={is_direct}"
                )

                response = requests.get(url=self.url, headers=self.headers)
                number_of_stops = response.json()["itineraries"][0]["segments"]["numberOfStops"] - 1
            else:
                number_of_stops = 0

            return (f"{cheapest_price}:{number_of_stops}")
        except (KeyError,IndexError):
            return "$67"

