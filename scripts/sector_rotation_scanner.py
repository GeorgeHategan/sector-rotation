#!/usr/bin/env python3
"""
=================================================================================
SECTOR ROTATION SCANNER - COMPREHENSIVE GUIDE FOR NON-PROGRAMMERS
=================================================================================

WHAT THIS SCRIPT DOES:
----------------------
This script analyzes which stock market sectors are gaining or losing strength.
Think of it as tracking where "smart money" is flowing in the market.

WHY IT MATTERS:
--------------
- When money flows INTO a sector → That sector's stocks tend to go UP
- When money flows OUT of a sector → That sector's stocks tend to go DOWN
- Understanding these flows helps you know WHAT to buy and WHEN

HOW IT WORKS:
------------
1. Downloads price data for 13 major sector ETFs (Exchange Traded Funds)
2. Calculates how much each sector has moved (up or down) over different time periods
3. Determines if money is flowing IN or OUT of each sector
4. Creates visual charts showing the strongest and weakest sectors
5. Saves all results to files for later analysis

THE 13 SECTORS WE TRACK:
------------------------
Think of these as the 13 "departments" of the stock market:
- Technology (XLK): Apple, Microsoft, tech companies
- Financials (XLF): Banks, insurance companies
- Healthcare (XLV): Hospitals, drug makers
- Energy (XLE): Oil & gas companies
- And 9 more...

=================================================================================
"""

# ============================================================================
# STEP 1: IMPORT REQUIRED LIBRARIES (External Tools)
# ============================================================================
# These are like importing toolboxes that help us do specific tasks

import requests       # Tool for downloading data from the internet
import pandas as pd   # Tool for organizing data in tables (like Excel)
from datetime import datetime  # Tool for working with dates and times
import json          # Tool for saving data in a structured format
import matplotlib    # Tool for creating charts and graphs
matplotlib.use('Agg')  # Tell matplotlib to work in background (no pop-up windows)
import matplotlib.pyplot as plt  # The actual chart-drawing tool
import os            # Tool for working with files and folders
from dotenv import load_dotenv  # Tool for loading secret API keys safely

# ============================================================================
# STEP 2: LOAD CONFIGURATION (Settings and Secrets)
# ============================================================================

# Load environment variables from .env file
# This file contains our API key (like a password) to access market data
# override=True ensures .env file takes precedence over existing environment variables
load_dotenv(override=True)

# Get our API key from the environment variables
# API_KEY is like a password that lets us download market data from Alpha Vantage
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

# Check if we have an API key - if not, stop the program with an error message
if not API_KEY:
    print("ERROR: ALPHAVANTAGE_API_KEY not found in environment variables!")
    print("Please check your .env file.")
    exit(1)

# The web address where we'll download market data from
BASE_URL = 'https://www.alphavantage.co/query'

# ============================================================================
# STEP 3: DEFINE THE 13 SECTORS WE'RE TRACKING
# ============================================================================
# This dictionary maps ticker symbols (short codes) to sector names
# Format: 'TICKER': 'Full Sector Name'

SECTOR_ETFS = {
    'XLK': 'Technology',              # Tech companies: Apple, Microsoft, NVIDIA
    'XLF': 'Financials',              # Banks & financial services: JP Morgan, Bank of America
    'XLV': 'Healthcare',              # Hospitals, drug companies: Pfizer, Johnson & Johnson
    'XLE': 'Energy',                  # Oil & gas companies: Exxon, Chevron
    'XLI': 'Industrials',             # Manufacturing, transportation: Boeing, Caterpillar
    'XLP': 'Consumer Staples',        # Everyday necessities: Procter & Gamble, Walmart
    'XLY': 'Consumer Discretionary',  # Luxury/optional items: Amazon, Tesla, Nike
    'XLB': 'Materials',               # Raw materials: Mining, chemicals, construction materials
    'XLRE': 'Real Estate',            # Property companies, REITs
    'XLU': 'Utilities',               # Electric, gas, water companies - very stable, boring
    'XLC': 'Communication Services',  # Facebook, Google, Netflix, phone companies
    'KRE': 'Regional Banking',        # Smaller local banks
    'IBB': 'Biotechnology'            # Biotech & pharmaceutical research companies
}

# ============================================================================
# NOTE: DEFENSIVE vs CYCLICAL SECTORS (Important for Analysis!)
# ============================================================================
# DEFENSIVE sectors (safe havens - people always need these):
#   - Utilities (XLU): People always need electricity
#   - Consumer Staples (XLP): People always need food, soap, etc.
#   - Healthcare (XLV): People always need medicine
#   → These do WELL when investors are SCARED (Risk-Off)
#
# CYCLICAL sectors (grow with economy):
#   - Technology (XLK): People buy more tech when economy is good
#   - Financials (XLF): Banks make more money when economy grows
#   - Consumer Discretionary (XLY): People buy luxury items when they feel rich
#   - Industrials (XLI): Manufacturing grows with economy
#   → These do WELL when investors are CONFIDENT (Risk-On)
# ============================================================================

# ============================================================================
# FUNCTION 1: GET INTRADAY DATA (For Real-Time Trading - NOT USED CURRENTLY)
# ============================================================================
def get_intraday_data(ticker):
    """
    Downloads minute-by-minute price data for a sector ETF.
    
    WHAT IT DOES:
    - Gets price data updated every 5 minutes throughout the trading day
    - Useful for day traders who need real-time information
    
    PARAMETERS:
    - ticker: The symbol of the ETF we want data for (e.g., 'XLK' for Technology)
    
    RETURNS:
    - A table (DataFrame) with columns: Open, High, Low, Close, Volume
    - Each row represents a 5-minute time period
    
    NOTE: This function is currently NOT used in the main analysis.
          We use daily data instead for more reliable long-term trends.
    """
    
    # Set up the request parameters (what we're asking for from the API)
    params = {
        'function': 'TIME_SERIES_INTRADAY',  # Tell API we want intraday data
        'symbol': ticker,                     # Which ETF (e.g., 'XLK')
        'interval': '5min',                   # Data every 5 minutes
        'apikey': API_KEY,                    # Our password to access the data
        'outputsize': 'full'                  # Get all available data (not just recent)
    }
    
    try:
        # Send the request to Alpha Vantage and get the response
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()  # Convert response to a usable format
        
        # Check if we got valid data back
        if 'Time Series (5min)' not in data:
            print(f"Error fetching {ticker}: {data.get('Note', data.get('Error Message', 'Unknown error'))}")
            return None
        
        # Extract the time series data
        time_series = data['Time Series (5min)']
        
        # Convert to a pandas DataFrame (think of it as an Excel spreadsheet)
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # Convert the index (row labels) to actual date/time objects
        df.index = pd.to_datetime(df.index)
        
        # Sort by date (oldest first, newest last)
        df = df.sort_index()
        
        # Rename columns to something more readable
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Convert all values to numbers (they come as text initially)
        df = df.astype(float)
        
        return df
    
    except Exception as e:
        # If anything goes wrong, print the error and return None
        print(f"Exception fetching {ticker}: {e}")
        return None


# ============================================================================
# FUNCTION 2: GET DAILY DATA (This is what we actually use!)
# ============================================================================
def get_daily_data(ticker, outputsize='compact'):
    """
    Downloads end-of-day price data for a sector ETF.
    
    WHAT IT DOES:
    - Gets one data point per day (the closing price at 4 PM EST)
    - More reliable for spotting longer-term trends
    - This is the MAIN function we use for analysis
    
    PARAMETERS:
    - ticker: The ETF symbol (e.g., 'XLK' for Technology)
    - outputsize: 'compact' = last 100 days, 'full' = 20+ years of data
    
    RETURNS:
    - A table with daily prices: Open, High, Low, Close, Volume
    - Each row = one trading day
    
    EXAMPLE:
    If we ask for 'XLK', we get:
        Date         Open    High    Low     Close   Volume
        2025-10-28   298.50  299.20  297.80  299.00  50000000
        2025-10-27   297.00  298.60  296.50  298.50  48000000
        ... (and so on)
    """
    
    # Set up what we're requesting from the API
    params = {
        'function': 'TIME_SERIES_DAILY',  # We want daily data (not minute-by-minute)
        'symbol': ticker,                  # Which sector ETF to download
        'apikey': API_KEY,                 # Our access key
        'outputsize': outputsize           # How much history to get
    }
    
    try:
        # Download the data from Alpha Vantage
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()  # Convert to usable format
        
        # Check if the download worked
        if 'Time Series (Daily)' not in data:
            # If not, show what went wrong
            print(f"DEBUG - API Response for {ticker}: {data}")
            return None
        
        # Extract the actual price data
        time_series = data['Time Series (Daily)']
        
        # Convert to a pandas DataFrame (like an Excel table)
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # Convert dates from text to actual date objects
        df.index = pd.to_datetime(df.index)
        
        # Sort so oldest dates are first, newest are last
        df = df.sort_index()
        
        # Rename columns to be more readable
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Convert all price/volume data from text to numbers
        df = df.astype(float)
        
        return df
    
    except Exception as e:
        # If anything breaks, return None
        return None


# ============================================================================
# FUNCTION 3: ANALYZE SECTOR STRENGTH (The Core Logic!)
# ============================================================================
def analyze_sector_strength(ticker, sector_name):
    """
    This is the HEART of the analysis! It calculates how strong or weak a sector is.
    
    WHAT IT DOES:
    - Downloads daily price data for a sector
    - Calculates price changes over 1 day, 5 days, and 20 days
    - Checks if trading volume is increasing (sign of strength) or decreasing
    - Combines all these factors into a "Momentum Score"
    - Determines if the sector is BUYING, SELLING, or NEUTRAL
    
    PARAMETERS:
    - ticker: ETF symbol (e.g., 'XLK')
    - sector_name: Human-readable name (e.g., 'Technology')
    
    RETURNS:
    - A dictionary with all the calculated metrics, or None if data unavailable
    
    KEY METRICS EXPLAINED:
    ----------------------
    1. Price Changes (1D, 5D, 20D):
       - Tells us how much the sector moved up or down
       - Example: +2.5% means sector is up 2.5% over that period
    
    2. Volume Trend:
       - Trading volume = how many shares were bought/sold
       - Increasing volume + rising price = STRONG buying pressure
       - Increasing volume + falling price = STRONG selling pressure
    
    3. Momentum Score:
       - A weighted average that gives more weight to recent moves
       - Formula: (1-day × 50%) + (5-day × 30%) + (20-day × 20%)
       - Positive score = Money flowing IN (good!)
       - Negative score = Money flowing OUT (bad!)
    """
    
    # Step 1: Download the daily price data for this sector
    daily_df = get_daily_data(ticker)
    
    # Step 2: Verify we got enough data (need at least 20 days)
    if daily_df is None or len(daily_df) < 20:
        return None  # Not enough data to analyze
    
    # ========================================================================
    # STEP 3: EXTRACT RECENT DATA FOR ANALYSIS
    # ========================================================================
    # Get the last 20 trading days (about 1 month)
    recent_20 = daily_df.tail(20).copy()
    
    # Get the last 5 trading days (1 week)
    recent_5 = daily_df.tail(5).copy()
    
    # ========================================================================
    # STEP 4: CALCULATE PRICE CHANGES (How much did price move?)
    # ========================================================================
    
    # 1-DAY PRICE CHANGE (Yesterday vs Today)
    # Formula: ((Today's Price - Yesterday's Price) / Yesterday's Price) × 100
    # Example: If it went from $100 to $102, that's +2%
    price_1d = ((recent_20.iloc[-1]['Close'] - recent_20.iloc[-2]['Close']) / recent_20.iloc[-2]['Close']) * 100
    
    # 5-DAY PRICE CHANGE (5 days ago vs Today)
    # Shows the trend over the past week
    price_5d = ((recent_5.iloc[-1]['Close'] - recent_5.iloc[0]['Close']) / recent_5.iloc[0]['Close']) * 100
    
    # 20-DAY PRICE CHANGE (20 days ago vs Today)
    # Shows the trend over the past month
    price_20d = ((recent_20.iloc[-1]['Close'] - recent_20.iloc[0]['Close']) / recent_20.iloc[0]['Close']) * 100
    
    # ========================================================================
    # STEP 5: CALCULATE VOLUME TREND (Is interest increasing?)
    # ========================================================================
    
    # Calculate average daily volume over the past 20 days
    avg_vol_20d = recent_20['Volume'].mean()
    
    # Calculate average daily volume over the past 5 days (more recent)
    recent_vol = recent_5['Volume'].mean()
    
    # Volume Trend: Is recent volume higher or lower than the 20-day average?
    # Positive % = Volume is increasing (more interest!)
    # Negative % = Volume is decreasing (less interest)
    vol_trend = ((recent_vol - avg_vol_20d) / avg_vol_20d) * 100
    
    # ========================================================================
    # STEP 6: CALCULATE RELATIVE STRENGTH (Price vs Average)
    # ========================================================================
    
    # Get today's closing price
    current_price = recent_20.iloc[-1]['Close']
    
    # Calculate the Simple Moving Average (SMA) over 20 days
    # SMA = average price over the last 20 days
    # This tells us the "normal" price level for this sector
    sma_20 = recent_20['Close'].mean()
    
    # Relative Strength vs SMA: Is the current price above or below average?
    # Positive % = Trading ABOVE average (bullish!)
    # Negative % = Trading BELOW average (bearish)
    rs_vs_sma = ((current_price - sma_20) / sma_20) * 100
    
    # ========================================================================
    # STEP 7: CALCULATE MOMENTUM SCORE (The Magic Formula!)
    # ========================================================================
    # This combines all timeframes into ONE number that shows sector strength
    # 
    # WHY WEIGHTED?
    # - Recent moves (1 day) matter more → 50% weight
    # - Short-term trend (5 days) → 30% weight  
    # - Longer trend (20 days) → 20% weight
    #
    # INTERPRETATION:
    # - Positive score = Money is flowing INTO this sector (BUY signal)
    # - Negative score = Money is flowing OUT of this sector (SELL signal)
    # - Score near 0 = Sector is flat/neutral
    #
    # EXAMPLE:
    # If 1D = +1%, 5D = +2%, 20D = +3%
    # Momentum = (1 × 0.5) + (2 × 0.3) + (3 × 0.2) = 0.5 + 0.6 + 0.6 = +1.7
    momentum_score = (price_1d * 0.5) + (price_5d * 0.3) + (price_20d * 0.2)
    
    # ========================================================================
    # STEP 8: DETERMINE TREND DIRECTION (Buy, Sell, or Neutral?)
    # ========================================================================
    # Based on momentum score AND volume, classify the sector's trend
    
    if momentum_score > 1.5 and vol_trend > 0:
        # Strong positive momentum + increasing volume = STRONG BUYING!
        trend = "🚀 STRONG BUY"
        
    elif momentum_score > 0.5:
        # Positive momentum (even without volume) = BUYING
        trend = "📈 BUYING"
        
    elif momentum_score < -1.5 and vol_trend > 0:
        # Strong negative momentum + increasing volume = STRONG SELLING!
        trend = "🔻 STRONG SELL"
        
    elif momentum_score < -0.5:
        # Negative momentum = SELLING
        trend = "📉 SELLING"
        
    else:
        # Momentum near zero = No clear direction
        trend = "➡️  NEUTRAL"
    
    # ========================================================================
    # STEP 9: PACKAGE ALL RESULTS INTO A DICTIONARY
    # ========================================================================
    # Return all the calculated metrics in an organized format
    # This dictionary will become one row in our final results table
    return {
        'Sector': sector_name,              # Full name: "Technology"
        'Ticker': ticker,                   # Symbol: "XLK"
        '1D_Change_%': round(price_1d, 2),  # Yesterday to today change
        '5D_Change_%': round(price_5d, 2),  # Last week's change
        '20D_Change_%': round(price_20d, 2),# Last month's change
        'Volume_Trend_%': round(vol_trend, 2),     # Is volume increasing?
        'RS_vs_SMA20_%': round(rs_vs_sma, 2),      # Above or below average?
        'Momentum_Score': round(momentum_score, 2), # THE KEY NUMBER!
        'Trend': trend,                     # Buy/Sell/Neutral classification
        'Current_Price': round(current_price, 2)   # Latest price
    }


# ============================================================================
# FUNCTION 4: CREATE SECTOR HEATMAP (Visual Chart #1)
# ============================================================================
def create_sector_heatmap(df, filename='sector_heatmap.png'):
    """
    Creates a colorful heatmap showing all sectors at a glance.
    
    WHAT IT DOES:
    - Shows all 13 sectors in rows
    - Shows 5 different metrics in columns (1D, 5D, 20D changes, Momentum, RS)
    - Uses colors: GREEN = good performance, RED = poor performance
    
    THINK OF IT AS:
    A "weather map" for the stock market. You can instantly see which sectors
    are "hot" (green) and which are "cold" (red).
    
    HOW TO READ IT:
    - Dark green = Strong positive performance (money flowing in)
    - Light green = Mild positive performance
    - Yellow = Neutral (no change)
    - Light red = Mild negative performance
    - Dark red = Strong negative performance (money flowing out)
    """
    import numpy as np
    
    # Set up dark theme for the chart (professional looking)
    plt.style.use('dark_background')
    
    # ========================================================================
    # PREPARE THE DATA
    # ========================================================================
    
    # Extract sector names (will be row labels)
    sectors = df['Sector'].tolist()
    
    # Extract the 5 metrics we want to display (will be columns)
    # This creates a 2D array (matrix): rows = sectors, columns = metrics
    data_matrix = df[['1D_Change_%', '5D_Change_%', '20D_Change_%', 'Momentum_Score', 'RS_vs_SMA20_%']].values
    
    # ========================================================================
    # CREATE THE CHART
    # ========================================================================
    
    # Create a figure (canvas) with specific size and dark background
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')  # Dark blue background
    
    # Create the heatmap using imshow
    # cmap='RdYlGn' = Red-Yellow-Green color scheme
    # vmin=-5, vmax=5 = Scale from -5% to +5%
    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=-5, vmax=5)
    
    # ========================================================================
    # ADD LABELS
    # ========================================================================
    
    # Set up the column labels (metrics)
    ax.set_xticks(np.arange(5))
    ax.set_xticklabels(['1D Change %', '5D Change %', '20D Change %', 'Momentum', 'RS vs SMA20%'], 
                       fontsize=10, color='#e0e0e0')
    
    # Set up the row labels (sector names)
    ax.set_yticks(np.arange(len(sectors)))
    ax.set_yticklabels(sectors, fontsize=10, color='#e0e0e0')
    
    # Rotate column labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # ========================================================================
    # ADD COLOR SCALE BAR (Legend)
    # ========================================================================
    
    # Add a color bar showing what the colors mean
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Performance (%)', rotation=270, labelpad=20, fontsize=10, color='#e0e0e0')
    cbar.ax.yaxis.set_tick_params(color='#e0e0e0')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#e0e0e0')
    
    # ========================================================================
    # ADD NUMBERS INSIDE EACH CELL
    # ========================================================================
    # Loop through each cell and add the actual number value
    
    for i in range(len(sectors)):      # For each sector (row)
        for j in range(5):              # For each metric (column)
            value = data_matrix[i, j]   # Get the value
            
            # Choose text color: white for extreme values, black for mild ones
            color = 'white' if abs(value) > 3 else 'black'
            
            # Add the text to the cell
            text = ax.text(j, i, f'{value:.1f}', ha="center", va="center", 
                          color=color, fontsize=8, fontweight='bold')
    
    # ========================================================================
    # FINAL TOUCHES
    # ========================================================================
    
    # Add title at the top
    ax.set_title('Sector Performance Heatmap', fontsize=16, fontweight='bold', 
                 pad=20, color='#60a5fa')
    
    # Add timestamp in bottom right corner showing when this was created
    fig.text(0.99, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", 
             ha='right', fontsize=8, style='italic', alpha=0.7, color='#9ca3af')
    
    # Adjust layout to prevent labels from being cut off
    plt.tight_layout()
    
    # Save the chart to a file
    # dpi=150 makes it high resolution (good quality)
    # bbox_inches='tight' ensures nothing gets cut off
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()  # Close the figure to free up memory
    
    print(f"\n🔥 Heatmap saved to: {filename}")
    return filename


# ============================================================================
# FUNCTION 5: CREATE SECTOR CHART (Visual Chart #2 - Bar Chart)
# ============================================================================
def create_sector_chart(df, filename='sector_rotation_chart.png'):
    """
    Creates a horizontal bar chart showing sector rankings.
    
    WHAT IT DOES:
    - Creates TWO charts stacked vertically:
      1. TOP: Momentum scores (our main ranking)
      2. BOTTOM: 5-day performance (short-term trend)
    
    WHY HORIZONTAL BARS?
    - Easier to read sector names on the left
    - Can see rankings at a glance (longest bar = strongest)
    
    COLOR CODING:
    - Dark green = Very strong positive
    - Light green = Positive
    - Light red = Negative
    - Dark red = Very weak negative
    
    HOW TO USE THIS CHART:
    - Look at the TOP chart first (Momentum Scores)
    - Sectors at the top = Where money is flowing TO (buy these)
    - Sectors at the bottom = Where money is flowing FROM (avoid or sell these)
    """
    
    # Set up dark theme for professional look
    plt.style.use('dark_background')
    
    # ========================================================================
    # CREATE FIGURE WITH 2 SUBPLOTS (One above the other)
    # ========================================================================
    
    # Create a canvas with 2 charts: ax1 (top) and ax2 (bottom)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), facecolor='#1a1a2e')
    ax1.set_facecolor('#1a1a2e')  # Dark background for top chart
    ax2.set_facecolor('#1a1a2e')  # Dark background for bottom chart
    
    # ========================================================================
    # SORT DATA BY MOMENTUM (Weakest to Strongest)
    # ========================================================================
    # This puts the strongest sectors at the TOP of the chart
    df_sorted = df.sort_values('Momentum_Score', ascending=True)
    
    # ========================================================================
    # CHART 1 (TOP): MOMENTUM SCORE BAR CHART
    # ========================================================================
    
    # Assign colors based on momentum score:
    # - Very negative (< -1): Dark red
    # - Negative (< 0): Light red
    # - Positive (< 1): Light green
    # - Very positive (>= 1): Dark green
    colors = ['#dc2626' if x < -1 else '#ef4444' if x < 0 else '#4ade80' if x < 1 else '#22c55e' 
              for x in df_sorted['Momentum_Score']]
    
    # Create horizontal bar chart
    ax1.barh(df_sorted['Sector'], df_sorted['Momentum_Score'], color=colors, alpha=0.8)
    
    # Add a vertical line at zero (divides positive from negative)
    ax1.axvline(x=0, color='#9ca3af', linestyle='-', linewidth=0.8)
    
    # Label the x-axis
    ax1.set_xlabel('Momentum Score', fontsize=12, fontweight='bold', color='#e0e0e0')
    
    # Add title
    ax1.set_title('Sector Rotation Analysis - Momentum Scores', fontsize=14, 
                  fontweight='bold', pad=20, color='#60a5fa')
    
    # Add grid lines for easier reading
    ax1.grid(axis='x', alpha=0.2, color='#4b5563')
    ax1.tick_params(colors='#e0e0e0')  # Make tick marks visible
    
    # Add value labels on each bar (shows exact number)
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax1.text(row['Momentum_Score'], i, f" {row['Momentum_Score']:+.2f}", 
                va='center', fontsize=9, fontweight='bold', color='#e0e0e0')
    
    # ========================================================================
    # CHART 2 (BOTTOM): 5-DAY PERFORMANCE BAR CHART
    # ========================================================================
    
    # Assign colors based on 5-day change (different thresholds)
    colors2 = ['#dc2626' if x < -2 else '#ef4444' if x < 0 else '#4ade80' if x < 2 else '#22c55e' 
               for x in df_sorted['5D_Change_%']]
    
    # Create horizontal bar chart for 5-day performance
    ax2.barh(df_sorted['Sector'], df_sorted['5D_Change_%'], color=colors2, alpha=0.8)
    
    # Add vertical line at zero
    ax2.axvline(x=0, color='#9ca3af', linestyle='-', linewidth=0.8)
    
    # Label the x-axis
    ax2.set_xlabel('5-Day Change (%)', fontsize=12, fontweight='bold', color='#e0e0e0')
    
    # Add title
    ax2.set_title('5-Day Price Performance by Sector', fontsize=14, 
                  fontweight='bold', pad=20, color='#60a5fa')
    
    # Add grid lines
    ax2.grid(axis='x', alpha=0.2, color='#4b5563')
    ax2.tick_params(colors='#e0e0e0')
    
    # Add value labels on each bar
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax2.text(row['5D_Change_%'], i, f" {row['5D_Change_%']:+.2f}%", 
                va='center', fontsize=9, fontweight='bold', color='#e0e0e0')
    
    # ========================================================================
    # FINAL TOUCHES
    # ========================================================================
    
    # Add timestamp showing when the chart was created
    fig.text(0.99, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", 
             ha='right', fontsize=8, style='italic', alpha=0.7, color='#9ca3af')
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Save to file
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    
    print(f"\n📊 Chart saved to: {filename}")
    return filename


# ============================================================================
# FUNCTION 6: SCAN ALL SECTORS (Main Data Collection Function)
# ============================================================================
def scan_sector_rotation():
    """
    Scans all 13 sectors and collects their performance data.
    
    WHAT IT DOES:
    This is the "workhorse" function that:
    1. Loops through all 13 sector ETFs
    2. Downloads price data for each one
    3. Calculates strength metrics for each one
    4. Compiles everything into one organized table
    5. Sorts sectors from strongest to weakest
    
    THINK OF IT AS:
    Like checking the temperature in 13 different cities and making a ranked list
    from hottest to coldest.
    
    RETURNS:
    - A pandas DataFrame (like an Excel table) with all sector data
    - Sorted by Momentum Score (best sectors first)
    - Returns None if something goes wrong
    """
    
    # ========================================================================
    # PRINT HEADER INFORMATION
    # ========================================================================
    print("=" * 80)
    print("SECTOR ROTATION SCANNER")
    print("=" * 80)
    print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("Analyzing sector strength and money flow...\n")
    
    # ========================================================================
    # STEP 1: CREATE EMPTY LIST TO STORE RESULTS
    # ========================================================================
    # We'll add one entry for each sector
    results = []
    
    # ========================================================================
    # STEP 2: LOOP THROUGH ALL 13 SECTORS
    # ========================================================================
    # For each sector in our SECTOR_ETFS dictionary...
    for ticker, sector_name in SECTOR_ETFS.items():
        # ticker = 'XLK', sector_name = 'Technology' (example)
        
        # Show what we're analyzing
        print(f"Analyzing {sector_name} ({ticker})...", end=' ')
        
        # Call the analyze_sector_strength function for this sector
        # This returns a dictionary with all the calculated metrics
        analysis = analyze_sector_strength(ticker, sector_name)
        
        # Check if we got valid data back
        if analysis:
            # If successful, add it to our results list
            results.append(analysis)
            # Show the trend (Buy/Sell/Neutral)
            print(f"{analysis['Trend']}")
        else:
            # If it failed, show error
            print("❌ Failed")
        
        # ====================================================================
        # RATE LIMITING: Wait 0.5 seconds before next API call
        # ====================================================================
        # Why? APIs have limits on how fast you can request data.
        # Waiting prevents us from getting blocked or throttled.
        import time
        time.sleep(0.5)  # Pause for half a second
    
    # ========================================================================
    # STEP 3: CHECK IF WE GOT ANY DATA
    # ========================================================================
    if not results:
        print("\n❌ No data available")
        return None  # Exit if no sectors worked
    
    # ========================================================================
    # STEP 4: CONVERT TO DATAFRAME AND SORT
    # ========================================================================
    # Convert our list of dictionaries into a pandas DataFrame (table)
    df = pd.DataFrame(results)
    
    # Sort by Momentum Score: highest (best) first, lowest (worst) last
    df = df.sort_values('Momentum_Score', ascending=False)
    
    # Return the completed table
    return df


# ============================================================================
# FUNCTION 7: IDENTIFY ROTATION PATTERNS (Interpret the Results)
# ============================================================================
def identify_rotation(df):
    """
    Analyzes the sector data and explains what it means in plain English.
    
    WHAT IT DOES:
    - Identifies which sectors are strongest (where money is flowing TO)
    - Identifies which sectors are weakest (where money is flowing FROM)
    - Determines if the market is Risk-On (bullish) or Risk-Off (bearish)
    - Provides actionable insights
    
    PARAMETERS:
    - df: The DataFrame with all sector data (from scan_sector_rotation)
    
    OUTPUT:
    - Prints analysis to the console
    - Does not return anything (display only)
    
    KEY CONCEPTS:
    -------------
    RISK-ON: Investors are confident, buying cyclical sectors (Tech, Finance)
    RISK-OFF: Investors are scared, buying defensive sectors (Utilities, Staples)
    """
    
    # ========================================================================
    # PRINT HEADER
    # ========================================================================
    print("\n" + "=" * 80)
    print("SECTOR ROTATION ANALYSIS")
    print("=" * 80)
    
    # ========================================================================
    # SECTION 1: TOP 3 STRONGEST SECTORS
    # ========================================================================
    print("\n🟢 STRONGEST SECTORS (Money Flowing IN):")
    print("-" * 80)
    
    # Get the top 3 sectors (they're already sorted, so just take first 3 rows)
    top_3 = df.head(3)
    
    # Loop through and display each one
    for idx, row in top_3.iterrows():
        tradingview_url = f"https://www.tradingview.com/chart/?symbol={row['Ticker']}"
        print(f"  {row['Trend']} {row['Sector']:25s} | 1D: {row['1D_Change_%']:+6.2f}% | 5D: {row['5D_Change_%']:+6.2f}% | Momentum: {row['Momentum_Score']:+6.2f}")
        print(f"     📊 Chart: {tradingview_url}")
    
    # Bottom performers (money flowing OUT)
    print("\n🔴 WEAKEST SECTORS (Money Flowing OUT):")
    print("-" * 80)
    bottom_3 = df.tail(3)
    for idx, row in bottom_3.iterrows():
        tradingview_url = f"https://www.tradingview.com/chart/?symbol={row['Ticker']}"
        print(f"  {row['Trend']} {row['Sector']:25s} | 1D: {row['1D_Change_%']:+6.2f}% | 5D: {row['5D_Change_%']:+6.2f}% | Momentum: {row['Momentum_Score']:+6.2f}")
        print(f"     📊 Chart: {tradingview_url}")
    
    # Overall market sentiment
    avg_momentum = df['Momentum_Score'].mean()
    print(f"\n📊 OVERALL MARKET MOMENTUM: {avg_momentum:+.2f}")
    
    if avg_momentum > 0.5:
        print("   ✅ Market is in RISK-ON mode (bullish)")
    elif avg_momentum < -0.5:
        print("   ⚠️  Market is in RISK-OFF mode (bearish)")
    else:
        print("   ➡️  Market is NEUTRAL (consolidating)")
    
    # Rotation insights
    print("\n💡 ROTATION INSIGHTS:")
    print("-" * 80)
    
    # Check defensive vs cyclical
    defensive = df[df['Sector'].isin(['Utilities', 'Consumer Staples', 'Healthcare'])]
    cyclical = df[df['Sector'].isin(['Technology', 'Consumer Discretionary', 'Industrials', 'Financials'])]
    
    defensive_avg = defensive['Momentum_Score'].mean()
    cyclical_avg = cyclical['Momentum_Score'].mean()
    
    if cyclical_avg > defensive_avg + 0.5:
        print("  📈 CYCLICAL sectors outperforming → RISK-ON environment")
    elif defensive_avg > cyclical_avg + 0.5:
        print("  🛡️  DEFENSIVE sectors outperforming → RISK-OFF environment")
    else:
        print("  ⚖️  Balanced performance across cyclical and defensive sectors")
    
    # Check for sector rotation
    top_sector = df.iloc[0]
    bottom_sector = df.iloc[-1]
    
    print(f"\n  🎯 TODAY'S FLOW: Money rotating FROM {bottom_sector['Sector']} TO {top_sector['Sector']}")


def main():
    """Main execution function"""
    
    # Scan all sectors
    df = scan_sector_rotation()
    
    if df is None:
        return
    
    # Display full results
    print("\n" + "=" * 80)
    print("DETAILED SECTOR METRICS")
    print("=" * 80)
    print(df.to_string(index=False))
    
    # Identify rotation patterns
    identify_rotation(df)
    
    # ========================================================================
    # STEP 3: GENERATE VISUALIZATIONS (Create the Charts!)
    # ========================================================================
    # Create a unique timestamp for this scan (so files don't overwrite each other)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_file = f"output/charts/sector_rotation_chart_{timestamp}.png"
    heatmap_file = f"output/heatmaps/sector_heatmap_{timestamp}.png"
    
    # Create the charts using the data we collected
    create_sector_chart(df, chart_file)
    create_sector_heatmap(df, heatmap_file)
    
    # ========================================================================
    # STEP 4: SAVE DATA TO FILES
    # ========================================================================
    # Save in multiple formats for different uses:
    
    # CSV format (can open in Excel)
    csv_file = f"data/historical/sector_rotation_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    
    # JSON format (for websites and AI analysis)
    json_file = f"data/historical/sector_rotation_{timestamp}.json"
    df.to_json(json_file, orient='records', indent=2)
    
    # ========================================================================
    # STEP 5: PRINT SUCCESS MESSAGE
    # ========================================================================
    print("\n" + "=" * 80)
    print(f"✅ Results saved to:")
    print(f"   - {csv_file}")
    print(f"   - {json_file}")
    print(f"   - {chart_file}")
    print(f"   - {heatmap_file}")
    print("=" * 80)


# ============================================================================
# PROGRAM ENTRY POINT (Where Execution Starts)
# ============================================================================
# This special block runs ONLY when you execute this script directly
# (not when it's imported as a module into another script)

if __name__ == "__main__":
    # ========================================================================
    # EXECUTION FLOW SUMMARY (The Big Picture)
    # ========================================================================
    # When you run this script, here's what happens step-by-step:
    #
    # 1. Load environment variables (API keys) from .env file
    # 2. Define the 13 sectors we're tracking
    # 3. Call main() function
    #    ↓
    # 4. main() calls scan_sector_rotation()
    #    ↓
    # 5. scan_sector_rotation() loops through all 13 sectors:
    #    - For each sector, calls analyze_sector_strength()
    #    - Calculates price changes, volume trends, momentum scores
    #    - Compiles all data into a DataFrame (table)
    #    ↓
    # 6. main() calls identify_rotation()
    #    - Prints top 3 strongest sectors
    #    - Prints bottom 3 weakest sectors  
    #    - Determines Risk-On vs Risk-Off market
    #    - Shows where money is rotating FROM → TO
    #    ↓
    # 7. main() creates visualizations:
    #    - Bar chart (momentum scores)
    #    - Heatmap (multi-timeframe view)
    #    ↓
    # 8. main() saves everything:
    #    - CSV file (Excel-compatible)
    #    - JSON file (for AI analysis & website)
    #    - PNG images (charts)
    #    ↓
    # 9. Done! Files are in output/ and data/ folders
    #
    # RESULT: You now know which sectors are strong/weak and where to invest!
    # ========================================================================
    
    main()  # Start the program!
