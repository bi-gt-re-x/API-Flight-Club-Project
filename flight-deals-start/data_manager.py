from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))


class DataManager:

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.bearer = os.getenv("SHEETY_PASSWORD", "")
        self.prices_url = os.getenv("SHEETY_PRICES_URL", "")
        self.users_url = os.getenv("SHEETY_USERS_URL", "")
        self.session = requests.Session()

    @property
    def configured(self) -> bool:
        return bool(self.bearer and self.prices_url and self.users_url)

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.bearer}"}

    @staticmethod
    def clean_destination(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row.get("id"),
            "city": str(row.get("city", "")).strip(),
            "iataCode": str(row.get("iataCode", "")).strip().upper(),
            "lowestPrice": row.get("lowestPrice"),
        }

    @staticmethod
    def clean_email(value: Any) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def is_email(value: str) -> bool:
        local, separator, domain = value.partition("@")
        return bool(local and separator and "." in domain and " " not in value)

    def _require_configuration(self) -> None:
        if not self.configured:
            raise RuntimeError(
                "Sheety is not configured. Add SHEETY_PASSWORD, SHEETY_PRICES_URL, "
                "and SHEETY_USERS_URL to your .env file."
            )

    def get_prices(self) -> list[dict[str, Any]]:
        self._require_configuration()
        response = self.session.get(self.prices_url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        return [self.clean_destination(row) for row in payload.get("prices", [])]

    def get_customer_emails(self) -> list[str]:
        self._require_configuration()
        response = self.session.get(self.users_url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        users = response.json().get("users", [])
        emails = [self.clean_email(user.get("email")) for user in users]
        return list(dict.fromkeys(email for email in emails if self.is_email(email)))

    def update_iata_code(self, row_id: int | str, iata_code: str) -> None:
        self._require_configuration()
        if not row_id:
            raise ValueError("The destination row has no id and cannot be updated.")
        code = iata_code.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("The IATA code must contain three letters.")
        url = f"{self.prices_url.rstrip('/')}/{row_id}"
        response = self.session.put(
            url,
            json={"price": {"iataCode": code}},
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

    def close(self) -> None:
        self.session.close()
