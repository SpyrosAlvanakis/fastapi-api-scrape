import finnhub
import psycopg2
from textblob import TextBlob
import pandas as pd
import datetime
import time
from .helpers import connect_to_db
from utils.load_secrets import load_secrets


def get_nvidia_news_via_api(start_date, end_date):
    # Set up the Finnhub client
    secrets = load_secrets()
    api_key = secrets.get('api_finhub')['api_key']

    finnhub_client = finnhub.Client(api_key=api_key)

    conn = connect_to_db()
    cur = conn.cursor()
    
    # Create table if not exists
    cur.execute('''CREATE TABLE IF NOT EXISTS nvidia_news_api (
        title TEXT,
        link TEXT,
        date TIMESTAMP,
        source TEXT,
        text TEXT,
        sentiment TEXT,
        sentiment_score NUMERIC
    )''')
    conn.commit()

    # Convert string dates to datetime objects
    start_date_utc = pd.to_datetime(start_date, utc=True)
    end_date_utc = pd.to_datetime(end_date, utc=True)

    current_date = start_date_utc

    while current_date <= end_date_utc:
        # Convert date to string format (YYYY-MM-DD)
        date_str = current_date.strftime('%Y-%m-%d')

        try:
            # Fetch news for the current day
            news = finnhub_client.company_news(symbol='NVDA', _from=date_str, to=date_str)

            for item in news:
                headline = item.get('headline', 'No Title')
                url = item.get('url', 'No URL')

                # Convert the timestamp to UTC using pandas
                date = pd.to_datetime(item['datetime'], unit='s', utc=True).strftime('%Y-%m-%d %H:%M:%S')

                source = item.get('source', 'Unknown Source')
                summary = item.get('summary', 'No Summary')  # Avoid potential NoneType issue
                blob = TextBlob(summary)
                sentiment_score = blob.sentiment.polarity
                sentiment = 'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'

                # Insert news data into the database
                cur.execute('''INSERT INTO nvidia_news_api (title, link, date, source, text, sentiment, sentiment_score)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                            (headline, url, date, source, summary, sentiment, sentiment_score))
                conn.commit()

        except Exception as e:
            print(f"Error fetching or inserting data for {date_str}: {e}")

        # Move to the next day
        current_date += pd.Timedelta(days=1)

        # Sleep for 2 seconds before the next API call
        time.sleep(2)

    # Close the cursor and connection
    cur.close()
    conn.close()

    return "NVIDIA news from API fetched and inserted into the database."