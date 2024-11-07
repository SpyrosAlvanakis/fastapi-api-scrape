import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import time
from textblob import TextBlob
from .helpers import connect_to_db
from utils.load_secrets import load_secrets


def scrape_nvidia_news_site(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    conn = connect_to_db()
    cur = conn.cursor()
    
    # Create table if not exists
    cur.execute('''CREATE TABLE IF NOT EXISTS nvidia_originalsite_scrape (
        title TEXT,
        link TEXT,
        date TIMESTAMP,
        source TEXT,
        text TEXT,
        sentiment TEXT,
        sentiment_score NUMERIC
    )''')
    conn.commit()

    secrets = load_secrets()
    nvidia_or = secrets.get('original_nvidia_site')
    base_url = nvidia_or['site_nv_url']
    i = 1
    keep_going = True

    while keep_going:
        url_page = base_url + "page=" + str(i)
        res = requests.get(url_page)
        soup = BeautifulSoup(res.text, "html.parser")
        articles_section = soup.find_all('div', class_="index-item-text")

        for article in articles_section:
            date_str = article.find('span', class_="index-item-text-info-date").get_text().strip()
            article_date = datetime.strptime(date_str, "%B %d, %Y")

            if article_date < start_date:
                keep_going = False
                break
            if article_date > end_date:
                continue

            link = article.find('a').get('href')
            title = article.find('a').get_text().strip()

            # If the link is relative, prepend the base URL
            if link.startswith("/"):
                link = nvidia_or['relative_site_nv_url'] + link

            # Fetch the full article from the link and extract the text from <p> tags
            article_res = requests.get(link)
            article_soup = BeautifulSoup(article_res.text, "html.parser")
            text = " ".join([p.get_text() for p in article_soup.find_all('p')])

            # Analyze sentiment
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            sentiment = 'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'

            # Insert data into the PostgreSQL database
            cur.execute('''INSERT INTO nvidia_originalsite_scrape (title, link, date, source, text, sentiment, sentiment_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)''', (title, link, article_date, "NVIDIA", text, sentiment, sentiment_score))
            conn.commit()

            time.sleep(2)  # Be polite and avoid overwhelming the server

        i += 1

    cur.close()
    conn.close()

    return "NVIDIA news from site scraped and inserted into the database."

