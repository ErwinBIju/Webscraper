# Price Alert Scraper

This Python script monitors the price of a specific product from Amazon using web scraping. If the price changes (and falls below a certain threshold), it sends an SMS and email alert. The price is also stored in an SQLite database for historical tracking.

## Features:
- Scrapes product information (name and price) from a given URL.
    Responsible for scraping the product details from a specific Amazon URL (https://a.co/d/8pIHcvR). It retrieves the product name and price from the page’s HTML content using the BeautifulSoup library.
- Stores price history in an SQLite database.
    Stores the current price of the product in the SQLite database, including the product name and the current date/time.
- Sends SMS notifications using Twilio when price drops below a threshold.
    Sends an SMS notification using the Twilio API. It takes a phone number (to_phone_number) and a message body (message_body) as parameters and sends the message to the specified number.
- Sends email alerts for price change notifications.
    Sends an email alert to a specified email address when the product price changes. The email contains the product name and the new price. It uses the smtplib library to send the email via Yahoo’s SMTP server.
- Runs the script daily at 2 AM using a scheduler.
    Use a scheduling library like schedule or APScheduler to automate scraping at regular intervals (e.g., daily or weekly). This way, you can track price trends over time without manually running the script.

## Requirements:
- Python 3.x
- `requests` library
- `BeautifulSoup` (part of `bs4` package)
- `Twilio` library for SMS notifications
- `sqlite3` for the database
- `smtplib` for email notifications
- `schedule` for task scheduling

You can install required libraries with:
```bash
pip install requests beautifulsoup4 twilio schedule