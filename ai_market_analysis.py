#!/usr/bin/env python3
"""
AI Market Analysis using OpenAI
Analyzes sector rotation data and provides expert market sentiment assessment
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv(override=True)

def get_latest_sector_data():
    """Load the most recent sector rotation data"""
    json_files = sorted(glob.glob('sector_rotation_*.json'), key=os.path.getmtime, reverse=True)
    
    if not json_files:
        print("❌ No sector rotation data found. Run sector_rotation_scanner.py first.")
        return None
    
    latest_file = json_files[0]
    print(f"📊 Loading data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)


def analyze_with_openai(sector_data):
    """Send sector data to OpenAI for expert analysis"""
    
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables!")
        print("Please add it to your .env file:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # Prepare the data summary for analysis
    data_summary = json.dumps(sector_data, indent=2)
    
    # Calculate additional metrics
    avg_momentum = sum(s['Momentum_Score'] for s in sector_data) / len(sector_data)
    strongest_sectors = sorted(sector_data, key=lambda x: x['Momentum_Score'], reverse=True)[:3]
    weakest_sectors = sorted(sector_data, key=lambda x: x['Momentum_Score'])[:3]
    
    # Create the prompt
    prompt = f"""You are an advanced market analyst with 20+ years of experience in technical analysis, sector rotation, and market cycles. 

Analyze the following sector rotation data and provide a comprehensive market assessment:

SECTOR DATA:
{data_summary}

SUMMARY METRICS:
- Average Market Momentum: {avg_momentum:.2f}
- Strongest Sectors: {', '.join([s['Sector'] for s in strongest_sectors])}
- Weakest Sectors: {', '.join([s['Sector'] for s in weakest_sectors])}

YOUR ANALYSIS SHOULD INCLUDE:

1. **Market Phase Assessment**: Are we in a bull market, bear market, or transitional phase?

2. **Risk Environment**: Is this a Risk-On or Risk-Off environment? What does the sector rotation tell us?

3. **Sector Rotation Pattern**: What does the current rotation pattern indicate about market expectations?

4. **Cyclical vs Defensive**: Analyze the performance of cyclical sectors (Tech, Financials, Consumer Discretionary, Industrials) versus defensive sectors (Utilities, Consumer Staples, Healthcare).

5. **Key Insights**: What are 3-5 actionable insights for traders and investors?

6. **Market Outlook**: Short-term (1-2 weeks) and medium-term (1-3 months) outlook.

7. **Risk Factors**: What are the main risks to watch?

Please be specific, data-driven, and provide your professional opinion based on the sector metrics provided."""

    print("\n" + "=" * 80)
    print("🤖 AI MARKET ANALYSIS")
    print("=" * 80)
    print("\nAnalyzing sector data with OpenAI GPT-4...\n")
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert market analyst specializing in sector rotation analysis, technical analysis, and market cycle identification. You provide clear, actionable insights based on data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        analysis = response.choices[0].message.content
        return analysis
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None


def save_analysis(analysis, sector_data):
    """Save the AI analysis to a file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create analysis report
    report = {
        'timestamp': datetime.now().isoformat(),
        'sector_data_summary': {
            'total_sectors': len(sector_data),
            'avg_momentum': sum(s['Momentum_Score'] for s in sector_data) / len(sector_data),
            'strongest_sector': max(sector_data, key=lambda x: x['Momentum_Score'])['Sector'],
            'weakest_sector': min(sector_data, key=lambda x: x['Momentum_Score'])['Sector']
        },
        'ai_analysis': analysis
    }
    
    # Save as JSON
    json_file = f"ai_market_analysis_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save as readable text
    txt_file = f"ai_market_analysis_{timestamp}.txt"
    with open(txt_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AI MARKET ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("Data source: Sector Rotation Scanner\n")
        f.write("AI Model: OpenAI GPT-4\n")
        f.write("=" * 80 + "\n")
    
    return json_file, txt_file


def main():
    """Main execution function"""
    print("=" * 80)
    print("AI MARKET ANALYSIS - SECTOR ROTATION")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load sector data
    sector_data = get_latest_sector_data()
    if not sector_data:
        return
    
    # Analyze with OpenAI
    analysis = analyze_with_openai(sector_data)
    if not analysis:
        return
    
    # Display the analysis
    print(analysis)
    print("\n" + "=" * 80)
    
    # Save the analysis
    json_file, txt_file = save_analysis(analysis, sector_data)
    
    print("\n" + "=" * 80)
    print("✅ Analysis saved to:")
    print(f"   - {json_file}")
    print(f"   - {txt_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
