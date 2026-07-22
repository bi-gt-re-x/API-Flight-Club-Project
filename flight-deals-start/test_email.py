from __future__ import annotations

from notification_manager import NotificationManager
from flight_data import FlightOffer


def test_email():
    notifier = NotificationManager()
    
    print(f"Email configured: {notifier.configured}")
    print(f"Sender email: {notifier.sender_email}")
    
    if not notifier.configured:
        print("\nERROR: Email not configured.")
        print("Please add your Gmail credentials to .env file:")
        print("  SENDER_EMAIL=your_email@gmail.com")
        print("  GMAIL_PASSWORD=your_app_password")
        print("\nNote: For Gmail, use an App Password (not your regular password).")
        print("Get one at: https://myaccount.google.com/apppasswords")
        return
    
    try:
        print("\nSending test email...")
        
        test_offer = FlightOffer(
            destination="Los Angeles",
            destination_code="LAX",
            origin_code="JFK",
            price=264.0,
            currency="USD",
            departure_date="2026-08-15",
            return_date=None,
            stops=0,
            booking_link="https://www.google.com/travel/flights"
        )
        
        recipient = input("Enter recipient email: ").strip()
        
        notifier.notify(test_offer, recipient)
        print(f"Email sent successfully to {recipient}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_email()
