import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DataManager:
    def __init__(self):
        self.bearer = os.environ["SHEETY_PASSWORD"]
        self.prices_url = os.environ["SHEETY_PRICES_URL"]
        self.users_url = os.environ["SHEETY_USERS_URL"]

        self.headers = {
            "Authorization": f"Bearer {self.bearer}",
        }

        self.response = requests.get(self.prices_url, headers=self.headers)
        self.response.raise_for_status()
        self.prices = self.response.json()

    def update_docs(self, sheet_data, x_check):
        self.id = sheet_data["prices"][x_check]["id"]
        self.url = f"{self.prices_url}/{self.id}"
        self.json = sheet_data["prices"][x_check]["iataCode"]

        self.final_json = {
            "price": {
                "iataCode": self.json,
            }
        }

        self.response = requests.put(url=self.prices_url, json=self.final_json, headers=self.headers)
        print(self.response.text)

    def get_customer_emails(self):
        self.response = requests.get(url=self.users_url, headers=self.headers)
        return self.response.json()
























