from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))


class SerpAPISearch:
    def __init__(self, timeout: int = 20) -> None:
        self.api_key = os.getenv("SERPAPI_KEY", "")
        self.endpoint = os.getenv("SERPAPI_ENDPOINT", "https://serpapi.com/search?engine=google_flights")
        self.timeout = timeout
        self.session = requests.Session()

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def search_flights(self, origin: str, destination: str, departure_date: str, adults: int = 1) -> list[dict[str, Any]]:
        if not self.configured:
            raise RuntimeError("SerpAPI is not configured. Add SERPAPI_KEY to .env.")
        
        params = {
            "api_key": self.api_key,
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "adults": adults,
            "type": "flights",
            "hl": "en",
            "currency": "USD"
        }
        
        response = self.session.get(
            self.endpoint,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "best_flights" in data:
            return data["best_flights"]
        elif "flights" in data:
            return data["flights"]
        else:
            return []

    def close(self) -> None:
        self.session.close()
