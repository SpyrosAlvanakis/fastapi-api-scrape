import pandas as pd
import numpy as np
from .helpers import pandas_db_connection

# ============================
#    Analysis func 2
# ============================

def safe_value(value, label="value"):
    """In case of near dates the scarcity of data can cause the pandas correlatin method to produce NaN values 
    which will cause the program to crash. This function will replace NaN values with 0. An extra security net is added
    by wraping the return statement in a try-except block."""

    if np.isnan(value):
        print(f"NaN detected in {label}, replacing with 0.")
        return 0
    else:
        return float(value)
    

def sentiment_analysis(): #TODO ADD DAY SHIFT AS A PARAMETER MAYBE

    conn = pandas_db_connection()

#=========================================FINANCIAL TIMES DATA ============================================

    query_ft = f'''SELECT * FROM nvidia_fintimes_scrape'''
    query_nvidia_stocks = f'''SELECT * FROM  nvda_stock_values; '''

    # Import dataframes from the database
    ft_nvidia_values_df = pd.read_sql_query(query_ft, conn)
    nvidia_values_df = pd.read_sql_query(query_nvidia_stocks, conn)
    # Convert 'date' columns to datetime
    ft_nvidia_values_df['date'] = pd.to_datetime(ft_nvidia_values_df['date']).dt.date
    nvidia_values_df['date'] = pd.to_datetime(nvidia_values_df['date']).dt.date

    # Select the 'date' and 'sentiment_score' columns in the correct way
    ft_nvidia_values_df = ft_nvidia_values_df[['date', 'sentiment_score']]

    # Group 'ft_nvidia_values_df' by 'date' and calculate the mean for sentiment_score
    ft_nvidia_values_df = ft_nvidia_values_df.groupby('date').mean()
    # Main_Value-sentiment correlation

    #We can create a new df that will contain the mean value of the stock data and the sentiment value for each day, but datetime doesn not match
    #so we have to find a way to match the dates of the two dataframes. 

    value_sentiment_df = pd.merge(ft_nvidia_values_df, nvidia_values_df, on='date', how='outer')
    value_sentiment_df=value_sentiment_df.dropna(subset=['low'])
    value_sentiment_df['mean']=value_sentiment_df[['high','low']].mean(axis=1)
    # value_sentiment_df['mean'] = value_sentiment_df[['high', 'low']].mean(axis=1)
    # clean_sentiment_df=value_sentiment_df[['date','mean','low','high', 'sentiment_score']]
    if 'sentiment_score' in value_sentiment_df.columns:
        value_sentiment_df['sentiment_score'] = value_sentiment_df['sentiment_score'].fillna(method='ffill').fillna(method='bfill')




#===================================== NVIDIA NEWS API========================================================================

    query_news_api = f'''SELECT date, sentiment_score FROM nvidia_news_api;'''

    nvidia_news_api_df=pd.read_sql_query(query_news_api, conn)
    nvidia_news_api_df['date']=pd.to_datetime(nvidia_news_api_df['date']).dt.date
    nvidia_news_api_df=nvidia_news_api_df[['date','sentiment_score']]
    nvidia_news_api_df=nvidia_news_api_df.groupby('date').mean()
    nvidia_news_score_value=pd.merge(nvidia_values_df,nvidia_news_api_df, on='date', how='outer')
    nvidia_news_score_value=nvidia_news_score_value.dropna(subset='low')
    nvidia_news_score_value['mean']=nvidia_news_score_value[['high','low']].mean(axis=1)
    if 'sentiment_score' in nvidia_news_score_value.columns:
        nvidia_news_score_value['sentiment_score'] = nvidia_news_score_value['sentiment_score'].fillna(method='ffill').fillna(method='bfill')

#==================================== NVIDIA ORIGINAL SITE ===================================================================

    query_news_original = f'''SELECT date, sentiment_score FROM nvidia_originalsite_scrape;'''

    nvidia_original_df= pd.read_sql_query(query_news_original, conn)
    nvidia_original_df['date']=pd.to_datetime(nvidia_original_df['date']).dt.date
    nvidia_original_df=nvidia_original_df[['date','sentiment_score']]
    nvidia_original_df=nvidia_original_df.groupby('date').mean()
    nvidia_original_df=pd.merge(nvidia_original_df,nvidia_values_df,on='date', how='outer')
    
    nvidia_original_df=nvidia_original_df.dropna(subset='low')
    nvidia_original_df['mean']=nvidia_original_df[['high','low']].mean(axis=1)
    if 'sentiment_score' in nvidia_original_df.columns:
        nvidia_original_df['sentiment_score'] = nvidia_original_df['sentiment_score'].fillna(method='ffill').fillna(method='bfill')


#============================================== CORRELATIONS =================================================================

#FT
    MeanValue_Sentiment_Correlation = value_sentiment_df[['mean', 'sentiment_score']].corr().iloc[0, 1]
    CloseValue_Sentiment_Correlation = value_sentiment_df[['close', 'sentiment_score']].corr().iloc[0, 1]
    value_sentiment_df['prev_day_sentiment_score'] = value_sentiment_df['sentiment_score'].shift(1)
    # Calculate the correlation between the sentiment score of the previous day and the stock value of the current day
    PrevDaySentiment_mean_Correlation = value_sentiment_df[['mean', 'prev_day_sentiment_score']].corr().iloc[0, 1]
    # Calculate the correlation between the sentiment score of the previous day and the stock open value of the current day
    PrevDaySentiment_Open_Correlation = value_sentiment_df[['open', 'prev_day_sentiment_score']].corr().iloc[0, 1]
    # Calculate the correlation between the sentiment score of the previous day and the stock close value of the current day
    PrevDaySentiment_Close_Correlation = value_sentiment_df[['close', 'prev_day_sentiment_score']].corr().iloc[0, 1]

#API
    api_mean_correlation=nvidia_news_score_value[['mean','sentiment_score']].corr().iloc[0,1]
    api_close_correlation=nvidia_news_score_value[['close','sentiment_score']].corr().iloc[0,1]
    nvidia_news_score_value['prev_day_sentiment_score']=nvidia_news_score_value['sentiment_score'].shift(1)
    api_mean_previous_score_correlation=nvidia_news_score_value[['mean','prev_day_sentiment_score']].corr().iloc[0,1]
    api_open_previous_score_correlation=nvidia_news_score_value[['open','prev_day_sentiment_score']].corr().iloc[0,1]
    api_close_previous_score_correlation=nvidia_news_score_value[['close','prev_day_sentiment_score']].corr().iloc[0,1]

#ORIGINAL 

    origin_mean_sentiment_corr=nvidia_original_df[['mean','sentiment_score']].corr().iloc[0,1]
    origin_close_sentiment_corr=nvidia_original_df[['close','sentiment_score']].corr().iloc[0,1]
    nvidia_original_df['prev_day_sentiment_score']=nvidia_original_df['sentiment_score'].shift(1)
    origin_mean_prevscore_corr=nvidia_original_df[['mean','prev_day_sentiment_score']].corr().iloc[0,1]
    origin_open_prevscore_corr=nvidia_original_df[['open','prev_day_sentiment_score']].corr().iloc[0,1]
    origin_close_prevscore_corr=nvidia_original_df[['close','prev_day_sentiment_score']].corr().iloc[0,1]


#=============================================== RETURN ================================================================

    try:
        ft_dict = {
            "[FT] concurrent mean value - sentiment correlation": safe_value(MeanValue_Sentiment_Correlation.round(2)),
            "[FT] concurrent close value - sentiment correlation": safe_value(CloseValue_Sentiment_Correlation.round(2)),
            "[FT] preceding sentiment - mean value correlation": safe_value(PrevDaySentiment_mean_Correlation.round(2)),
            "[FT] preceding sentiment - open value correlation": safe_value(PrevDaySentiment_Open_Correlation.round(2)),
            "[FT] preceding sentiment - close value correlation": safe_value(PrevDaySentiment_Close_Correlation.round(2))
        }
    except Exception as e:
        ft_dict = {
            "[FT] concurrent mean value - sentiment correlation": 0,
            "[FT] concurrent close value - sentiment correlation": 0,
            "[FT] preceding sentiment - mean value correlation": 0,
            "[FT] preceding sentiment - open value correlation": 0,
            "[FT] preceding sentiment - close value correlation": 0
        }

    try:
        news_api_dict = {
            "[news api] concurrent mean value - sentiment correlation": safe_value(api_mean_correlation.round(2)),
            "[news api] concurrent close value - sentiment correlation": safe_value(api_close_correlation.round(2)),
            "[news api] preceding sentiment - mean value correlation": safe_value(api_mean_previous_score_correlation.round(2)),
            "[news api] preceding sentiment - open value correlation": safe_value(api_open_previous_score_correlation.round(2)),
            "[news api] preceding sentiment - close value correlation": safe_value(api_close_previous_score_correlation.round(2))
        }
    except Exception as e:
        news_api_dict = {
            "[news api] concurrent mean value - sentiment correlation": 0,
            "[news api] concurrent close value - sentiment correlation": 0,
            "[news api] preceding sentiment - mean value correlation": 0,
            "[news api] preceding sentiment - open value correlation": 0,
            "[news api] preceding sentiment - close value correlation": 0
        }

    try:
        original_dict = {
            "[original] concurrent mean value - sentiment correlation": safe_value(origin_mean_sentiment_corr.round(2)),
            "[original] concurrent close value - sentiment correlation": safe_value(origin_close_sentiment_corr.round(2)),
            "[original] preceding sentiment - mean value correlation": safe_value(origin_mean_prevscore_corr.round(2)),
            "[original] preceding sentiment - open value correlation": safe_value(origin_open_prevscore_corr.round(2)),
            "[original] preceding sentiment - close value correlation": safe_value(origin_close_prevscore_corr.round(2))
        }
    except Exception as e:
        original_dict = {
            "[original] concurrent mean value - sentiment correlation": 0,
            "[original] concurrent close value - sentiment correlation": 0,
            "[original] preceding sentiment - mean value correlation": 0,
            "[original] preceding sentiment - open value correlation": 0,
            "[original] preceding sentiment - close value correlation": 0
        }

    #It's obvious that zeroe

    # Return the merged dictionary
    merged_dict = {
        "FT": ft_dict,
        "news api": news_api_dict,
        "original": original_dict
    }

    return merged_dict

