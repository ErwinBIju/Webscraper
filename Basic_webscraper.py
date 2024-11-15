import requests
import re
import os
import smtplib
import sqlite3
import schedule
import time
from twilio.rest import Client
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup

# Twilio client setup
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
account_token = os.getenv("TWILIO_ACCOUNT_TOKEN")
client = Client(account_sid, account_token)

# Email setup (use app password for Yahoo)
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Initialize the SQLite database
def initialize_db():
    """Creates the database table if it doesn't already exist."""
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PriceHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            price REAL,
            date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Scraping function to get product details
def scraper():
    """Scrapes product name and price from the given URL."""
    url = "https://a.co/d/8pIHcvR"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Successfully fetched the website")
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        print(f"URL extraction failed with status code {response.status_code}")
        exit(0)

    name_element = soup.find("meta", attrs={"name": "title"})
    price_element = soup.find("span", class_="a-offscreen")

    # Extract price and clean up
    price = price_element.get_text() if price_element else None
    price = re.sub(r'[^\d.]', '', price) if price else None
    price = float(price) if price else None

    # Extract product name
    product_name = name_element["content"] if name_element and "content" in name_element.attrs else None
    
    return product_name, price

# Send SMS notification using Twilio
def send_sms_notification(to_phone_number, message_body):
    """Sends an SMS to the given phone number."""
    message = client.messages.create(
        body=message_body,
        from_="+1 (xxx) xxx-xxxx",
        to=to_phone_number
    )
    print(f"Message sent! SID: {message.sid}")

# Send email notification
def send_alert(email, product_name, current_price):
    """Sends an email alert about price change."""
    msg = MIMEText(f"The price for {product_name} dropped to {current_price}")
    msg['Subject'] = "Price Alert"
    msg['From'] = EMAIL_USER
    msg['To'] = email

    try:
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)  # Use app password
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error in sending email: {e}")

# Get the last price stored in the database
def get_last_price_from_db(product_name):
    """Fetches the last recorded price for the product."""
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price FROM PriceHistory
        WHERE product_name = ?
        ORDER BY date DESC
        LIMIT 1
    ''', (product_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Store price in the database
def store_price_in_db(product_name, price):
    """Stores product price data in the database."""
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO PriceHistory (product_name, price, date)
        VALUES (?, ?, ?)
    ''', (product_name, price, datetime.now()))
    conn.commit()
    conn.close()
    print("Price stored in database")

# Main function to run the scraper and handle alerts
def main():
    try:
        product_name, current_price = scraper()
        initialize_db()
        last_price = get_last_price_from_db(product_name)
        
        # Check if the price has changed
        if last_price != current_price:
            store_price_in_db(product_name, current_price)
            
            recipient_email = "xxxxxxxxxx@xxxx.xxx"
            message_body = f"The price for the {product_name} has decreased to CAD{current_price}!"
            
            # Send SMS and email alerts if price falls below $15
            if current_price < 15:
                send_sms_notification("+1 (xxx) xxx-xxxx", message_body)
                #send_alert(recipient_email, product_name, current_price)
            else:
                print(f"Product: {product_name}, Price: {current_price}")
        else:
            print("Price has not changed")

    
    except Exception as e:
        print(f"An exception {e} occurred.")

# Schedule the task to run daily at 2 AM
schedule.every().day.at("02:00").do(main)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(5)