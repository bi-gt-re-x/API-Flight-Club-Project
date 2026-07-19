from __future__ import annotations

from datetime import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import webbrowser

from ui_constants import APP_NAME, LIGHT_BLUE, NAVY, PAGE, SUBTLE, BORDER
from flight_data import FlightOffer


class OfferDetailsDialog(QDialog):
    def __init__(self, offer: FlightOffer, parent=None) -> None:
        super().__init__(parent)
        self.offer = offer
        self.setup_ui()
        
    def setup_ui(self) -> None:
        self.setWindowTitle(f"{APP_NAME} — Deal details")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PAGE};
            }}
            QLabel {{
                color: white;
            }}
            QPushButton {{
                background-color: {LIGHT_BLUE};
                color: {NAVY};
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)
        self.setMinimumSize(500, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 35, 40, 35)
        
        title_label = QLabel("Flight deal details")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        layout.addWidget(title_label)
        
        route_label = QLabel(self.offer.route)
        route_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        route_label.setStyleSheet(f"color: white;")
        layout.addWidget(route_label)
        
        details_text = f"Date: {self.display_date(self.offer.departure_date)}\n{self.offer.stop_label}\nTotal: {self.offer.display_price}"
        details_label = QLabel(details_text)
        details_label.setFont(QFont("Arial", 14))
        details_label.setStyleSheet(f"color: {SUBTLE};")
        layout.addWidget(details_label)
        
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        
        if self.offer.booking_link:
            open_button = QPushButton("Open offer link")
            open_button.clicked.connect(self.open_link)
            buttons_layout.addWidget(open_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BORDER};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BLUE};
                color: {NAVY};
            }}
        """)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
    def display_date(self, value: str) -> str:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%b %-d, %Y")
        except ValueError:
            return value
            
    def open_link(self) -> None:
        if self.offer.booking_link:
            webbrowser.open(self.offer.booking_link)
