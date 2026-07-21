from __future__ import annotations

from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from ui_constants import APP_NAME, AIRPORTS, BLUE, GOLD, GREEN, PAGE, CARD, SUBTLE, ACCENT, ACCENT_LIGHT, SHADOW, BORDER, LIGHT_BLUE, NAVY
from flight_search_worker import FlightSearchWorker
from flight_data import FlightOffer


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Find Better Flights")
        self.setMinimumSize(900, 900)
        self.resize(1000, 1000)
        
        self.worker = FlightSearchWorker()
        self.offers: list[FlightOffer] = []
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setStyleSheet(f"""
            QMainWindow {{
                background-color: {PAGE};
            }}
            QWidget {{
                background-color: {PAGE};
            }}
            QLabel {{
                color: white;
            }}
            QLineEdit {{
                background-color: {CARD};
                color: white;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                min-height: 16px;
            }}
            QLineEdit:focus {{
                border: 1px solid {LIGHT_BLUE};
            }}
            QPushButton {{
                background-color: white;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 25px 60px;
                font-size: 20px;
                font-weight: bold;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: #f0f0f0;
            }}
            QPushButton:pressed {{
                background-color: #e0e0e0;
            }}
            QPushButton:disabled {{
                background-color: {SHADOW};
                color: #666;
            }}
        """)
        
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 50, 40, 50)
        
        self.setup_header(main_layout)
        self.setup_form(main_layout)
        self.setup_status(main_layout)
        self.setup_results(main_layout)
        
    def setup_header(self, layout: QVBoxLayout) -> None:
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        title_label = QLabel("Flight Club")
        title_label.setFont(QFont("Arial", 52, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        
        plane_label = QLabel("✈")
        plane_label.setFont(QFont("Arial", 54, QFont.Weight.Bold))
        plane_label.setStyleSheet(f"color: white;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(plane_label)
        header_layout.addStretch()
        
        subtitle_label = QLabel("We find better flight deals and email them to you.")
        subtitle_label.setFont(QFont("Arial", 18))
        subtitle_label.setStyleSheet(f"color: {SUBTLE};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def setup_form(self, layout: QVBoxLayout) -> None:
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 40px;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        self.from_input = self.create_text_field("Starting Airport Code", "JFK", form_layout)
        self.to_input = self.create_text_field("Ending Airport Code", "LAX", form_layout)
        self.date_input = self.create_text_field("Travel Date", "mm/dd/yyyy", form_layout)
        self.email_input = self.create_text_field("Your Email", "you@example.com", form_layout)
        
        self.search_button = QPushButton("Find Best Deals Now")
        self.search_button.clicked.connect(self.start_search)
        form_layout.addSpacing(15)
        form_layout.addWidget(self.search_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(form_frame)
        
        
    def create_text_field(self, title: str, placeholder: str, layout: QVBoxLayout) -> QLineEdit:
        label = QLabel(title)
        label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {LIGHT_BLUE};")
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addSpacing(5)
        
        return input_field
        
    def setup_status(self, layout: QVBoxLayout) -> None:
        self.status_label = QLabel("We'll search for the best prices and email you when we find a great deal.")
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setStyleSheet(f"color: {SUBTLE};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        
        layout.addWidget(self.status_label)
        
    def setup_results(self, layout: QVBoxLayout) -> None:
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setVisible(False)
        self.results_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {PAGE};
            }}
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(15)
        
        self.results_area.setWidget(self.results_widget)
        layout.addWidget(self.results_area)
        
    def setup_timer(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_worker_queue)
        self.timer.start(80)
        
    def check_worker_queue(self) -> None:
        has_result, result = self.worker.process_queue()
        if has_result:
            if isinstance(result, Exception):
                self.handle_error(result)
            else:
                self.search_button.setEnabled(True)
                self.search_button.setText("Find Best Deals Now")
                
    def start_search(self) -> None:
        date_text = self.date_input.text().strip()
        email = self.email_input.text().strip()
        
        if date_text == "mm/dd/yyyy":
            date_text = ""
        if email == "you@example.com":
            email = ""
            
        if not date_text:
            QMessageBox.warning(self, APP_NAME, "Please choose your preferred travel date.")
            return
            
        try:
            iso_date = datetime.strptime(date_text, "%m/%d/%Y").date().isoformat()
        except ValueError:
            QMessageBox.warning(self, APP_NAME, "Use the travel-date format mm/dd/yyyy, for example 08/15/2026.")
            return
            
        if not self.worker.notifier.valid_recipient(email):
            QMessageBox.warning(self, APP_NAME, "Please enter a valid email address for your flight deal.")
            return
            
        origin = self.from_input.text().strip().upper()
        destination = self.to_input.text().strip().upper()
        
        if len(origin) != 3 or not origin.isalpha():
            QMessageBox.warning(self, APP_NAME, "Please enter a valid 3-letter airport code for the starting airport (e.g., JFK).")
            return
        if len(destination) != 3 or not destination.isalpha():
            QMessageBox.warning(self, APP_NAME, "Please enter a valid 3-letter airport code for the ending airport (e.g., LAX).")
            return
        
        if origin == destination:
            QMessageBox.warning(self, APP_NAME, "Choose two different airports for your trip.")
            return
            
        self.search_button.setEnabled(False)
        self.search_button.setText("Searching…")
        self.status_label.setText("Searching live fares and preparing your email…")
        self.status_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        
        self.clear_results()
        self.results_area.setVisible(True)
        
        self.worker.start_search(origin, destination, iso_date, email, self.display_results)
        
    def display_results(self, result: tuple[list[FlightOffer], str]) -> None:
        offers, email = result
        self.offers = offers
        
        if not offers:
            self.status_label.setText("No available fares were found for that date. Try another date and search again.")
            self.status_label.setStyleSheet(f"color: {SUBTLE};")
            return
            
        self.status_label.setText(f"Emailed to {email}")
        self.status_label.setStyleSheet(f"color: {GREEN};")
            
    def add_offer_card(self, offer: FlightOffer, rank: int) -> None:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 18px;
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setSpacing(20)
        
        rank_label = QLabel(f"#{rank}")
        rank_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        rank_label.setStyleSheet(f"""
            background-color: {LIGHT_BLUE};
            color: {NAVY};
            padding: 10px 15px;
            border-radius: 6px;
        """)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_label.setFixedSize(60, 50)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(5)
        
        route_label = QLabel(offer.route)
        route_label.setFont(QFont("Arial", 17, QFont.Weight.Bold))
        route_label.setStyleSheet("color: white;")
        
        date_label = QLabel(f"{self.display_date(offer.departure_date)}  •  {offer.stop_label}")
        date_label.setFont(QFont("Arial", 12))
        date_label.setStyleSheet(f"color: {SUBTLE};")
        
        details_layout.addWidget(route_label)
        details_layout.addWidget(date_label)
        
        price_label = QLabel(offer.display_price)
        price_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        price_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: self.show_offer_details(offer))
        view_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BORDER};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BLUE};
                color: {NAVY};
            }}
        """)
        
        card_layout.addWidget(rank_label)
        card_layout.addLayout(details_layout)
        card_layout.addStretch()
        card_layout.addWidget(price_label)
        card_layout.addWidget(view_button)
        
        self.results_layout.addWidget(card)
        
    def show_offer_details(self, offer: FlightOffer) -> None:
        from offer_details_dialog import OfferDetailsDialog
        dialog = OfferDetailsDialog(offer, self)
        dialog.exec()
        
    def display_date(self, value: str) -> str:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%b %-d, %Y")
        except ValueError:
            return value
            
    def clear_results(self) -> None:
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def handle_error(self, error: Exception) -> None:
        self.search_button.setEnabled(True)
        self.search_button.setText("Find Best Deals Now")
        
        friendly_error = self.get_friendly_error(error)
        QMessageBox.critical(self, APP_NAME, friendly_error)
        
        self.status_label.setText("We could not complete that search. Please try again.")
        self.status_label.setStyleSheet(f"color: #ff4757;")
        
    def get_friendly_error(self, error: Exception) -> str:
        text = str(error)
        lower = text.lower()
        
        if "not configured" in lower:
            return text
        if "401" in text or "authentication" in lower or "access token" in lower:
            return "Your Amadeus login was rejected. Check AMADEUS_API_KEY and AMADEUS_API_SECRET in .env."
        if "429" in text:
            return "The flight service is busy right now. Please wait a moment and search again."
        if "timeout" in lower:
            return "The flight service took too long to respond. Check your connection and try again."
        if "smtp" in lower or "gmail" in lower:
            return "Gmail could not send the email. Use a Gmail app password in your .env file."
        return text or "Something went wrong while finding flight prices."
        
    def closeEvent(self, event) -> None:
        self.worker.close()
        self.timer.stop()
        event.accept()
