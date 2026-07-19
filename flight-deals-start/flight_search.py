from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))


class FlightSearch:
    TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    CITY_URL = "https://test.api.amadeus.com/v1/reference-data/locations/cities"

    def __init__(self, timeout: int = 20) -> None:
        self.api_key = os.getenv("AMADEUS_API_KEY", "")
        self.api_secret = os.getenv("AMADEUS_API_SECRET", "")
        self.timeout = timeout
        self.session = requests.Session()
        self.token = ""

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_secret)

    @property
    def token_ready(self) -> bool:
        return bool(self.token)

    def clear_token(self) -> None:
        self.token = ""

    def get_new_token(self) -> str:
        if not self.configured:
            raise RuntimeError("Amadeus is not configured. Add AMADEUS_API_KEY and AMADEUS_API_SECRET.")
        response = self.session.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token

    def _headers(self) -> dict[str, str]:
        if not self.token:
            self.get_new_token()
        return {"Authorization": f"Bearer {self.token}"}

    def get_iata_code(self, city: str) -> str:
        query = city.strip()
        if not query:
            raise ValueError("A city name is required for an IATA lookup.")
        if len(query) < 2:
            raise ValueError("Enter at least two letters of a city name.")
        response = self.session.get(
            self.CITY_URL,
            params={"keyword": query, "max": 1},
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        locations: list[dict[str, Any]] = response.json().get("data", [])
        if not locations or not locations[0].get("iataCode"):
            raise LookupError(f"No IATA code was found for {city}.")
        return str(locations[0]["iataCode"]).upper()

    def close(self) -> None:
        self.session.close()
