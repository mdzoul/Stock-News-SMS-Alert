"""
This code will return 3 article headlines via SMS
if TSLA stock has increased or decreased by 5%
"""
import os
import requests
from twilio.rest import Client

# -------------------- CONSTANTS -------------------- #
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
STOCK_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_PARAMS = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME,
}
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
FROM_NUM = os.environ.get("FROM_NUM")
TO_NUM = os.environ.get("TO_NUM")

# -------------------- MAIN BODY -------------------- #
# Stock
stock_response = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]

ytd = list(stock_data)[0]
ytd_close = float(stock_data[ytd]["4. close"])

before_ytd = list(stock_data)[1]
before_ytd_close = float(stock_data[before_ytd]["4. close"])

# (𝑉2−𝑉1)/𝑉1 × 100
percentage_diff = round((abs(ytd_close - before_ytd_close) / before_ytd_close * 100), 2)
if ytd_close < before_ytd_close:
    INDICATOR = "🔻"
else:
    INDICATOR = "🔺"

if percentage_diff > 0:
    # News
    news_response = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMS)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]

    three_articles = news_data[:3]
    formatted_articles = [f"Headline: {article['title']}.\nBrief: {article['description']}"
                          for article in three_articles]

    # Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for article in formatted_articles:
        message = client.messages.create(
            body=f"""{STOCK_NAME}: {INDICATOR}{percentage_diff}%\n{article}""",
            from_=FROM_NUM,
            to=TO_NUM
        )
        print(message.status)
