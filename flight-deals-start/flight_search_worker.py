from __future__ import annotations

import threading
import traceback
import queue
from typing import Callable
from serpapi_search import SerpAPISearch
from notification_manager import NotificationManager
from flight_data import FlightOffer


class FlightSearchWorker:
    def __init__(self) -> None:
        self.search_service = SerpAPISearch()
        self.notifier = NotificationManager()
        self.worker_queue: queue.Queue = queue.Queue()

    def search_flights(self, origin: str, destination: str, travel_date: str, email: str) -> tuple[list[FlightOffer], str]:
        flights_data = self.search_service.search_flights(origin, destination, travel_date)
        offers = self._convert_to_offers(flights_data, origin, destination)
        if offers:
            self.notifier.notify(offers[0], email)
        return offers, email

    def _convert_to_offers(self, flights_data: list[dict], origin: str, destination: str) -> list[FlightOffer]:
        offers = []
        for flight in flights_data[:3]:
            try:
                price_info = flight.get("price", {})
                price = float(price_info.get("amount", 0)) if price_info else 0
                currency = price_info.get("currency", "USD") if price_info else "USD"
                
                departure_airport = flight.get("departure_airport", {})
                arrival_airport = flight.get("arrival_airport", {})
                
                departure_code = departure_airport.get("id", origin).split(":")[-1].upper()
                arrival_code = arrival_airport.get("id", destination).split(":")[-1].upper()
                
                departure_date = flight.get("departure_date", "")
                arrival_date = flight.get("arrival_date", "")
                
                stops_info = flight.get("stops", 0)
                if isinstance(stops_info, list):
                    stops = len(stops_info)
                else:
                    stops = int(stops_info) if stops_info else 0
                
                booking_link = flight.get("deep_link", "")
                
                offer = FlightOffer(
                    destination=arrival_airport.get("name", destination),
                    destination_code=arrival_code,
                    origin_code=departure_code,
                    price=price,
                    currency=currency,
                    departure_date=departure_date,
                    return_date=arrival_date if arrival_date != departure_date else None,
                    stops=stops,
                    booking_link=booking_link
                )
                offers.append(offer)
            except (ValueError, KeyError, TypeError):
                continue
        
        return sorted(offers, key=lambda x: x.price)

    def start_search(self, origin: str, destination: str, travel_date: str, email: str, callback: Callable[[tuple[list[FlightOffer], str]], None]) -> None:
        def runner() -> None:
            try:
                result = self.search_flights(origin, destination, travel_date, email)
                self.worker_queue.put(("done", callback, result))
            except Exception as error:
                self.worker_queue.put(("error", error, traceback.format_exc()))
        
        threading.Thread(target=runner, daemon=True, name="flight-club-search").start()

    def process_queue(self) -> tuple[bool, tuple[list[FlightOffer], str] | Exception | None]:
        try:
            item = self.worker_queue.get_nowait()
            if item[0] == "error":
                return True, item[1]
            else:
                callback = item[1]
                result = item[2]
                callback(result)
                return True, result
        except queue.Empty:
            return False, None

    def close(self) -> None:
        self.search_service.close()
