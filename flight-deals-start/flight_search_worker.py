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
            try:
                self.notifier.notify(offers[0], email)
            except RuntimeError:
                pass
        return offers, email

    def _convert_to_offers(self, flights_data: list[dict], origin: str, destination: str) -> list[FlightOffer]:
        offers = []
        for flight in flights_data[:3]:
            try:
                price = float(flight.get("price", 0))
                currency = "USD"
                
                flights = flight.get("flights", [])
                if not flights:
                    continue
                    
                first_flight = flights[0]
                departure_airport = first_flight.get("departure_airport", {})
                arrival_airport = first_flight.get("arrival_airport", {})
                
                departure_code = departure_airport.get("id", origin).upper()
                arrival_code = arrival_airport.get("id", destination).upper()
                
                departure_time = departure_airport.get("time", "")
                arrival_time = arrival_airport.get("time", "")
                
                departure_date = departure_time.split(" ")[0] if departure_time else ""
                arrival_date = arrival_time.split(" ")[0] if arrival_time else ""
                
                stops = len(flights) - 1
                
                booking_token = flight.get("booking_token", "")
                booking_link = f"https://www.google.com/travel/flights?q=flights%20from%20{origin}%20to%20{destination}%20on%20{departure_date}"
                
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
