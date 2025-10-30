#!/usr/bin/env python3
"""
Create Historical Market Momentum Chart
Reads all historical sector rotation data and creates a trend chart
"""

import json
import glob
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def create_historical_momentum_chart(filename='../output/charts/historical_market_momentum.png'):
    """
    Creates a chart showing how overall market momentum has changed over time.
    """
    
    print("\n📈 Creating historical market momentum chart...")
    
    # Find all historical data files
    json_files = sorted(glob.glob('../data/historical/sector_rotation_*.json'))
    
    if len(json_files) < 2:
        print("⚠️  Not enough historical data (need at least 2 scans)")
        return None
    
    print(f"   Found {len(json_files)} historical files")
    
    # Extract timestamps and momentum scores
    timestamps = []
    avg_momentums = []
    
    for json_file in json_files:
        try:
            # Extract timestamp from filename
            basename = os.path.basename(json_file)
            date_str = basename.replace('sector_rotation_', '').replace('.json', '')
            timestamp = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            
            # Load the data
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Calculate average momentum across all sectors
            if isinstance(data, list) and len(data) > 0:
                total_momentum = sum(sector.get('Momentum_Score', 0) for sector in data)
                avg_momentum = total_momentum / len(data)
                
                timestamps.append(timestamp)
                avg_momentums.append(avg_momentum)
        
        except Exception as e:
            print(f"   ⚠️  Skipping {json_file}: {e}")
            continue
    
    if len(timestamps) < 2:
        print("⚠️  Could not read enough historical data")
        return None
    
    print(f"   Successfully loaded {len(timestamps)} data points")
    print(f"   Date range: {timestamps[0].strftime('%Y-%m-%d')} to {timestamps[-1].strftime('%Y-%m-%d')}")
    
    # Create the chart
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Plot the line chart
    ax.plot(timestamps, avg_momentums, 
            color='#60a5fa', linewidth=2.5, marker='o', markersize=4, 
            label='Average Market Momentum')
    
    # Add a horizontal line at zero
    ax.axhline(y=0, color='#9ca3af', linestyle='--', linewidth=1, alpha=0.5, 
               label='Neutral Line')
    
    # Fill areas above/below zero with color
    ax.fill_between(timestamps, avg_momentums, 0, 
                     where=[m >= 0 for m in avg_momentums],
                     alpha=0.3, color='#22c55e', label='Bullish Territory')
    ax.fill_between(timestamps, avg_momentums, 0, 
                     where=[m < 0 for m in avg_momentums],
                     alpha=0.3, color='#dc2626', label='Bearish Territory')
    
    # Add grid
    ax.grid(True, alpha=0.2, color='#4b5563', linestyle='-', linewidth=0.5)
    
    # Labels and title
    ax.set_xlabel('Date', fontsize=12, fontweight='bold', color='#e0e0e0')
    ax.set_ylabel('Average Momentum Score', fontsize=12, fontweight='bold', color='#e0e0e0')
    ax.set_title('Historical Market Momentum Trend', fontsize=16, fontweight='bold', 
                 pad=20, color='#60a5fa')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45, ha='right')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    
    # Style the tick marks
    ax.tick_params(colors='#e0e0e0')
    
    # Add current value annotation
    if len(avg_momentums) > 0:
        last_momentum = avg_momentums[-1]
        last_time = timestamps[-1]
        ax.annotate(f'Current: {last_momentum:+.2f}',
                   xy=(last_time, last_momentum),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#1e293b', alpha=0.8),
                   fontsize=10, fontweight='bold', color='#60a5fa',
                   arrowprops=dict(arrowstyle='->', color='#60a5fa', lw=1.5))
    
    # Add timestamp
    fig.text(0.99, 0.01, 
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data points: {len(timestamps)}", 
             ha='right', fontsize=8, style='italic', alpha=0.7, color='#9ca3af')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    
    print(f"\n✅ Historical momentum chart saved to: {filename}")
    print(f"   📊 Chart shows {len(timestamps)} data points")
    print(f"   📅 From {timestamps[0].strftime('%Y-%m-%d %H:%M')} to {timestamps[-1].strftime('%Y-%m-%d %H:%M')}")
    
    # Print some statistics
    max_momentum = max(avg_momentums)
    min_momentum = min(avg_momentums)
    current_momentum = avg_momentums[-1]
    
    print(f"\n   📈 Highest momentum: {max_momentum:+.2f}")
    print(f"   📉 Lowest momentum: {min_momentum:+.2f}")
    print(f"   🎯 Current momentum: {current_momentum:+.2f}")
    
    if current_momentum > 0:
        print(f"   ✅ Market is currently BULLISH")
    elif current_momentum < 0:
        print(f"   ⚠️  Market is currently BEARISH")
    else:
        print(f"   ➡️  Market is currently NEUTRAL")
    
    return filename


if __name__ == "__main__":
    print("=" * 80)
    print("HISTORICAL MARKET MOMENTUM CHART GENERATOR")
    print("=" * 80)
    
    result = create_historical_momentum_chart()
    
    if result:
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED - Not enough historical data")
        print("=" * 80)
