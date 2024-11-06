import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
from .helpers import pandas_db_connection, minmax_normalize

# ============================
#    Visualization func 1
# ============================
def get_visualization_1(rescale: bool) -> BytesIO:
    """Generates the NVIDIA Stock vs Sentiment Scores plot.

    Args:
        normalize (bool): Whether to normalize sentiment scores.

    Returns:
        BytesIO: The image data in memory as a PNG.
    """
    conn = pandas_db_connection()

    # Query to get NVIDIA stock data
    query_nvidia_stock = "SELECT date, close FROM nvda_stock_values"
    df_nvidia_stock = pd.read_sql_query(query_nvidia_stock, conn)

    # Query to get sentiment scores from all the sources
    query_nvidia_news_api = "SELECT date, sentiment_score FROM nvidia_news_api"
    query_nvidia_original = "SELECT date, sentiment_score FROM nvidia_originalsite_scrape"
    query_ft_nvidia = "SELECT date, sentiment_score FROM nvidia_fintimes_scrape"

    df_news_api = pd.read_sql_query(query_nvidia_news_api, conn)
    df_original = pd.read_sql_query(query_nvidia_original, conn)
    df_ft = pd.read_sql_query(query_ft_nvidia, conn)

    # Ensure 'date' is not the index before converting to datetime
    for df in [df_nvidia_stock, df_news_api, df_original, df_ft]:
        if df.index.name == 'date':
            df.reset_index(inplace=True)

    # Convert 'date' columns to datetime format and extract year-month-day
    df_nvidia_stock['date'] = pd.to_datetime(df_nvidia_stock['date']).dt.date
    df_news_api['date'] = pd.to_datetime(df_news_api['date']).dt.date
    df_original['date'] = pd.to_datetime(df_original['date']).dt.date
    df_ft['date'] = pd.to_datetime(df_ft['date']).dt.date

    # Group by date and calculate the mean sentiment score, then add the source column
    df_news_api_daily = df_news_api.groupby('date', as_index=False)['sentiment_score'].mean()
    df_news_api_daily['source'] = 'api_news'

    df_original_daily = df_original.groupby('date', as_index=False)['sentiment_score'].mean()
    df_original_daily['source'] = 'nvidia_original'

    df_ft_daily = df_ft.groupby('date', as_index=False)['sentiment_score'].mean()
    df_ft_daily['source'] = 'ft_nvidia'

    # Conditionally normalize the sentiment scores
    if rescale:
        df_news_api_daily = minmax_normalize(df_news_api_daily, 'sentiment_score')
        df_original_daily = minmax_normalize(df_original_daily, 'sentiment_score')
        df_ft_daily = minmax_normalize(df_ft_daily, 'sentiment_score')    
    # Concatenate all the sentiment DataFrames
    df_sentiments = pd.concat([df_news_api_daily, df_original_daily, df_ft_daily])

    # Sort by date
    df_sentiments.sort_values(by='date', inplace=True)
    df_nvidia_stock.sort_values(by='date', inplace=True)

    # Plotting the data
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Stock prices on the first Y-axis
    ax1.plot(df_nvidia_stock['date'], df_nvidia_stock['close'], color='b', label='NVIDIA Stock Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NVIDIA Stock Price', color='b')

    # Second Y-axis for sentiment scores
    ax2 = ax1.twinx()
    
    # Scatter plot for each sentiment source
    for source in df_sentiments['source'].unique():
        source_data = df_sentiments[df_sentiments['source'] == source]
        if source == 'api_news':
            ax2.plot(source_data['date'], source_data['sentiment_score'], label='API Sentiment', color='red', alpha=0.5)
        elif source == 'nvidia_original':
            ax2.plot(source_data['date'], source_data['sentiment_score'], label='NVIDIA site Sentiment', color='green', alpha=0.5)
        elif source == 'ft_nvidia':
            ax2.plot(source_data['date'], source_data['sentiment_score'], label='FT Sentiment', color='black', alpha=0.5)
    
    if rescale:
        ax2.set_ylabel('Sentiment Score (rescale)', color='r')
    else: 
        ax2.set_ylabel('Sentiment Score', color='r')

    # Tight layout for better spacing
    fig.tight_layout()

    # Set the title and add a legend
    plt.title("NVIDIA Stock Price vs Sentiment Scores (Rescaled)")
    ax2.legend(loc='upper left')

    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return buf
