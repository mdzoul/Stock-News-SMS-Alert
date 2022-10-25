import requests
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = " T9PIYTEYNIB0OACU"
STOCK_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "5641c04f5d704c55a15234e4a4ebd0d3"
NEWS_PARAMS = {
    "apiKey": NEWS_API_KEY,
    "q": COMPANY_NAME
}
TWILIO_ACCOUNT_SID = "AC3759af84b38e8b8c8db11d9d3e01f43a"
TWILIO_AUTH_TOKEN = "65d4359bc6fca2d153f79732249f8b9d"

# Stock
stock_response = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock_data = stock_response.json()

ytd = list(stock_data["Time Series (Daily)"])[0]
ytd_close = float(stock_data["Time Series (Daily)"][ytd]["4. close"])

before_ytd = list(stock_data["Time Series (Daily)"])[1]
before_ytd_close = float(stock_data["Time Series (Daily)"][before_ytd]["4. close"])

percentage_diff = round((abs(ytd_close - before_ytd_close) / before_ytd_close * 100), 2)  # (𝑉2−𝑉1)/𝑉1 × 100

if ytd_close < before_ytd_close:
    indicator = "🔻"
else:
    indicator = "🔺"

if percentage_diff > 5:
    # News
    news_response = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMS)
    news_response.raise_for_status()
    news_data = news_response.json()

    article_headlines_list = [article["title"] for article in news_data["articles"][:3]]
    article_description_list = [article["description"] for article in news_data["articles"][:3]]

    # Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # Send 3 messages at once
    for _ in range(0, 3):
        message = client.messages.create(
            body=f"""
{STOCK_NAME} {indicator}{percentage_diff}%

Headline: {article_headlines_list[_]}

Brief: {article_description_list[_]}
        """,
            from_='+19034833039',
            to='+6582289433'
        )

        print(message.status)
