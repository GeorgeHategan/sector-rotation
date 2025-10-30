# Historical Market Momentum Chart

## 📈 New Feature Added!

A new chart has been added that shows **how overall market momentum has changed over time**.

## What It Shows

The chart displays:
- **Average momentum score** across all 13 sectors over time
- **Bullish periods** (green shaded area above zero line)
- **Bearish periods** (red shaded area below zero line)
- **Trend direction** - is the market becoming more bullish or bearish?
- **Current momentum** with annotation

## How to Generate

### Option 1: Standalone Script
Run the dedicated script to create just the historical chart:
```bash
cd scripts
python create_historical_chart.py
```

### Option 2: Automatic (included in main scanner)
The historical chart is now automatically generated when you run:
```bash
python sector_rotation_scanner.py
```

## Output Location

The chart is saved to:
```
output/charts/historical_market_momentum.png
```

And automatically copied to:
```
docs/historical_market_momentum.png
```
(for GitHub Pages)

## Requirements

The script needs:
- At least 2 historical scan files in `data/historical/`
- The more historical data you have, the better the chart looks!

## How to Read the Chart

### Line Interpretation
- **Line going UP** = Market momentum is improving (becoming more bullish)
- **Line going DOWN** = Market momentum is weakening (becoming more bearish)  
- **Line crossing zero upward** = Shift from bearish to bullish market
- **Line crossing zero downward** = Shift from bullish to bearish market

### Color Zones
- **Green area (above 0)** = Bullish territory - most sectors have positive momentum
- **Red area (below 0)** = Bearish territory - most sectors have negative momentum
- **Line at zero** = Neutral - balanced market

### Current Value
The chart shows an annotation with the current momentum score, so you can see:
- Where we are now
- Where we've been
- Which direction we're trending

## Use Cases

This chart helps you:
1. **Identify trend changes** - See when market shifts from bullish to bearish (or vice versa)
2. **Confirm trends** - Is the current market direction strengthening or weakening?
3. **Historical context** - Compare current momentum to recent past
4. **Entry/exit timing** - Look for momentum turning points

## Example Interpretation

If the chart shows:
```
Line trending upward for past week → Market is gaining bullish momentum
Line crossed zero yesterday → Just shifted from bearish to bullish
Current value: +1.25 → Moderately bullish
```

**Interpretation**: The market has recently become bullish and the trend is strengthening. Good time to look for long positions in strong sectors.

## Technical Details

- **Data source**: All JSON files in `data/historical/sector_rotation_*.json`
- **Calculation**: Average of all 13 sector momentum scores for each scan
- **Update frequency**: Generated every time the scanner runs (hourly during market hours)
- **Chart format**: PNG image (1400x800 pixels, high resolution)

## Maintenance

The chart automatically:
- Reads all available historical data
- Handles missing or corrupted files gracefully
- Scales the x-axis based on date range
- Updates with each new scan

No manual intervention needed! 🎉
