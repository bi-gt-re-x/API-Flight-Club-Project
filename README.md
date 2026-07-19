# Flight Club

Flight Club is a desktop flight-deal finder built with Python and Tkinter. Choose a departure airport, destination airport, preferred travel date, and email address. Flight Club checks live Amadeus offers, shows the three best prices, and emails the lowest deal to you through Gmail.

## What the app does

- Select a departure airport from a clear airport menu.
- Select a destination airport from a clear airport menu.
- Enter a preferred travel date in `mm/dd/yyyy` format.
- Enter the email address that should receive the deal.
- Search live Amadeus prices for the selected route.
- Rank and show the three lowest available prices.
- Email the lowest available price through Gmail.
- Open an individual result to see its details and available offer link.

## Run Flight Club

Open the project in PyCharm, open `flight-deals-start/main.py`, and run it with a Python 3 interpreter. You can also run it from a terminal:

```bash
cd flight-deals-start
python3 main.py
```

The application reads `.env` from the same folder as `main.py`, so it works whether PyCharm starts the program from the project folder or from `flight-deals-start`.

## Python packages

Flight Club uses two Python packages in addition to the Python standard library:

```bash
python3 -m pip install requests python-dotenv
```

In PyCharm, install these into the interpreter selected for the project. Open the project interpreter settings, add `requests` and `python-dotenv`, then run `main.py` again.

Tkinter is included with most Python installations on macOS. The interface uses standard Tk widgets so it remains compatible with the older Tk version bundled with some macOS Python installations.

## Required setup

Create a file named `.env` inside `flight-deals-start`. Do not share this file or commit it to Git because it holds private credentials.

```env
AMADEUS_API_KEY=your_amadeus_client_id
AMADEUS_API_SECRET=your_amadeus_client_secret
SENDER_EMAIL=your_gmail_address@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
```

`SENDER_EMAIL` is the Gmail account sending the deal notification. `GMAIL_PASSWORD` must be a Gmail app password, not the regular Gmail account password.

## Gmail app password

1. Turn on two-step verification for the Gmail account that sends the messages.
2. In Google Account security settings, create an app password for Mail.
3. Copy that app password into `GMAIL_PASSWORD` in `.env`.
4. Restart Flight Club after changing `.env` values.

## Supported airports

The interface currently includes these commonly used airport choices:

- New York — JFK
- Los Angeles — LAX
- Chicago — ORD
- Dallas — DFW
- Miami — MIA
- San Francisco — SFO
- Seattle — SEA
- Atlanta — ATL
- Boston — BOS
- Las Vegas — LAS

## Search behavior

Flight Club asks Amadeus for multiple offers, sorts the response by total price, and displays up to three options. The price is the total returned by the flight service for the selected traveler count. Availability can vary by date, route, and the Amadeus test account.

If no flights are returned, try a different travel date or airport pairing. A successful configuration can still produce no offers if the Amadeus test environment has no inventory for that search.

## Troubleshooting

If Flight Club says the Amadeus login was rejected, verify `AMADEUS_API_KEY` and `AMADEUS_API_SECRET` in `.env`.

If Flight Club cannot send the email, verify the Gmail address and use an app password instead of a normal password.

If the date is rejected, enter it exactly as `08/15/2026` rather than `2026-08-15`.

If you do not see the form after starting the app, make sure PyCharm is using the same Python interpreter where `requests` and `python-dotenv` are installed.

If the email does not arrive, check the Spam folder first. Gmail app-password messages can occasionally be filtered when an account sends its first message to a recipient.

The search button remains disabled while a request is running. This prevents duplicate API searches and duplicate email notifications.
