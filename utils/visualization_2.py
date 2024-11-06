import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import sys
import plotly.graph_objects as go
from .helpers import pandas_db_connection

# ============================
#    Visualization func 1
# ============================
def get_visualization_2():
    api_apple_query = '''SELECT * FROM aapl_stock_values;'''
    api_amd_query = '''SELECT * FROM amd_stock_values;'''
    api_nvidia_query = '''SELECT * FROM nvda_stock_values;'''

    conn = pandas_db_connection()

    #import dataframes from the database
    apple_values_df = pd.read_sql(api_apple_query, conn)
    amd_values_df = pd.read_sql(api_amd_query, conn)
    nvidia_values_df = pd.read_sql(api_nvidia_query, conn)

    #plot the graphs for the mean values of the stock data, (high+low)/2, in an interacting graph using plotly
    nvidia_mean=nvidia_values_df[['high','low']].mean(axis=1)
    amd_mean = amd_values_df[['high', 'low']].mean(axis=1)
    apple_mean = apple_values_df[['high', 'low']].mean(axis=1)

    fig1=go.Figure()
    # NVIDIA
    fig1.add_trace(go.Scatter(
        x=nvidia_values_df['date'],
        y=nvidia_mean,
        mode='markers',
        name='NVIDIA',
        line=dict(color='green', width=5),
        hovertemplate=(
            '<b>Date:</b> %{x}<br>' +  # Display Date
            '<b>Mean Value:</b> $%{y}<br>' +  # Display Mean with dollar sign
            '<b>Open:</b> $%{customdata[0]}<br>' +  # Display Open with dollar sign
            '<b>High:</b> $%{customdata[1]}<br>' +  # Display High with dollar sign
            '<b>Low:</b> $%{customdata[2]}<br>' +  # Display Low with dollar sign
            '<b>Close:</b> $%{customdata[3]}<br>' +  # Display Close with dollar sign
            '<extra></extra>'
        ),
        # Round the custom data values to 2 decimal places
        customdata=nvidia_values_df[['open', 'high', 'low', 'close']].round(2).values
    ))

    fig1.add_trace(go.Scatter(
        x=nvidia_values_df['date'],
        y=nvidia_mean,
        mode='lines',
        line=dict(color='green', width=1),
        showlegend=False
    ))

    # AMD 
    fig1.add_trace(go.Scatter(
        x=amd_values_df['date'],
        y=amd_mean,
        mode='markers',
        name='AMD',
        line=dict(color='orange', width=5),
        hovertemplate=(
            '<b>Date:</b> %{x}<br>' +
            '<b>Mean Value:</b> $%{y}<br>' +
            '<b>Open:</b> $%{customdata[0]}<br>' +
            '<b>High:</b> $%{customdata[1]}<br>' +
            '<b>Low:</b> $%{customdata[2]}<br>' +
            '<b>Close:</b> $%{customdata[3]}<br>' +
            '<extra></extra>'
        ),
        customdata=amd_values_df[['open', 'high', 'low', 'close']].round(2).values
    ))

    fig1.add_trace(go.Scatter(
        x=amd_values_df['date'],
        y=amd_mean,
        mode='lines',
        line=dict(color='orange', width=1),
        showlegend=False
    ))

    # Apple
    fig1.add_trace(go.Scatter(
        x=apple_values_df['date'],
        y=apple_mean,
        mode='markers',
        name='Apple',
        line=dict(color='grey', width=5),
        hovertemplate=(
            '<b>Date:</b> %{x}<br>' +
            '<b>Mean Value:</b> $%{y}<br>' +
            '<b>Open:</b> $%{customdata[0]}<br>' +
            '<b>High:</b> $%{customdata[1]}<br>' +
            '<b>Low:</b> $%{customdata[2]}<br>' +
            '<b>Close:</b> $%{customdata[3]}<br>' +
            '<extra></extra>'
        ),
        customdata=apple_values_df[['open', 'high', 'low', 'close']].round(2).values
    ))

    fig1.add_trace(go.Scatter(
        x=apple_values_df['date'],
        y=apple_mean,
        mode='lines',
        line=dict(color='grey', width=1),
        showlegend=False
    ))

    # Update the layout to add y-axis label
    fig1.update_layout(
        xaxis_title='Date',  # Label for the x-axis 
        yaxis_title='Value [$]',  # Label for the y-axis
        title='Stock Mean Values'  # Optional title for the plot
    )

    # Show the plot
    fig1.show()