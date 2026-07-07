import smtplib
import os
from datetime import datetime

class NotificationManager:
   def __init__(self):
       self.sender_email = os.environ["SENDER_EMAIL"]
       self.password = os.environ["GMAIL_PASSWORD"]

   def notify(self, cheapest_price, city_code, stops, receiver_email):
       self.value = cheapest_price
       self.date = datetime.now().strftime("%Y-%m-%d")
       self.city = city_code
       self.receiver_email = receiver_email

       request = smtplib.SMTP('smtp.gmail.com')
       request.starttls()
       request.login(self.sender_email, self.password)
       request.sendmail(from_addr=self.sender_email,
                        to_addrs=self.receiver_email,
                        msg=f"Check out the cheapest price for a flight from LAX to {self.city}"
                            f" with {stops} stops. For only {self.value}!"
                            f" On the date of {self.date}.")