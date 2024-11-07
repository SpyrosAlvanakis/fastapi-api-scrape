from sqlalchemy import create_engine
from utils.load_secrets import load_secrets
import psycopg2
import pandas as pd
import json
import os

# ============================
#    Helper functions
# ============================

# Rescaling of data for sentiment analysis
def minmax_normalize(df, column):
    """Apply Min-Max normalization to a column in the DataFrame between -1 and 1."""
    min_val = df[column].min()
    max_val = df[column].max()
    
    if max_val - min_val == 0:
        # Avoid division by zero error
        df[column] = 0
    else:
        # Apply the normalization formula to keep the values in the [-1, 1] range
        df[column] = 2 * (df[column] - min_val) / (max_val - min_val) - 1
    
    return df

# Update the database connection function to use SQLAlchemy
def pandas_db_connection():
    """Create a SQLAlchemy engine for Pandas."""
    secrets = load_secrets()
    credentials = secrets.get('database_credentials')
    
    if not credentials:
        return None

    username = credentials.get('username')
    password = credentials.get('password')
    host = credentials.get('host')
    port = credentials.get('port')
    database = credentials.get('database')

    try:
        if not password:
            engine = create_engine(f'postgresql+psycopg2://{username}@{host}:{port}/{database}')
        else:
            engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
        return engine
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None

def connect_to_db():
    """Create a psycopg2 connection for raw database access."""
    secrets = load_secrets()
    credentials = secrets.get('database_credentials')

    if not credentials:
        return None

    username = credentials.get('username')
    password = credentials.get('password')
    host = credentials.get('host')
    port = credentials.get('port')
    database = credentials.get('database')

    try:
        if not password:
            conn = psycopg2.connect(dbname=database, user=username, host=host, port=port)
        else:
            conn = psycopg2.connect(dbname=database, user=username, password=password, host=host, port=port)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

