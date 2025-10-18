#!/usr/bin/env python3
"""
Sector Rotation Scanner with ClickUp Integration
==================================================

Scans sector ETFs for rotation patterns and automatically posts:
1. Sector analysis results
2. Chart visualization
3. Trading recommendations

to your ClickUp dashboard.

Dashboard: https://app.clickup.com/90151783954/dashboards/2kyqe3gj-215
"""

import os
import sys
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
# override=True ensures .env file takes precedence over existing environment variables
load_dotenv(override=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Alpha Vantage API
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

# ClickUp Configuration
CLICKUP_API_TOKEN = os.environ.get('CLICKUP_API_TOKEN', '')
CLICKUP_LIST_ID = os.environ.get('CLICKUP_LIST_ID', '')  # Will need to set this

# Major Sector ETFs
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
    'KRE': 'Regional Banks',
    'IBB': 'Biotech'
}

# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_sector_data(symbol: str) -> pd.DataFrame:
    """Fetch daily data for sector ETF."""
    try:
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            return None
        
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        return df
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


# ============================================================================
# SECTOR ANALYSIS
# ============================================================================

def calculate_sector_metrics(df: pd.DataFrame, period: int = 20) -> dict:
    """Calculate performance metrics for a sector."""
    if df is None or len(df) < period:
        return None
    
    current_price = df['close'].iloc[-1]
    
    # Performance metrics
    metrics = {
        '1_day': ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100 if len(df) >= 2 else 0,
        '5_day': ((df['close'].iloc[-1] / df['close'].iloc[-6]) - 1) * 100 if len(df) >= 6 else 0,
        '20_day': ((df['close'].iloc[-1] / df['close'].iloc[-21]) - 1) * 100 if len(df) >= 21 else 0,
        'current_price': current_price,
        'avg_volume': df['volume'].tail(20).mean()
    }
    
    # Relative strength
    sma_20 = df['close'].tail(20).mean()
    metrics['vs_sma20'] = ((current_price / sma_20) - 1) * 100
    
    # Momentum
    recent_high = df['high'].tail(20).max()
    recent_low = df['low'].tail(20).min()
    metrics['pct_from_high'] = ((current_price / recent_high) - 1) * 100
    metrics['pct_from_low'] = ((current_price / recent_low) - 1) * 100
    
    return metrics


def rank_sectors(sector_data: dict) -> pd.DataFrame:
    """Rank sectors by performance."""
    rankings = []
    
    for symbol, data in sector_data.items():
        if data and data['metrics']:
            rankings.append({
                'Symbol': symbol,
                'Sector': data['sector_name'],
                '1D %': data['metrics']['1_day'],
                '5D %': data['metrics']['5_day'],
                '20D %': data['metrics']['20_day'],
                'vs SMA20': data['metrics']['vs_sma20'],
                'Score': (data['metrics']['1_day'] * 0.3 + 
                         data['metrics']['5_day'] * 0.4 + 
                         data['metrics']['20_day'] * 0.3)
            })
    
    df = pd.DataFrame(rankings)
    df = df.sort_values('Score', ascending=False)
    return df


# ============================================================================
# CHART GENERATION
# ============================================================================

def create_sector_rotation_chart(rankings_df: pd.DataFrame) -> str:
    """Create visual chart of sector performance and save to file."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    chart_path = f"{output_dir}/sector_rotation_chart_{timestamp}.png"
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('📊 Sector Rotation Analysis', fontsize=16, fontweight='bold')
    
    # Chart 1: Performance Comparison
    sectors = rankings_df['Sector'].values
    scores = rankings_df['Score'].values
    colors = ['green' if s > 0 else 'red' for s in scores]
    
    bars = ax1.barh(sectors, scores, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Composite Score', fontsize=12, fontweight='bold')
    ax1.set_title('Sector Strength Ranking (Combined 1D/5D/20D Performance)', fontsize=12)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, score) in enumerate(zip(bars, scores)):
        label = f'{score:+.2f}%'
        x_pos = score + (0.1 if score > 0 else -0.1)
        ax1.text(x_pos, bar.get_y() + bar.get_height()/2, label,
                va='center', ha='left' if score > 0 else 'right',
                fontsize=9, fontweight='bold')
    
    # Chart 2: Multi-timeframe Heatmap
    timeframes = ['1D %', '5D %', '20D %']
    heatmap_data = rankings_df[timeframes].values.T
    
    im = ax2.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', 
                    vmin=-5, vmax=5, interpolation='nearest')
    
    ax2.set_xticks(range(len(sectors)))
    ax2.set_xticklabels(sectors, rotation=45, ha='right')
    ax2.set_yticks(range(len(timeframes)))
    ax2.set_yticklabels(timeframes)
    ax2.set_title('Performance Heatmap (Green=Strong, Red=Weak)', fontsize=12)
    
    # Add text annotations
    for i in range(len(timeframes)):
        for j in range(len(sectors)):
            value = heatmap_data[i, j]
            text_color = 'white' if abs(value) > 2 else 'black'
            ax2.text(j, i, f'{value:.1f}%',
                    ha='center', va='center',
                    color=text_color, fontsize=9, fontweight='bold')
    
    plt.colorbar(im, ax=ax2, label='Performance %')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Chart saved: {chart_path}")
    return chart_path


# ============================================================================
# CLICKUP INTEGRATION
# ============================================================================

def upload_file_to_clickup(file_path: str, task_id: str) -> bool:
    """Upload file attachment to ClickUp task."""
    
    if not CLICKUP_API_TOKEN:
        print("⚠ No ClickUp API token set. Skipping file upload.")
        return False
    
    try:
        headers = {
            'Authorization': CLICKUP_API_TOKEN
        }
        
        with open(file_path, 'rb') as f:
            files = {
                'attachment': (os.path.basename(file_path), f, 'image/png')
            }
            
            response = requests.post(
                f'https://api.clickup.com/api/v2/task/{task_id}/attachment',
                headers=headers,
                files=files
            )
            
            if response.status_code in [200, 201]:
                print(f"✓ Chart uploaded to ClickUp task {task_id}")
                return True
            else:
                print(f"✗ Upload failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"✗ Error uploading to ClickUp: {e}")
        return False


def post_to_clickup(rankings_df: pd.DataFrame, chart_path: str) -> bool:
    """Create ClickUp task with sector rotation analysis."""
    
    if not CLICKUP_API_TOKEN or not CLICKUP_LIST_ID:
        print("\n⚠ ClickUp not configured. Set environment variables:")
        print("   export CLICKUP_API_TOKEN='your_token'")
        print("   export CLICKUP_LIST_ID='your_list_id'")
        print("\nRun 'python find_clickup_list.py' to find your List ID")
        return False
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Identify top 3 and bottom 3
        top_3 = rankings_df.head(3)
        bottom_3 = rankings_df.tail(3)
        
        # Build task description
        description = f"""# 📊 Sector Rotation Analysis
**Scan Time:** {timestamp}

## 🚀 Strongest Sectors (Long Opportunities)

"""
        
        for _, row in top_3.iterrows():
            description += f"""### {row['Sector']} ({row['Symbol']})
- **Score:** {row['Score']:.2f}%
- **1 Day:** {row['1D %']:+.2f}%
- **5 Days:** {row['5D %']:+.2f}%
- **20 Days:** {row['20D %']:+.2f}%
- **vs SMA20:** {row['vs SMA20']:+.2f}%

"""
        
        description += """## ⚠️ Weakest Sectors (Avoid/Short)

"""
        
        for _, row in bottom_3.iterrows():
            description += f"""### {row['Sector']} ({row['Symbol']})
- **Score:** {row['Score']:.2f}%
- **1 Day:** {row['1D %']:+.2f}%
- **5 Days:** {row['5D %']:+.2f}%
- **20 Days:** {row['20D %']:+.2f}%
- **vs SMA20:** {row['vs SMA20']:+.2f}%

"""
        
        # Market sentiment
        avg_score = rankings_df['Score'].mean()
        positive_count = len(rankings_df[rankings_df['Score'] > 0])
        
        if avg_score > 1:
            sentiment = "🟢 RISK-ON"
            sentiment_desc = "Broad market strength, favor aggressive sectors"
        elif avg_score < -1:
            sentiment = "🔴 RISK-OFF"
            sentiment_desc = "Market weakness, favor defensive sectors"
        else:
            sentiment = "🟡 NEUTRAL"
            sentiment_desc = "Mixed market, selective opportunities"
        
        description += f"""## 📈 Market Sentiment: {sentiment}
{sentiment_desc}

**Positive Sectors:** {positive_count}/{len(rankings_df)}
**Average Score:** {avg_score:.2f}%

## 💡 Trading Strategy
- **Rotate Into:** Top 3 sectors
- **Rotate Out Of:** Bottom 3 sectors
- **Look for stocks in:** {', '.join(top_3['Sector'].values)}

---
*Auto-generated by Sector Rotation Scanner*
*Chart attached below ⬇️*
"""
        
        # Create task
        headers = {
            'Authorization': CLICKUP_API_TOKEN,
            'Content-Type': 'application/json'
        }
        
        task_data = {
            'name': f'📊 Sector Rotation Scan - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'description': description,
            'priority': 2,  # High priority
            'tags': ['sector-rotation', 'market-analysis', 'automated-scan']
        }
        
        response = requests.post(
            f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task',
            headers=headers,
            json=task_data
        )
        
        if response.status_code in [200, 201]:
            task_id = response.json()['id']
            print(f"✓ ClickUp task created: {task_id}")
            
            # Upload chart
            if chart_path and os.path.exists(chart_path):
                upload_file_to_clickup(chart_path, task_id)
            
            print(f"\n✓ Posted to ClickUp!")
            print(f"  View: https://app.clickup.com/t/{task_id}")
            return True
        else:
            print(f"✗ Failed to create task: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error posting to ClickUp: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN SCANNER
# ============================================================================

def scan_sectors():
    """Main sector rotation scan."""
    print("\n" + "="*80)
    print("SECTOR ROTATION SCANNER with ClickUp Integration")
    print("="*80 + "\n")
    
    print(f"Scanning {len(SECTOR_ETFS)} sector ETFs...\n")
    
    sector_data = {}
    
    for symbol, sector_name in SECTOR_ETFS.items():
        print(f"Fetching {symbol} ({sector_name})...", end=' ')
        
        df = fetch_sector_data(symbol)
        metrics = calculate_sector_metrics(df) if df is not None else None
        
        sector_data[symbol] = {
            'sector_name': sector_name,
            'data': df,
            'metrics': metrics
        }
        
        if metrics:
            print(f"✓ Score: {metrics['1_day']*0.3 + metrics['5_day']*0.4 + metrics['20_day']*0.3:+.2f}%")
        else:
            print("✗ No data")
        
        time.sleep(0.5)  # Rate limiting
    
    # Rank sectors
    print("\n" + "="*80)
    print("SECTOR RANKINGS")
    print("="*80 + "\n")
    
    rankings_df = rank_sectors(sector_data)
    print(rankings_df.to_string(index=False))
    
    # Market sentiment
    avg_score = rankings_df['Score'].mean()
    positive = len(rankings_df[rankings_df['Score'] > 0])
    
    print("\n" + "="*80)
    if avg_score > 1:
        print("📈 MARKET SENTIMENT: RISK-ON (Bullish)")
    elif avg_score < -1:
        print("📉 MARKET SENTIMENT: RISK-OFF (Bearish)")
    else:
        print("📊 MARKET SENTIMENT: NEUTRAL")
    print(f"Positive Sectors: {positive}/{len(rankings_df)}")
    print("="*80)
    
    # Create chart
    print("\n📊 Generating sector rotation chart...")
    chart_path = create_sector_rotation_chart(rankings_df)
    
    # Save CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = f"results/sector_rotation_{timestamp}.csv"
    rankings_df.to_csv(csv_path, index=False)
    print(f"✓ Data saved: {csv_path}")
    
    # Save JSON
    json_path = f"results/sector_rotation_{timestamp}.json"
    rankings_df.to_json(json_path, orient='records', indent=2)
    print(f"✓ Data saved: {json_path}")
    
    # Post to ClickUp
    print("\n📤 Posting results to ClickUp...")
    success = post_to_clickup(rankings_df, chart_path)
    
    if success:
        print("\n✅ Scan complete! Results posted to ClickUp dashboard.")
    else:
        print("\n✅ Scan complete! (ClickUp posting skipped - configure tokens)")
    
    print("\n" + "="*80)
    print("SCAN COMPLETE")
    print("="*80 + "\n")
    
    return rankings_df, chart_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution."""
    
    # Check ClickUp configuration
    if not CLICKUP_API_TOKEN:
        print("\n⚠️  ClickUp API Token not set!")
        print("To enable ClickUp posting:")
        print("  1. Get your API token from: https://app.clickup.com/settings/apps")
        print("  2. Run: export CLICKUP_API_TOKEN='your_token_here'")
        print("  3. Run: python find_clickup_list.py to get your List ID")
        print("  4. Run: export CLICKUP_LIST_ID='your_list_id_here'")
        print("\nContinuing with scan (no ClickUp posting)...\n")
        time.sleep(2)
    
    scan_sectors()


if __name__ == "__main__":
    main()
