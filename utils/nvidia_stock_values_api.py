import yfinance as yf
import psycopg2
import time
from .helpers import connect_to_db

def scrape_nvidia_stock(start_date, end_date):
    # Connect to PostgreSQL
    conn = connect_to_db()
    cursor = conn.cursor()

    # List of companies to scrape data for
    companies = ["NVDA", "AAPL", "AMD"]
    
    # Create tables for each company if they don't exist
    for company in companies:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {company}_stock_values (
            date DATE PRIMARY KEY,
            open FLOAT NOT NULL,
            high FLOAT NOT NULL,
            low FLOAT NOT NULL,
            close FLOAT NOT NULL,
            volume FLOAT NOT NULL
        )''')
    conn.commit()

    # Fetch stock data using yfinance for each company
    stock_data = {}
    stock_data["NVDA"] = yf.Ticker("NVDA").history(start=start_date, end=end_date, interval='1d')
    stock_data["AAPL"] = yf.Ticker("AAPL").history(start=start_date, end=end_date, interval='1d')
    stock_data["AMD"] = yf.Ticker("AMD").history(start=start_date, end=end_date, interval='1d')

    # Function to insert data into PostgreSQL
    def insert_data(company, data):
        for index, row in data.iterrows():
            insert_query = f'''
            INSERT INTO {company}_stock_values (date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING
            '''
            # Convert np.float64 to standard Python float
            cursor.execute(insert_query, (
                index.date(), 
                float(row['Open']), 
                float(row['High']), 
                float(row['Low']), 
                float(row['Close']), 
                float(row['Volume'])
            ))

    # Insert stock data for each company
    for company in companies:
        insert_data(company, stock_data[company])

    # Commit and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    return "Stock data for NVDA, AAPL, and AMD scraped and inserted into the database."
