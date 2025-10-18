#!/usr/bin/env python3
"""
Generate GitHub Pages from Sector Rotation Results
==================================================

Creates a static HTML page with:
- Latest sector rotation chart
- Interactive data tables
- Historical trends
- Auto-refreshing content
"""

import json
import os
from datetime import datetime
from pathlib import Path
import shutil

def generate_html():
    """Generate the GitHub Pages HTML."""
    
    # Find latest results
    results_dir = Path('results')
    json_files = sorted(results_dir.glob('sector_rotation_*.json'), reverse=True)
    chart_files = sorted(results_dir.glob('sector_rotation_chart_*.png'), reverse=True)
    
    if not json_files or not chart_files:
        print("No results found!")
        return
    
    # Load latest data
    with open(json_files[0]) as f:
        data = json.load(f)
    
    # Get timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Prepare docs directory
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    
    # Copy latest chart
    latest_chart = chart_files[0]
    shutil.copy(latest_chart, docs_dir / 'latest_chart.png')
    
    # Sort data by score
    data.sort(key=lambda x: x['Score'], reverse=True)
    
    # Count sectors
    positive = sum(1 for s in data if s['Score'] > 0)
    negative = len(data) - positive
    
    # Top and bottom sectors
    top_3 = data[:3]
    bottom_3 = data[-3:]
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3600">
    <title>Sector Rotation Scanner - Live Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .update-time {{
            background: #f0f0f0;
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .chart-container img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        
        .sectors {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .sector-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .sector-card.top {{
            border-left: 5px solid #10b981;
        }}
        
        .sector-card.bottom {{
            border-left: 5px solid #ef4444;
        }}
        
        .sector-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .sector-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .sector-score {{
            font-size: 1.8em;
            font-weight: bold;
        }}
        
        .sector-score.positive {{
            color: #10b981;
        }}
        
        .sector-score.negative {{
            color: #ef4444;
        }}
        
        .sector-metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 0.9em;
        }}
        
        .metric {{
            background: #f9fafb;
            padding: 10px;
            border-radius: 8px;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.85em;
        }}
        
        .metric-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        table {{
            width: 100%;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        tr:hover {{
            background: #f9fafb;
        }}
        
        .positive-num {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .negative-num {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        footer {{
            text-align: center;
            color: white;
            padding: 30px;
            font-size: 0.9em;
        }}
        
        footer a {{
            color: white;
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            .sectors {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Sector Rotation Scanner</h1>
            <p class="subtitle">Real-time market sector analysis • Updated hourly</p>
            <div class="update-time">
                Last updated: {timestamp}
            </div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Sectors</h3>
                <div class="stat-value">{len(data)}</div>
            </div>
            <div class="stat-card">
                <h3>Positive Sectors</h3>
                <div class="stat-value positive-num">{positive}</div>
            </div>
            <div class="stat-card">
                <h3>Negative Sectors</h3>
                <div class="stat-value negative-num">{negative}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 style="margin-bottom: 20px; color: #667eea;">Sector Performance Chart</h2>
            <img src="latest_chart.png" alt="Sector Rotation Chart">
        </div>
        
        <h2 style="color: white; margin-bottom: 20px; text-align: center; font-size: 2em;">🚀 Top 3 Sectors</h2>
        <div class="sectors">
'''
    
    for sector in top_3:
        score_class = 'positive' if sector['Score'] > 0 else 'negative'
        html += f'''
            <div class="sector-card top">
                <div class="sector-header">
                    <div class="sector-name">{sector['Sector']}</div>
                    <div class="sector-score {score_class}">{sector['Score']:+.2f}%</div>
                </div>
                <div class="sector-metrics">
                    <div class="metric">
                        <div class="metric-label">1 Day</div>
                        <div class="metric-value {'positive-num' if sector['1D %'] > 0 else 'negative-num'}">{sector['1D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">5 Days</div>
                        <div class="metric-value {'positive-num' if sector['5D %'] > 0 else 'negative-num'}">{sector['5D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">20 Days</div>
                        <div class="metric-value {'positive-num' if sector['20D %'] > 0 else 'negative-num'}">{sector['20D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">vs SMA20</div>
                        <div class="metric-value {'positive-num' if sector['vs SMA20'] > 0 else 'negative-num'}">{sector['vs SMA20']:+.2f}%</div>
                    </div>
                </div>
            </div>
'''
    
    html += '''
        </div>
        
        <h2 style="color: white; margin-bottom: 20px; text-align: center; font-size: 2em;">⚠️ Bottom 3 Sectors</h2>
        <div class="sectors">
'''
    
    for sector in bottom_3:
        score_class = 'positive' if sector['Score'] > 0 else 'negative'
        html += f'''
            <div class="sector-card bottom">
                <div class="sector-header">
                    <div class="sector-name">{sector['Sector']}</div>
                    <div class="sector-score {score_class}">{sector['Score']:+.2f}%</div>
                </div>
                <div class="sector-metrics">
                    <div class="metric">
                        <div class="metric-label">1 Day</div>
                        <div class="metric-value {'positive-num' if sector['1D %'] > 0 else 'negative-num'}">{sector['1D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">5 Days</div>
                        <div class="metric-value {'positive-num' if sector['5D %'] > 0 else 'negative-num'}">{sector['5D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">20 Days</div>
                        <div class="metric-value {'positive-num' if sector['20D %'] > 0 else 'negative-num'}">{sector['20D %']:+.2f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">vs SMA20</div>
                        <div class="metric-value {'positive-num' if sector['vs SMA20'] > 0 else 'negative-num'}">{sector['vs SMA20']:+.2f}%</div>
                    </div>
                </div>
            </div>
'''
    
    html += '''
        </div>
        
        <h2 style="color: white; margin-bottom: 20px; text-align: center; font-size: 2em;">📋 All Sectors</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Sector</th>
                    <th>Score</th>
                    <th>1 Day %</th>
                    <th>5 Days %</th>
                    <th>20 Days %</th>
                    <th>vs SMA20</th>
                </tr>
            </thead>
            <tbody>
'''
    
    for sector in data:
        score_class = 'positive-num' if sector['Score'] > 0 else 'negative-num'
        html += f'''
                <tr>
                    <td><strong>{sector['Symbol']}</strong></td>
                    <td>{sector['Sector']}</td>
                    <td class="{score_class}">{sector['Score']:+.2f}%</td>
                    <td class="{'positive-num' if sector['1D %'] > 0 else 'negative-num'}">{sector['1D %']:+.2f}%</td>
                    <td class="{'positive-num' if sector['5D %'] > 0 else 'negative-num'}">{sector['5D %']:+.2f}%</td>
                    <td class="{'positive-num' if sector['20D %'] > 0 else 'negative-num'}">{sector['20D %']:+.2f}%</td>
                    <td class="{'positive-num' if sector['vs SMA20'] > 0 else 'negative-num'}">{sector['vs SMA20']:+.2f}%</td>
                </tr>
'''
    
    html += '''
            </tbody>
        </table>
        
        <footer>
            <p><strong>Sector Rotation Scanner</strong></p>
            <p>Automated market analysis • Updates every hour</p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/GeorgeHategan/sector-rotation" target="_blank">View on GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
'''
    
    # Write HTML file
    with open(docs_dir / 'index.html', 'w') as f:
        f.write(html)
    
    print(f"✓ GitHub Pages generated: docs/index.html")
    print(f"✓ Chart copied: docs/latest_chart.png")
    print(f"✓ {len(data)} sectors processed")

if __name__ == '__main__':
    generate_html()
