from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import requests


@dataclass
class FlightOffer:
    destination: str
    destination_code: str
    origin_code: str
    price: float
    currency: str
    departure_date: str
    return_date: str | None
    stops: int
    booking_link: str = ""

    def is_below(self, threshold: float) -> bool:
        return self.price <= threshold

    @property
    def route(self) -> str:
        return f"{self.origin_code} → {self.destination_code}"

    @property
    def display_price(self) -> str:
        return f"{self.currency} {self.price:,.2f}"

    @property
    def stop_label(self) -> str:
        if self.stops == 0:
            return "Direct flight"
        return f"{self.stops} stop{'s' if self.stops != 1 else ''}"

    @property
    def trip_dates(self) -> str:
        if self.return_date:
            return f"{self.departure_date} to {self.return_date}"
        return self.departure_date

    def details(self) -> dict[str, str | float | int | None]:
        return {
            "route": self.route,
            "destination": self.destination,
            "price": self.price,
            "currency": self.currency,
            "departure_date": self.departure_date,
            "return_date": self.return_date,
            "stops": self.stops,
            "booking_link": self.booking_link,
        }


class FlightData:
    OFFERS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def find_cheapest_flight(
        self, origin: str, destination: str, token: str, departure_date: str,
        adults: int = 1, max_price: float | None = None, nonstop: bool = False,
    ) -> FlightOffer | None:
        params: dict[str, Any] = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": "ECONOMY",
            "nonStop": str(nonstop).lower(),
            "max": 20,
        }
        if max_price is not None and max_price > 0:
            params["maxPrice"] = max_price
        offers = self.find_best_flights(
            origin=origin,
            destination=destination,
            token=token,
            departure_date=departure_date,
            adults=adults,
            max_price=max_price,
            nonstop=nonstop,
            limit=1,
        )
        return offers[0] if offers else None

    def find_best_flights(
        self, origin: str, destination: str, token: str, departure_date: str,
        adults: int = 1, max_price: float | None = None, nonstop: bool = False,
        limit: int = 3,
    ) -> list[FlightOffer]:
        self._validate_search(origin, destination, departure_date, adults, limit)
        params: dict[str, Any] = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": "ECONOMY",
            "nonStop": str(nonstop).lower(),
            "max": max(3, min(20, limit * 5)),
        }
        if max_price is not None and max_price > 0:
            params["maxPrice"] = max_price
        response = self.session.get(
            self.OFFERS_URL,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        raw_offers = response.json().get("data", [])
        ranked = sorted(raw_offers, key=lambda offer: float(offer["price"]["grandTotal"]))[:limit]
        return [self._to_offer(offer, origin, destination) for offer in ranked]

    @staticmethod
    def _validate_search(origin: str, destination: str, departure_date: str, adults: int, limit: int) -> None:
        if len(origin.strip()) != 3 or not origin.strip().isalpha():
            raise ValueError("The origin airport must be a three-letter IATA code.")
        if len(destination.strip()) != 3 or not destination.strip().isalpha():
            raise ValueError("The destination airport must be a three-letter IATA code.")
        try:
            date.fromisoformat(departure_date)
        except ValueError as error:
            raise ValueError("The departure date must use YYYY-MM-DD.") from error
        if adults < 1 or adults > 9:
            raise ValueError("The number of travelers must be from 1 to 9.")
        if limit < 1 or limit > 20:
            raise ValueError("The number of returned offers must be from 1 to 20.")

    def _to_offer(self, raw: dict[str, Any], origin: str, destination: str) -> FlightOffer:
        itinerary = raw.get("itineraries", [{}])[0]
        segments = itinerary.get("segments", [])
        first_segment = segments[0] if segments else {}
        last_segment = segments[-1] if segments else {}
        departure = first_segment.get("departure", {}).get("at", "")[:10]
        return_date = None
        if len(raw.get("itineraries", [])) > 1:
            return_date = raw["itineraries"][1].get("departure", {}).get("at", "")[:10]
        return FlightOffer(
            destination=destination,
            destination_code=destination,
            origin_code=origin,
            price=float(raw["price"]["grandTotal"]),
            currency=str(raw["price"].get("currency", "USD")),
            departure_date=departure,
            return_date=return_date,
            stops=max(0, len(segments) - 1),
            booking_link=raw.get("self", {}).get("href", ""),
        )

    @staticmethod
    def default_departure_date(days_from_now: int = 30) -> str:
        return (date.today() + timedelta(days=days_from_now)).isoformat()

    def close(self) -> None:
        self.session.close()
