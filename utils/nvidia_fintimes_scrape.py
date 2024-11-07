import requests
from bs4 import BeautifulSoup
from datetime import datetime
from textblob import TextBlob
import psycopg2
import time
from utils.helpers import connect_to_db
from utils.load_secrets import load_secrets


def scrape_nvidia_ft(start_date_str, end_date_str):
    # Convert dates from strings
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Database connection
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS nvidia_fintimes_scrape (
        title TEXT,
        link TEXT,
        date TIMESTAMP,
        source TEXT,
        text TEXT,
        sentiment TEXT,
        sentiment_score NUMERIC
    )''')
    conn.commit()

    # Scraping logic
    secrets = load_secrets()
    ft_secrets = secrets.get('fin_times_site')
    url_base = ft_secrets.get('site_ft')
    sup = ft_secrets.get('ft_sup')
    link_ft_for_href = ft_secrets.get('link_ft_for_href')

    i = 1
    loop_control = True

    while loop_control:
        url = f'{url_base}&page={i}{sup}' if i > 1 else f'{url_base}{sup}'
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        hyper_news = soup.find_all('div', class_='o-teaser__content')

        if not hyper_news:
            break

        for news in hyper_news:
            # Safely find and parse the date element
            news_date_element = news.find('time', class_='o-teaser__timestamp-date')
            if news_date_element:
                news_date_text = news_date_element.get_text().strip()
                news_date = datetime.strptime(news_date_text, '%B %d, %Y')

                if news_date < start_date:
                    loop_control = False
                    break
                if news_date > end_date:
                    continue
            else:
                continue  # Skip if date is missing

            # Safely extract the title
            title_element = news.find('a', class_='js-teaser-heading-link')
            if title_element:
                title = title_element.get_text().strip()
                link = link_ft_for_href + title_element['href']
            else:
                continue  # Skip if title or link is missing

            # Safely extract the text (standfirst)
            text_element = news.find('p', class_='o-teaser__standfirst')
            text = text_element.get_text().strip() if text_element else ''

            # Sentiment analysis
            sentiment_analysis = TextBlob(text)
            sentiment_score = sentiment_analysis.sentiment.polarity
            sentiment = 'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'

            # Insert data into the database
            cursor.execute('''INSERT INTO nvidia_fintimes_scrape (title, link, date, source, text, sentiment, sentiment_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)''', (title, link, news_date, "Financial Times", text, sentiment, sentiment_score))
            conn.commit()

            time.sleep(1)  # Delay to avoid overwhelming the server

        i += 1

    cursor.close()
    conn.close()

    return "Financial Times NVIDIA news scraped and inserted into the database."
