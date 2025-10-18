# Sector Rotation Scanner

## 🌐 Live Dashboard

View real-time sector rotation analysis at:
**[https://georgehategan.github.io/sector-rotation/](https://georgehategan.github.io/sector-rotation/)**

### 🤖 Automatic Updates

This dashboard updates automatically during market hours via GitHub Actions:
- Updates every hour during market hours (9:30 AM - 4:00 PM EST)
- Monday through Friday only
- No manual intervention required

---

## Overview

This directory contains scanners that analyze sector rotation and identify money flow between market sectors.

## Scanners

### 1. **sector_rotation_scanner.py** - Sector Rotation Analyzer
**Purpose:** Identifies money flow between market sectors

**Features:**
- Analyzes 13 major market sectors using ETFs (including IBB and KRE)
- Identifies money flow patterns
- Determines market sentiment (Risk-On vs Risk-Off)
- Tracks defensive vs cyclical sector performance
- Shows which sectors are strongest/weakest
- Generates interactive heatmap visualizations

**Sectors Analyzed:**
- XLK (Technology)
- XLF (Financials)
- XLE (Energy)
- XLV (Healthcare)
- XLY (Consumer Discretionary)
- XLP (Consumer Staples)
- XLI (Industrials)
- XLB (Materials)
- XLU (Utilities)
- XLRE (Real Estate)
- XLC (Communications)
- KRE (Regional Banking)
- IBB (Biotechnology)

**Usage:**
```bash
python sector_rotation_scanner.py
```

**Outputs:**
- CSV and JSON data files
- Momentum bar charts
- Performance heatmap

---

### 2. **ai_market_analysis.py** - 🤖 AI Market Analysis (NEW!)
**Purpose:** Expert AI analysis of sector rotation patterns using OpenAI GPT-4

**Features:**
- Determines if we're in a bull or bear market
- Assesses Risk-On vs Risk-Off environment
- Analyzes cyclical vs defensive sector performance
- Provides actionable trading insights
- Short and medium-term market outlook
- Identifies key risk factors

**Usage:**
```bash
# Run after sector scan
python sector_rotation_scanner.py
python ai_market_analysis.py
```

**What You Get:**
- Market phase assessment (bull/bear/transitional)
- Risk environment analysis
- 3-5 actionable insights
- Short-term and medium-term outlook
- Key risks to monitor

📖 **Detailed Guide**: See [AI_ANALYSIS_GUIDE.md](AI_ANALYSIS_GUIDE.md)

---

### 3. **smart_sector_breakout_scanner.py** - Smart Sector Breakout Scanner
**Purpose:** Combines sector rotation analysis with breakout detection

**Features:**
- Identifies strongest sectors
- Finds breakout opportunities within strong sectors
- Integrated analysis approach
- Higher probability setups

**Usage:**
```bash
python smart_sector_breakout_scanner.py
```

---

## Results Directory

All scanner output files are saved to `results/` subdirectory:
- `sector_rotation_YYYYMMDD_HHMMSS.csv`
- `sector_rotation_YYYYMMDD_HHMMSS.json`

## Output Details

Results include:
- Sector performance metrics
- Money flow indicators
- Risk sentiment analysis
- Strongest/weakest sectors
- Rotation patterns

## How to Use

### 1. Analyze Market Sentiment
```bash
python sector_rotation_scanner.py
```
This will show you:
- Which sectors are receiving capital
- Overall market sentiment (Risk-On/Risk-Off)
- Relative sector strength

### 2. Find Sector-Specific Breakouts
```bash
python smart_sector_breakout_scanner.py
```
This will:
- Identify strongest sector
- Scan that sector for breakouts
- Provide complete analysis

## Trading Strategy

1. **Run sector rotation scanner** to identify hot sectors
2. **Focus on strongest 2-3 sectors**
3. **Run breakout scanner** on those sectors
4. **Trade with the sector momentum**

## Market Sentiment Guide

**Risk-On (Bullish):**
- Technology (XLK) ↑
- Financials (XLF) ↑
- Consumer Discretionary (XLY) ↑
- Energy (XLE) ↑

**Risk-Off (Bearish):**
- Utilities (XLU) ↑
- Consumer Staples (XLP) ↑
- Healthcare (XLV) ↑
- Treasuries/Bonds ↑

## Quick Start

1. Run sector analysis: `python sector_rotation_scanner.py`
2. Update GitHub Pages: `python update_github_pages.py`
3. Identify strongest sectors from results
4. Run smart scanner: `python smart_sector_breakout_scanner.py`
5. Review results in output files

## Publishing to GitHub Pages

### Manual Updates

After running the scanner, publish your results online:

```bash
# 1. Run the scanner
python sector_rotation_scanner.py

# 2. Update GitHub Pages data
python update_github_pages.py

# 3. Commit and push
git add docs/
git commit -m "Update sector rotation data"
git push
```

Your live dashboard will be available at: `https://georgehategan.github.io/sector-rotation/`

### Automatic Updates with GitHub Actions

Set up automated updates during market hours:

1. **Add API Key as GitHub Secret**:
   - Go to repository **Settings** → **Secrets and variables** → **Actions**
   - Add secret: `ALPHAVANTAGE_API_KEY` = your API key
   
2. **Enable GitHub Actions**:
   - The workflow file is already included (`.github/workflows/update-sector-data.yml`)
   - GitHub Actions will run automatically during market hours
   
3. **Enable GitHub Pages** (one-time setup):
   - Go to **Settings** → **Pages**
   - Source: Branch `main`, Folder `/docs`
   - Click **Save**

📖 **Detailed Setup Guide**: See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

The dashboard will automatically update every hour during market hours (9:30 AM - 4:00 PM EST, Mon-Fri).

### First-Time Setup for GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** > **Pages**
3. Under "Source", select:
   - Branch: `main`
   - Folder: `/docs`
4. Click **Save**
5. Wait a few minutes for deployment

## Security

⚠️ **API Key Protection**: This repository uses environment variables to protect your API keys.

1. Create a `.env` file in the project root:
   ```
   ALPHAVANTAGE_API_KEY=your_alphavantage_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```
2. The `.env` file is automatically ignored by git (listed in `.gitignore`)
3. Never commit your API keys to the repository

### Optional: AI Market Analysis

To enable AI-powered market analysis with OpenAI:
1. Get an API key from https://platform.openai.com/api-keys
2. Add `OPENAI_API_KEY` to your `.env` file
3. Run: `python ai_market_analysis.py`

The AI will analyze sector rotation patterns and provide expert insights on market conditions.

## Requirements

See main repository `requirements.txt` for dependencies.
