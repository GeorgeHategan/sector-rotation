#!/usr/bin/env python3
"""
Sector Rotation Scanner
Identifies money flow between market sectors using sector ETFs
Determines which sectors are gaining/losing strength
"""

import requests
import pandas as pd
from datetime import datetime
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# override=True ensures .env file takes precedence over existing environment variables
load_dotenv(override=True)

# Alpha Vantage API Configuration
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

if not API_KEY:
    print("ERROR: ALPHAVANTAGE_API_KEY not found in environment variables!")
    print("Please check your .env file.")
    exit(1)
BASE_URL = 'https://www.alphavantage.co/query'

# Major Sector ETFs (SPDR Sector Select ETFs)
SECTOR_ETFS = {
    'XLK': 'Technology',
    'XLF': 'Financials',
    'XLV': 'Healthcare',
    'XLE': 'Energy',
    'XLI': 'Industrials',
    'XLP': 'Consumer Staples',
    'XLY': 'Consumer Discretionary',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLU': 'Utilities',
    'XLC': 'Communication Services',
    'KRE': 'Regional Banking'
    , 'IBB': 'Biotechnology'
}

def get_intraday_data(ticker):
    """Fetch intraday data (5-min intervals) for sector analysis"""
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': ticker,
        'interval': '5min',
        'apikey': API_KEY,
        'outputsize': 'full'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Time Series (5min)' not in data:
            print(f"Error fetching {ticker}: {data.get('Note', data.get('Error Message', 'Unknown error'))}")
            return None
        
        time_series = data['Time Series (5min)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype(float)
        
        return df
    
    except Exception as e:
        print(f"Exception fetching {ticker}: {e}")
        return None


def get_daily_data(ticker, outputsize='compact'):
    """Fetch daily data for longer-term trend analysis"""
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': API_KEY,
        'outputsize': outputsize
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            print(f"DEBUG - API Response for {ticker}: {data}")
            return None
        
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype(float)
        
        return df
    
    except Exception as e:
        return None


def analyze_sector_strength(ticker, sector_name):
    """
    Analyze sector strength using multiple timeframes
    Returns metrics for rotation analysis
    """
    daily_df = get_daily_data(ticker)
    
    if daily_df is None or len(daily_df) < 20:
        return None
    
    # Calculate recent performance
    recent_20 = daily_df.tail(20).copy()
    recent_5 = daily_df.tail(5).copy()
    
    # Price changes
    price_1d = ((recent_20.iloc[-1]['Close'] - recent_20.iloc[-2]['Close']) / recent_20.iloc[-2]['Close']) * 100
    price_5d = ((recent_5.iloc[-1]['Close'] - recent_5.iloc[0]['Close']) / recent_5.iloc[0]['Close']) * 100
    price_20d = ((recent_20.iloc[-1]['Close'] - recent_20.iloc[0]['Close']) / recent_20.iloc[0]['Close']) * 100
    
    # Volume trend
    avg_vol_20d = recent_20['Volume'].mean()
    recent_vol = recent_5['Volume'].mean()
    vol_trend = ((recent_vol - avg_vol_20d) / avg_vol_20d) * 100
    
    # Relative strength (comparing to 20-day average)
    current_price = recent_20.iloc[-1]['Close']
    sma_20 = recent_20['Close'].mean()
    rs_vs_sma = ((current_price - sma_20) / sma_20) * 100
    
    # Momentum score (weighted average of timeframes)
    momentum_score = (price_1d * 0.5) + (price_5d * 0.3) + (price_20d * 0.2)
    
    # Determine trend direction
    if momentum_score > 1.5 and vol_trend > 0:
        trend = "🚀 STRONG BUY"
    elif momentum_score > 0.5:
        trend = "📈 BUYING"
    elif momentum_score < -1.5 and vol_trend > 0:
        trend = "🔻 STRONG SELL"
    elif momentum_score < -0.5:
        trend = "📉 SELLING"
    else:
        trend = "➡️  NEUTRAL"
    
    return {
        'Sector': sector_name,
        'Ticker': ticker,
        '1D_Change_%': round(price_1d, 2),
        '5D_Change_%': round(price_5d, 2),
        '20D_Change_%': round(price_20d, 2),
        'Volume_Trend_%': round(vol_trend, 2),
        'RS_vs_SMA20_%': round(rs_vs_sma, 2),
        'Momentum_Score': round(momentum_score, 2),
        'Trend': trend,
        'Current_Price': round(current_price, 2)
    }


def create_sector_heatmap(df, filename='sector_heatmap.png'):
    """Create a heatmap visualization of sector performance across multiple timeframes"""
    import numpy as np
    
    # Set dark theme
    plt.style.use('dark_background')
    
    # Prepare data for heatmap
    sectors = df['Sector'].tolist()
    
    # Create a matrix with different metrics
    data_matrix = df[['1D_Change_%', '5D_Change_%', '20D_Change_%', 'Momentum_Score', 'RS_vs_SMA20_%']].values
    
    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Create heatmap
    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=-5, vmax=5)
    
    # Set ticks and labels with light colors
    ax.set_xticks(np.arange(5))
    ax.set_yticks(np.arange(len(sectors)))
    ax.set_xticklabels(['1D Change %', '5D Change %', '20D Change %', 'Momentum', 'RS vs SMA20%'], 
                       fontsize=10, color='#e0e0e0')
    ax.set_yticklabels(sectors, fontsize=10, color='#e0e0e0')
    
    # Rotate the tick labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Performance (%)', rotation=270, labelpad=20, fontsize=10, color='#e0e0e0')
    cbar.ax.yaxis.set_tick_params(color='#e0e0e0')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#e0e0e0')
    
    # Add values in cells
    for i in range(len(sectors)):
        for j in range(5):
            value = data_matrix[i, j]
            color = 'white' if abs(value) > 3 else 'black'
            text = ax.text(j, i, f'{value:.1f}', ha="center", va="center", 
                          color=color, fontsize=8, fontweight='bold')
    
    # Add title with light color
    ax.set_title('Sector Performance Heatmap', fontsize=16, fontweight='bold', 
                 pad=20, color='#60a5fa')
    
    # Add timestamp with light color
    fig.text(0.99, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", 
             ha='right', fontsize=8, style='italic', alpha=0.7, color='#9ca3af')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    
    print(f"\n🔥 Heatmap saved to: {filename}")
    return filename


def create_sector_chart(df, filename='sector_rotation_chart.png'):
    """Create a visual chart of sector performance"""
    
    # Set dark theme
    plt.style.use('dark_background')
    
    # Create figure with 2 subplots and dark background
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), facecolor='#1a1a2e')
    ax1.set_facecolor('#1a1a2e')
    ax2.set_facecolor('#1a1a2e')
    
    # Sort by momentum score
    df_sorted = df.sort_values('Momentum_Score', ascending=True)
    
    # Chart 1: Momentum Score Bar Chart
    colors = ['#dc2626' if x < -1 else '#ef4444' if x < 0 else '#4ade80' if x < 1 else '#22c55e' 
              for x in df_sorted['Momentum_Score']]
    
    ax1.barh(df_sorted['Sector'], df_sorted['Momentum_Score'], color=colors, alpha=0.8)
    ax1.axvline(x=0, color='#9ca3af', linestyle='-', linewidth=0.8)
    ax1.set_xlabel('Momentum Score', fontsize=12, fontweight='bold', color='#e0e0e0')
    ax1.set_title('Sector Rotation Analysis - Momentum Scores', fontsize=14, 
                  fontweight='bold', pad=20, color='#60a5fa')
    ax1.grid(axis='x', alpha=0.2, color='#4b5563')
    ax1.tick_params(colors='#e0e0e0')
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax1.text(row['Momentum_Score'], i, f" {row['Momentum_Score']:+.2f}", 
                va='center', fontsize=9, fontweight='bold', color='#e0e0e0')
    
    # Chart 2: 5-Day Performance
    colors2 = ['#dc2626' if x < -2 else '#ef4444' if x < 0 else '#4ade80' if x < 2 else '#22c55e' 
               for x in df_sorted['5D_Change_%']]
    
    ax2.barh(df_sorted['Sector'], df_sorted['5D_Change_%'], color=colors2, alpha=0.8)
    ax2.axvline(x=0, color='#9ca3af', linestyle='-', linewidth=0.8)
    ax2.set_xlabel('5-Day Change (%)', fontsize=12, fontweight='bold', color='#e0e0e0')
    ax2.set_title('5-Day Price Performance by Sector', fontsize=14, 
                  fontweight='bold', pad=20, color='#60a5fa')
    ax2.grid(axis='x', alpha=0.2, color='#4b5563')
    ax2.tick_params(colors='#e0e0e0')
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax2.text(row['5D_Change_%'], i, f" {row['5D_Change_%']:+.2f}%", 
                va='center', fontsize=9, fontweight='bold', color='#e0e0e0')
    
    # Add timestamp and source with light color
    fig.text(0.99, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", 
             ha='right', fontsize=8, style='italic', alpha=0.7, color='#9ca3af')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    
    print(f"\n📊 Chart saved to: {filename}")
    return filename


def scan_sector_rotation():
    """
    Scan all sectors and identify rotation patterns
    """
    print("=" * 80)
    print("SECTOR ROTATION SCANNER")
    print("=" * 80)
    print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("Analyzing sector strength and money flow...\n")
    
    results = []
    
    for ticker, sector_name in SECTOR_ETFS.items():
        print(f"Analyzing {sector_name} ({ticker})...", end=' ')
        
        analysis = analyze_sector_strength(ticker, sector_name)
        
        if analysis:
            results.append(analysis)
            print(f"{analysis['Trend']}")
        else:
            print("❌ Failed")
        
        import time
        time.sleep(0.5)  # Rate limiting for premium API
    
    if not results:
        print("\n❌ No data available")
        return None
    
    # Convert to DataFrame and sort by momentum
    df = pd.DataFrame(results)
    df = df.sort_values('Momentum_Score', ascending=False)
    
    return df


def identify_rotation(df):
    """
    Identify rotation patterns and provide insights
    """
    print("\n" + "=" * 80)
    print("SECTOR ROTATION ANALYSIS")
    print("=" * 80)
    
    # Top performers (money flowing IN)
    print("\n🟢 STRONGEST SECTORS (Money Flowing IN):")
    print("-" * 80)
    top_3 = df.head(3)
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
    
    # Generate visualizations
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_file = f"sector_rotation_chart_{timestamp}.png"
    heatmap_file = f"sector_heatmap_{timestamp}.png"
    
    create_sector_chart(df, chart_file)
    create_sector_heatmap(df, heatmap_file)
    
    # Save results
    csv_file = f"sector_rotation_{timestamp}.csv"
    json_file = f"sector_rotation_{timestamp}.json"
    
    df.to_csv(csv_file, index=False)
    df.to_json(json_file, orient='records', indent=2)
    
    print("\n" + "=" * 80)
    print(f"✅ Results saved to:")
    print(f"   - {csv_file}")
    print(f"   - {json_file}")
    print(f"   - {chart_file}")
    print(f"   - {heatmap_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
