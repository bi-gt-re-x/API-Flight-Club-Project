import os
import requests

# I swear the api is trolling me, I'm pretty sure Amadeus costs money, if ur spending 5 dollars, give some to me please

class FlightSearch:
    def __init__(self):
        self.api_key = os.environ["AMADEUS_API_KEY"]
        self.api_secret = os.environ["AMADEUS_API_SECRET"]
        self.TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.CITY_URL = "https://test.api.amadeus.com/v1/reference-data/locations/cities"

        self.token_data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }

        self.token = self.get_new_token()

        self.headers = {
            "Authorization": f"Bearer {self.token}",
        }

    def check_iata(self, iata, sheet_data, x_check):
        if not iata or iata == "TESTING":

            self.city_params = {
                "keyword": sheet_data["prices"][x_check]["city"],
            }

            response = requests.get(url=self.CITY_URL,
                                    params=self.city_params,
                                    headers=self.headers,)
            sheet_data["prices"][x_check].update({"iataCode": response.json()["data"][0]["iataCode"]})

    def get_new_token(self):
        response = requests.post(self.TOKEN_URL, data=self.token_data)
        return response.json()["access_token"]
