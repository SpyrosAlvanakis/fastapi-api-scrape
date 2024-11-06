import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from .helpers import pandas_db_connection, minmax_normalize

# ============================
#    Analysis func 1
# ============================
def linear_regression_analysis():
    """Performs linear regression analysis on NVIDIA stock price using sentiment scores and AMD/Apple close values."""

    conn = pandas_db_connection()

    # Query to get NVIDIA stock data with just the date (no timestamp)
    query_nvidia_stock = "SELECT date::date AS date, close FROM nvda_stock_values"
    df_nvidia_stock = pd.read_sql_query(query_nvidia_stock, conn)

    # Query to get AMD stock data with just the date (no timestamp)
    query_amd_stock = "SELECT date::date AS date, close FROM amd_stock_values"
    df_amd_stock = pd.read_sql_query(query_amd_stock, conn)

    # Query to get Apple stock data with just the date (no timestamp)
    query_apple_stock = "SELECT date::date AS date, close FROM aapl_stock_values"
    df_apple_stock = pd.read_sql_query(query_apple_stock, conn)

    # Rename the 'close' columns appropriately for each stock dataframe
    df_nvidia_stock.rename(columns={'close': 'close_nvda'}, inplace=True)
    df_amd_stock.rename(columns={'close': 'close_amd'}, inplace=True)
    df_apple_stock.rename(columns={'close': 'close_aapl'}, inplace=True)

    # Merge the stock dataframes on 'date'
    df_stock = pd.merge(df_nvidia_stock, df_amd_stock, on='date', how='outer')
    df_stock = pd.merge(df_stock, df_apple_stock, on='date', how='outer')

    # Query to get sentiment scores from all the sources
    # query_nvidia_news_api = "SELECT date, source, sentiment_score FROM nvidia_news_api"
    query_nvidia_news_api = """
        WITH all_dates AS (
            SELECT 
                generate_series(
                    (SELECT MIN(date::date) FROM nvidia_news_api),  -- Casting to date here
                    (SELECT MAX(date::date) FROM nvidia_news_api), 
                    '1 day'::interval
                )::date AS date
        )
        SELECT 
            all_dates.date,
            COALESCE(AVG(t.sentiment_score), 0) AS sentiment_score_api_news,  -- Correctly referencing sentiment_score
            'api_news' AS source  -- Assigning 'api_news' as the source
        FROM all_dates
        LEFT JOIN nvidia_news_api t 
            ON all_dates.date = t.date::date  -- Casting nvidia_news_api.date to date
        WHERE EXTRACT(DOW FROM all_dates.date) NOT IN (0, 6)  -- Exclude Sundays (0) and Saturdays (6)
        GROUP BY all_dates.date
        ORDER BY all_dates.date;
        """
    query_nvidia_original = """
        WITH all_dates AS (
            SELECT 
                generate_series(
                    (SELECT MIN(date::date) FROM nvidia_originalsite_scrape),  -- Casting to date here
                    (SELECT MAX(date::date) FROM nvidia_originalsite_scrape), 
                    '1 day'::interval
                )::date AS date
        )
        SELECT 
            all_dates.date,
            COALESCE(AVG(t.sentiment_score), 0) AS sentiment_score_original,  -- Correctly referencing sentiment_score
            'original' AS source  -- Assigning 'original' as the source
        FROM all_dates
        LEFT JOIN nvidia_originalsite_scrape t 
            ON all_dates.date = t.date::date  -- Casting nvidia_originalsite_scrape.date to date
        WHERE EXTRACT(DOW FROM all_dates.date) NOT IN (0, 6)  -- Exclude Sundays (0) and Saturdays (6)
        GROUP BY all_dates.date
        ORDER BY all_dates.date;    
        """
    query_ft_nvidia = """
        WITH all_dates AS (
            SELECT 
                generate_series(
                    (SELECT MIN(date::date) FROM nvidia_fintimes_scrape),  -- Casting to date here
                    (SELECT MAX(date::date) FROM nvidia_fintimes_scrape), 
                    '1 day'::interval
                )::date AS date
        )
        SELECT 
            all_dates.date,
            COALESCE(AVG(t.sentiment_score), 0) AS sentiment_score_ft,  -- Correctly referencing sentiment_score
            'ft' AS source  -- Assigning 'ft' as the source
        FROM all_dates
        LEFT JOIN nvidia_fintimes_scrape t 
            ON all_dates.date = t.date::date  -- Casting nvidia_fintimes_scrape.date to date
        WHERE EXTRACT(DOW FROM all_dates.date) NOT IN (0, 6)  -- Exclude Sundays (0) and Saturdays (6)
        GROUP BY all_dates.date
        ORDER BY all_dates.date;
        """

    df_news_api = pd.read_sql_query(query_nvidia_news_api, conn)
    df_original = pd.read_sql_query(query_nvidia_original, conn)
    df_ft = pd.read_sql_query(query_ft_nvidia, conn)

    # Merge the dataframes on the 'date' column using outer joins to ensure all dates are included
    df_combined = pd.merge(df_news_api[['date', 'sentiment_score_api_news']], 
                        df_original[['date', 'sentiment_score_original']], 
                        on='date', 
                        how='outer')

    df_combined = pd.merge(df_combined, 
                        df_ft[['date', 'sentiment_score_ft']], 
                        on='date', 
                        how='outer')

    # Fill missing sentiment scores with 0 for each sentiment source
    df_combined['sentiment_score_api_news'].fillna(0, inplace=True)
    df_combined['sentiment_score_original'].fillna(0, inplace=True)
    df_combined['sentiment_score_ft'].fillna(0, inplace=True)

    # Sort by date to maintain chronological order
    df_combined.sort_values(by='date', inplace=True)

    # Now merge the stock data with the sentiment data (df_combined) on 'date'
    df_merged = pd.merge(df_stock, df_combined, on='date', how='outer')

    # Drop rows where any of the close stock columns ('close_nvda', 'close_amd', 'close_aapl') have NaN values
    df_merged.dropna(subset=['close_nvda', 'close_amd', 'close_aapl'], inplace=True)

    # Sort by date to maintain chronological order
    df_merged.sort_values(by='date', inplace=True)

    # Optional: reset index
    df_merged.reset_index(drop=True, inplace=True)

    # Define features (sentiment scores and stock prices) and target (NVIDIA stock prices)
    X = df_merged[['sentiment_score_api_news', 'sentiment_score_original', 'sentiment_score_ft', 'close_amd', 'close_aapl']]
    y = df_merged['close_nvda']

    # Fit the linear regression model on the training set
    model = LinearRegression()
    model.fit(X, y)

    # Make predictions on the training set itself
    train_predictions = model.predict(X)

    # Calculate evaluation metrics on the training set
    mse_train = mean_squared_error(y, train_predictions)
    r_squared_train = r2_score(y, train_predictions)

    # Optional: you can still make predictions for the test set if needed
    test_predictions = model.predict(X)

    # Store training metrics in the results dictionary
    results = {
        'coefficients': model.coef_.tolist(),
        'intercept': model.intercept_.tolist() if isinstance(model.intercept_, np.ndarray) else model.intercept_,
        'train_predictions': train_predictions.tolist(),
        'actual_train_data': y.tolist(),
        'mse_train': mse_train,  # Mean Squared Error on the training set
        'r_squared_train': r_squared_train  # R-squared on the training set
    }
    return results


