# Sector Rotation Scanner

## Overview

This directory contains scanners that analyze sector rotation and identify money flow between market sectors.

## Scanners

### 1. **sector_rotation_scanner.py** - Sector Rotation Analyzer
**Purpose:** Identifies money flow between market sectors

**Features:**
- Analyzes 11 major market sectors using ETFs
- Identifies money flow patterns
- Determines market sentiment (Risk-On vs Risk-Off)
- Tracks defensive vs cyclical sector performance
- Shows which sectors are strongest/weakest

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

**Usage:**
```bash
python sector_rotation_scanner.py
```

---

### 2. **smart_sector_breakout_scanner.py** - Smart Sector Breakout Scanner
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
2. Identify strongest sectors from results
3. Run smart scanner: `python smart_sector_breakout_scanner.py`
4. Review results in `results/` directory

## Requirements

See main repository `requirements.txt` for dependencies.
