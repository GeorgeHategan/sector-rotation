# AI Market Analysis Guide

## Overview

The AI Market Analysis feature uses OpenAI's GPT-4 to provide expert-level analysis of sector rotation data, helping you understand market conditions and make informed trading decisions.

## Setup

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy your API key

### 2. Add to Environment Variables

Add your OpenAI API key to the `.env` file:

```bash
ALPHAVANTAGE_API_KEY=your_alphavantage_key_here
OPENAI_API_KEY=your_openai_key_here
```

## Usage

### Basic Usage

Run the AI analysis after scanning sectors:

```bash
# 1. Scan sectors
python3 sector_rotation_scanner.py

# 2. Get AI analysis
python3 ai_market_analysis.py
```

### What You Get

The AI provides a comprehensive analysis including:

1. **Market Phase Assessment**
   - Bull market, bear market, or transitional phase identification
   - Confidence level and supporting evidence

2. **Risk Environment Analysis**
   - Risk-On vs Risk-Off assessment
   - What the sector rotation indicates

3. **Sector Rotation Patterns**
   - Money flow analysis
   - Market expectations insights

4. **Cyclical vs Defensive Performance**
   - Comparison of growth vs defensive sectors
   - What this means for market direction

5. **Actionable Insights**
   - 3-5 specific trading/investing recommendations
   - Based on current sector data

6. **Market Outlook**
   - Short-term (1-2 weeks) forecast
   - Medium-term (1-3 months) outlook

7. **Risk Factors**
   - Key risks to monitor
   - Warning signs to watch for

## Output Files

The analysis is saved to two files:

- `ai_market_analysis_YYYYMMDD_HHMMSS.json` - Structured data format
- `ai_market_analysis_YYYYMMDD_HHMMSS.txt` - Human-readable report

## Example Output

```
================================================================================
AI MARKET ANALYSIS REPORT
================================================================================
Generated: 2025-10-18 20:45:00
================================================================================

1. MARKET PHASE ASSESSMENT

Based on the sector rotation data, we are currently in a TRANSITIONAL PHASE 
with defensive characteristics...

2. RISK ENVIRONMENT

The current environment shows RISK-OFF sentiment. Key indicators:
- Consumer Staples and Healthcare outperforming (defensive rotation)
- Regional Banking showing strong selling pressure
- Technology sector neutral despite typically leading in risk-on...

[... continued analysis ...]
```

## Cost

- OpenAI API calls cost approximately $0.02-0.05 per analysis
- GPT-4 pricing: https://openai.com/pricing
- You have full control over when analysis runs (not automated)

## Tips for Best Results

1. **Run after market hours** - Get end-of-day analysis
2. **Compare over time** - Track how the AI's assessment changes
3. **Combine with technical analysis** - Use as one input among many
4. **Review historical analyses** - Build a library of market insights

## Automated Analysis (Optional)

You can modify `auto_update.sh` or the GitHub Actions workflow to include AI analysis:

```bash
# Add to auto_update.sh after sector scan
python3 sector_rotation_scanner.py
python3 ai_market_analysis.py  # Add this line
python3 update_github_pages.py
```

**Note**: This will consume OpenAI API credits on every run.

## Troubleshooting

### "OPENAI_API_KEY not found"

Make sure:
- `.env` file exists in project root
- Contains `OPENAI_API_KEY=your_key_here`
- No quotes around the key value

### "Rate limit exceeded"

- Wait a few minutes and try again
- Check your OpenAI account usage limits
- Consider upgrading your OpenAI plan

### "No sector rotation data found"

- Run `sector_rotation_scanner.py` first
- Check that JSON files were created in the project directory

## Security

✅ **Your OpenAI API key is protected**:
- Stored in `.env` file (git-ignored)
- Never committed to repository
- Only accessible to your scripts

## Disclaimer

The AI analysis is for informational purposes only and should not be considered financial advice. Always do your own research and consult with financial professionals before making investment decisions.
