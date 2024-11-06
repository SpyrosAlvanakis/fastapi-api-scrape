from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from starlette.responses import StreamingResponse
import importlib
import utils

# ============================
#    FastAPI app
# ============================
app = FastAPI()

class DateRange(BaseModel):
    start_date: str
    end_date: str

class DatabaseRequest(BaseModel):
    db_name: str

# ============================
# Endpoints: Post
# ============================

# Endpoint 1: Scrape Financial Times NVIDIA news
@app.post(
    "/scrape_nvidia_ft",
    summary="Scrape Financial Times NVIDIA News",
    description="""
        This endpoint scrapes news articles related to NVIDIA from the Financial Times website.
        The user can specify a date range using `start_date` and `end_date` in the request body in the `Year-Month-Day` format.
        The scraped data includes article titles, publication dates, and sentiment analysis.
        The data will be inserted into the PostgreSQL database.
    """
)
async def post_scrape_nvidia_ft(date_range: DateRange):
    try:
        result = utils.scrape_nvidia_ft(date_range.start_date, date_range.end_date)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 2: Scrape NVIDIA stock data via yfinance
@app.post(
    "/get_nvidia_stock",
    summary="Api call to NVIDIA-APPLE-AMD Stock Data",
    description="""
        This endpoint make API calls for historical stock data for NVIDIA-APPLE-AMD using the `yfinance` API.
        The user can specify a date range using `start_date` and `end_date` in the request body in the `Year-Month-Day` format.
        The stock data includes open, close, high, low prices, and trading volume for the specified date range.
        The data will be inserted into the PostgreSQL database.
    """
)
async def post_scrape_nvidia_stock(date_range: DateRange):
    try:
        result = utils.scrape_nvidia_stock(date_range.start_date, date_range.end_date)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 3: Fetch NVIDIA news via Finnhub API
@app.post(
    "/get_nvidia_news_via_api",
    summary="Fetch NVIDIA News via Finnhub API",
    description="""
        This endpoint fetches news articles related to NVIDIA using the Finnhub API.
        The user can specify a date range using `start_date` and `end_date` in the request body in the `Year-Month-Day` format.
        The API returns news headlines, publication dates, URLs, and sentiment scores.
        The data will be inserted into the PostgreSQL database for future analysis.
    """
)
async def post_get_nvidia_news_via_api(date_range: DateRange):
    try:
        result = utils.get_nvidia_news_via_api(date_range.start_date, date_range.end_date)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 4: Scrape NVIDIA's official site
@app.post(
    "/scrape_nvidia_news_site",
    summary="Fetch NVIDIA News from the official NVIDIA site",
        description="""
            This endpoint scrapes news articles related to NVIDIA from the official NVIDIA site.
            The user can specify a date range using `start_date` and `end_date` in the request body in the `Year-Month-Day` format.
            The API returns news headlines, publication dates, URLs, and sentiment scores.
            The data will be inserted into the PostgreSQL database for future analysis.
        """
    )
async def post_scrape_nvidia_news_site(date_range: DateRange):
    try:
        result = utils.scrape_nvidia_news_site(date_range.start_date, date_range.end_date)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ============================
# Endpoints: Get
# ============================

# Endpoint 1: Visualization 1 - NVIDIA Stock and Sentiment Scores Plot
@app.get(
    "/visualization_1",
    summary="NVIDIA Stock & Sentiment Scores Plot",
    description="""
        This endpoint generates a 3-axis plot showing:
        1. The NVIDIA stock values for each day.
        2. The mean sentiment scores for each day from three different sources (API news, NVIDIA original site, and Financial Times).
        3. The dates.
        Optionally, the sentiment scores can be rescaled between -1 and 1 by setting the `rescale` parameter to True.
    """,
)
async def visualization_sent_vs_date(rescale: bool = Query(False, description="Whether to rescale sentiment scores between -1 and 1")):
    try:
        # Call the get_visualization function and pass the rescale parameter
        image_buffer = utils.get_visualization_1(rescale)
        
        # Return the image as a StreamingResponse
        return StreamingResponse(image_buffer, media_type="image/png")
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 2: Visualization 2 - Stock Comparison for NVIDIA, Apple, and AMD
@app.get(
    "/visualization_2",
    summary="Stock Comparison: NVIDIA, Apple, and AMD",
    description="""
        This endpoint generates a plot comparing the stock values of NVIDIA, Apple, and AMD for each day.
        The plot includes the daily stock prices as well as their high and low values.
    """,
)
async def get_visualisation_2():
    try:
        # Call the actual visualization function (assume it's defined elsewhere)
        utils.get_visualization_2()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "Data visualisation completed successfully."}


# Endpoint 3: Analysis 1 - Simple Linear Regression Model
@app.get(
    "/analysis_1",
    summary="Linear Regression Analysis of NVIDIA Stock",
    description="""
        This endpoint runs a simple linear regression model to predict NVIDIA stock prices based on sentiment scores from different sources.
        The result is returned as a JSON object containing:
        1. The model's coefficients.
        2. The intercept.
        3. Predictions for the last 30 percent of days.
        4. Actual stock prices for the last 30 percent of days.
        5. The dates for the last 30 percent of days.
    """,
)
async def linear_regression_analysis():
    try:
        # Call the linear_regression_analysis function and pass the rescale parameter
        result = utils.linear_regression_analysis()
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        if "ValueError: Out of range float values are not JSON compliant: nan" in str(e):
            raise HTTPException(status_code=400, detail="Need more data to predict stock prices.")
        else:
            raise HTTPException(status_code=500, detail="Error generating the linear regression analysis")



# Endpoint 4: Analysis 2 - Correlation Between Sentiment Scores and Stock Prices
@app.get(
    "/analysis_2",
    summary="Correlation Between Sentiment Scores and NVIDIA Stock",
    description="""
        This endpoint computes the correlation between sentiment scores from different sources (API news, NVIDIA original site, and Financial Times) 
        and NVIDIA stock values on a per-day basis.
        The result is returned as a JSON object containing correlation values.
    """,
)
async def sentiment_analysis():
    try:
        return utils.sentiment_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

