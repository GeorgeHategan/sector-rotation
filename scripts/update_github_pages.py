#!/usr/bin/env python3
"""
Update GitHub Pages with latest sector rotation data
Run this after sector_rotation_scanner.py to publish results to GitHub Pages
"""

import os
import json
import shutil
from datetime import datetime
import glob
from zoneinfo import ZoneInfo

def update_github_pages():
    """Copy latest scan results to docs folder for GitHub Pages"""
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # Find the most recent files
    json_files = sorted(glob.glob('data/historical/sector_rotation_*.json'), key=os.path.getmtime, reverse=True)
    chart_files = sorted(glob.glob('output/charts/sector_rotation_chart_*.png'), key=os.path.getmtime, reverse=True)
    heatmap_files = sorted(glob.glob('output/heatmaps/sector_heatmap_*.png'), key=os.path.getmtime, reverse=True)
    ai_analysis_files = sorted(glob.glob('output/reports/ai_market_analysis_*.json'), key=os.path.getmtime, reverse=True)
    
    # Check for historical momentum chart
    historical_chart = 'output/charts/historical_market_momentum.png' if os.path.exists('output/charts/historical_market_momentum.png') else None
    
    if not json_files:
        print("❌ No sector rotation data found. Run sector_rotation_scanner.py first.")
        return
    
    latest_json = json_files[0]
    latest_chart = chart_files[0] if chart_files else None
    latest_heatmap = heatmap_files[0] if heatmap_files else None
    latest_ai_analysis = ai_analysis_files[0] if ai_analysis_files else None
    
    print(f"📊 Found latest data: {latest_json}")
    
    # Load the JSON data
    with open(latest_json, 'r') as f:
        sector_data = json.load(f)
    
    # Load AI analysis if available
    ai_analysis_text = None
    if latest_ai_analysis:
        print(f"🤖 Found AI analysis: {latest_ai_analysis}")
        with open(latest_ai_analysis, 'r') as f:
            ai_data = json.load(f)
            ai_analysis_text = ai_data.get('ai_analysis', '')
    
    # Create the latest_data.json for GitHub Pages
    # Use CET timezone for the timestamp
    cet_tz = ZoneInfo('Europe/Berlin')  # CET/CEST timezone
    page_data = {
        'timestamp': datetime.now(cet_tz).isoformat(),
        'sectors': sector_data,
        'chart_file': os.path.basename(latest_chart) if latest_chart else '',
        'heatmap_file': os.path.basename(latest_heatmap) if latest_heatmap else '',
        'ai_analysis': ai_analysis_text
    }
    
    # Save to docs folder
    with open('docs/latest_data.json', 'w') as f:
        json.dump(page_data, f, indent=2)
    
    print(f"✅ Updated docs/latest_data.json")
    
    # Copy image files to docs folder
    if latest_chart:
        shutil.copy(latest_chart, f'docs/{os.path.basename(latest_chart)}')
        print(f"✅ Copied {latest_chart} to docs/")
    
    if latest_heatmap:
        shutil.copy(latest_heatmap, f'docs/{os.path.basename(latest_heatmap)}')
        print(f"✅ Copied {latest_heatmap} to docs/")
    
    # Copy historical momentum chart if it exists
    if historical_chart:
        shutil.copy(historical_chart, 'docs/historical_market_momentum.png')
        print(f"✅ Copied historical momentum chart to docs/")
    
    if latest_ai_analysis:
        print(f"✅ Included AI analysis in latest_data.json")
    
    print("\n" + "=" * 80)
    print("🎉 GitHub Pages data updated successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Commit the changes:")
    print("   git add docs/")
    print("   git commit -m 'Update sector rotation data'")
    print("   git push")
    print("\n2. Enable GitHub Pages in your repository settings:")
    print("   - Go to Settings > Pages")
    print("   - Source: Deploy from a branch")
    print("   - Branch: main, Folder: /docs")
    print("   - Save")
    print("\n3. Your page will be available at:")
    print("   https://georgehategan.github.io/sector-rotation/")
    print("=" * 80)


if __name__ == "__main__":
    update_github_pages()
