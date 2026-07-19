from __future__ import annotations
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
from flight_data import FlightOffer

load_dotenv(Path(__file__).resolve().with_name(".env"))


class NotificationManager:
    def __init__(self, smtp_host: str = "smtp.gmail.com", smtp_port: int = 587) -> None:
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.password = os.getenv("GMAIL_PASSWORD", "")
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    @property
    def configured(self) -> bool:
        return bool(self.sender_email and self.password)

    @staticmethod
    def valid_recipient(address: str) -> bool:
        local, separator, domain = address.strip().partition("@")
        return bool(local and separator and "." in domain and " " not in address)

    @staticmethod
    def subject_for(offer: FlightOffer) -> str:
        return f"Flight deal: {offer.origin_code} to {offer.destination_code}"

    @staticmethod
    def body_for(offer: FlightOffer) -> str:
        trip = f"Depart: {offer.departure_date}"
        if offer.return_date:
            trip = f"{trip} | Return: {offer.return_date}"
        return (
            "A flight deal was found!\n\n"
            f"Route: {offer.route}\n"
            f"Price: {offer.display_price}\n"
            f"Stops: {offer.stop_label}\n{trip}\n\n"
            "Open Flight Club to search again or book through your preferred provider."
        )

    def notify(self, offer: FlightOffer, receiver_email: str) -> None:
        if not self.configured:
            raise RuntimeError("Gmail is not configured. Add SENDER_EMAIL and GMAIL_PASSWORD.")
        if not self.valid_recipient(receiver_email):
            raise ValueError("A recipient email address is required.")
        message = EmailMessage()
        message["Subject"] = self.subject_for(offer)
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message.set_content(self.body_for(offer))
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.sender_email, self.password)
            smtp.send_message(message)
