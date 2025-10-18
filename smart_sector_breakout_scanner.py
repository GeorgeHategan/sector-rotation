#!/usr/bin/env python3
"""
Smart Sector Breakout Scanner
1. Identifies the strongest sector (highest money inflow)
2. Scans all stocks in that sector for breakouts
3. Validates with volume confirmation
4. Checks for news catalysts
5. Ranks by probability/quality
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# Alpha Vantage API Configuration
API_KEY = '75IGYUZ3C7AC2PBM'
BASE_URL = 'https://www.alphavantage.co/query'

# Major Sector ETFs and their top holdings
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
}

# Top stocks in each sector (under $100 focus)
SECTOR_STOCKS = {
    'Technology': ['AMD', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'NOW', 'PANW', 'SNOW', 'CRWD', 
                   'PLTR', 'PLUG', 'WKHS', 'GOEV', 'BLNK', 'ASTR', 'IONQ', 'MVST', 'ARM', 'SMCI'],
    'Financials': ['BAC', 'JPM', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'SCHW',
                   'SOFI', 'OPEN', 'UPST', 'COIN', 'HOOD', 'NU', 'AFRM'],
    'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE', 'DHR', 'BMY',
                   'CLOV', 'TLRY', 'SNDL', 'ACB', 'CGC', 'HEXO', 'OGI', 'CRON', 'MRNA', 'GILD'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL', 'MULN', 'FANG'],
    'Industrials': ['GE', 'CAT', 'HON', 'UNP', 'RTX', 'BA', 'LMT', 'DE', 'MMM', 'GD',
                    'SPCE', 'RIDE', 'RIVN', 'LCID'],
    'Consumer Staples': ['PG', 'KO', 'PEP', 'COST', 'WMT', 'PM', 'MDLZ', 'CL', 'MO', 'KMB'],
    'Consumer Discretionary': ['TSLA', 'AMZN', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'BKNG', 'CMG',
                               'FUBO', 'WISH', 'SKLZ', 'GREE', 'DKNG', 'DASH', 'ABNB', 'UBER', 'LYFT'],
    'Materials': ['LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'NUE', 'DD', 'DOW', 'HYMC'],
    'Real Estate': ['PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'SPG', 'DLR', 'O', 'WELL', 'AVB'],
    'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ED', 'PEG'],
    'Communication Services': ['META', 'GOOGL', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS', 'CHTR',
                               'SNAP', 'AMC', 'RBLX', 'PINS', 'MTCH', 'PARA'],
    'Regional Banking': ['ZION', 'HBAN', 'KEY', 'RF', 'CFG', 'FITB', 'MTB', 'FHN', 'SNV', 'WTFC',
                        'EWBC', 'COLB', 'WAL', 'ONB', 'UBSI', 'CATY', 'FFIN', 'SFNC']
}


def get_daily_data(ticker, outputsize='compact'):
    """Fetch daily stock data"""
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


def get_news_sentiment(ticker):
    """Get news and sentiment for a ticker"""
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': ticker,
        'apikey': API_KEY,
        'limit': 5
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'feed' not in data:
            return None
        
        news_items = data['feed']
        
        if not news_items:
            return None
        
        # Calculate sentiment scores
        sentiments = []
        recent_news = []
        
        for item in news_items[:5]:  # Top 5 news items
            ticker_sentiment = None
            for ticker_data in item.get('ticker_sentiment', []):
                if ticker_data['ticker'] == ticker:
                    ticker_sentiment = float(ticker_data.get('ticker_sentiment_score', 0))
                    break
            
            if ticker_sentiment:
                sentiments.append(ticker_sentiment)
                recent_news.append({
                    'title': item.get('title', ''),
                    'sentiment': ticker_sentiment,
                    'time': item.get('time_published', '')
                })
        
        if not sentiments:
            return None
        
        return {
            'avg_sentiment': sum(sentiments) / len(sentiments),
            'news_count': len(sentiments),
            'recent_news': recent_news
        }
    
    except Exception as e:
        return None


def analyze_sector_strength(ticker):
    """Quick sector strength analysis"""
    df = get_daily_data(ticker)
    
    if df is None or len(df) < 20:
        return None
    
    recent_20 = df.tail(20).copy()
    recent_5 = df.tail(5).copy()
    
    price_1d = ((recent_20.iloc[-1]['Close'] - recent_20.iloc[-2]['Close']) / recent_20.iloc[-2]['Close']) * 100
    price_5d = ((recent_5.iloc[-1]['Close'] - recent_5.iloc[0]['Close']) / recent_5.iloc[0]['Close']) * 100
    
    momentum_score = (price_1d * 0.5) + (price_5d * 0.5)
    
    return momentum_score


def check_breakout_quality(df, ticker):
    """
    Enhanced breakout analysis with quality scoring
    Returns score 0-100 based on multiple factors
    """
    if df is None or len(df) < 30:
        return None
    
    recent = df.tail(50).copy()
    
    # Calculate indicators
    recent['SMA_10'] = recent['Close'].rolling(window=10).mean()
    recent['SMA_20'] = recent['Close'].rolling(window=20).mean()
    recent['SMA_50'] = recent['Close'].rolling(window=50).mean()
    
    today = recent.iloc[-1]
    today_date = recent.index[-1]
    lookback_data = recent.iloc[-21:-1]
    
    # Basic metrics
    prev_high = lookback_data['High'].max()
    avg_volume = lookback_data['Volume'].mean()
    
    # Breakout criteria
    price_breakout = today['Close'] > prev_high
    volume_spike = today['Volume'] > avg_volume * 1.5
    above_sma10 = today['Close'] > today['SMA_10'] if not pd.isna(today['SMA_10']) else False
    above_sma20 = today['Close'] > today['SMA_20'] if not pd.isna(today['SMA_20']) else False
    uptrend = today['SMA_10'] > today['SMA_20'] if not pd.isna(today['SMA_10']) and not pd.isna(today['SMA_20']) else False
    
    if not price_breakout:
        return None
    
    # Quality Score (0-100)
    quality_score = 0
    
    # 1. Breakout strength (0-25 points)
    breakout_pct = ((today['Close'] - prev_high) / prev_high) * 100
    if breakout_pct > 5:
        quality_score += 25
    elif breakout_pct > 3:
        quality_score += 20
    elif breakout_pct > 1:
        quality_score += 15
    else:
        quality_score += 10
    
    # 2. Volume confirmation (0-25 points)
    volume_ratio = today['Volume'] / avg_volume
    if volume_ratio > 3:
        quality_score += 25
    elif volume_ratio > 2:
        quality_score += 20
    elif volume_ratio > 1.5:
        quality_score += 15
    else:
        quality_score += 5
    
    # 3. Trend alignment (0-25 points)
    if above_sma10 and above_sma20 and uptrend:
        quality_score += 25
    elif above_sma10 and above_sma20:
        quality_score += 20
    elif above_sma10 or above_sma20:
        quality_score += 10
    
    # 4. Consolidation quality (0-25 points)
    # Check if stock consolidated before breakout
    consolidation_period = lookback_data.iloc[-10:]
    price_range = (consolidation_period['High'].max() - consolidation_period['Low'].min()) / consolidation_period['Close'].mean()
    
    if price_range < 0.10:  # Tight consolidation < 10%
        quality_score += 25
    elif price_range < 0.15:
        quality_score += 20
    elif price_range < 0.20:
        quality_score += 15
    else:
        quality_score += 5
    
    return {
        'ticker': ticker,
        'date': today_date.strftime('%Y-%m-%d'),
        'close': round(today['Close'], 2),
        'prev_high': round(prev_high, 2),
        'breakout_pct': round(breakout_pct, 2),
        'volume': int(today['Volume']),
        'avg_volume': int(avg_volume),
        'volume_ratio': round(volume_ratio, 2),
        'quality_score': quality_score,
        'sma_10': round(today['SMA_10'], 2) if not pd.isna(today['SMA_10']) else 0,
        'sma_20': round(today['SMA_20'], 2) if not pd.isna(today['SMA_20']) else 0,
    }


def main():
    """Main execution"""
    print("=" * 80)
    print("SMART SECTOR BREAKOUT SCANNER")
    print("=" * 80)
    print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Identify strongest sector
    print("STEP 1: Analyzing sector strength...")
    print("-" * 80)
    
    sector_scores = {}
    for etf, sector_name in SECTOR_ETFS.items():
        print(f"Analyzing {sector_name} ({etf})...", end=' ')
        momentum = analyze_sector_strength(etf)
        if momentum:
            sector_scores[sector_name] = momentum
            print(f"Momentum: {momentum:+.2f}")
        else:
            print("Failed")
        time.sleep(0.5)
    
    if not sector_scores:
        print("\n❌ Could not analyze sectors")
        return
    
    # Find strongest sector with available stocks
    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    
    strongest_sector = None
    sector_stocks = []
    
    for sector_name, momentum in sorted_sectors:
        stocks = SECTOR_STOCKS.get(sector_name, [])
        if stocks:
            strongest_sector = (sector_name, momentum)
            sector_stocks = stocks
            break
    
    if not strongest_sector:
        print("\n❌ No sectors with available stocks found")
        return
    
    print(f"\n✅ STRONGEST SECTOR (with stocks): {strongest_sector[0]} (Momentum: {strongest_sector[1]:+.2f})")
    
    # Step 2: Scan stocks in strongest sector
    print(f"\nSTEP 2: Scanning stocks in {strongest_sector[0]} sector...")
    print("-" * 80)
    
    breakout_candidates = []
    
    for ticker in sector_stocks:
        print(f"Scanning {ticker}...", end=' ')
        
        df = get_daily_data(ticker)
        breakout = check_breakout_quality(df, ticker)
        
        if breakout:
            # Step 3: Get news sentiment
            print("✓ Breakout found, checking news...", end=' ')
            news = get_news_sentiment(ticker)
            
            if news:
                breakout['news_sentiment'] = round(news['avg_sentiment'], 3)
                breakout['news_count'] = news['news_count']
                breakout['has_news'] = True
                
                # Adjust quality score based on sentiment
                if news['avg_sentiment'] > 0.2:
                    breakout['quality_score'] += 10  # Bonus for positive news
                elif news['avg_sentiment'] < -0.2:
                    breakout['quality_score'] -= 10  # Penalty for negative news
                
                print(f"✓ News sentiment: {news['avg_sentiment']:+.3f}")
            else:
                breakout['news_sentiment'] = 0
                breakout['news_count'] = 0
                breakout['has_news'] = False
                print("⚠️  No recent news")
            
            breakout_candidates.append(breakout)
        else:
            print("- No breakout")
        
        time.sleep(0.5)
    
    if not breakout_candidates:
        print(f"\n❌ No breakouts found in {strongest_sector[0]} sector")
        return
    
    # Step 4: Rank by quality score
    df_results = pd.DataFrame(breakout_candidates)
    df_results = df_results.sort_values('quality_score', ascending=False)
    
    print("\n" + "=" * 80)
    print(f"BREAKOUT OPPORTUNITIES IN {strongest_sector[0].upper()} SECTOR")
    print("=" * 80)
    print(f"\nFound {len(df_results)} breakout(s), ranked by quality:\n")
    
    for idx, row in df_results.iterrows():
        quality_label = "🔥 EXCELLENT" if row['quality_score'] >= 75 else "✓ GOOD" if row['quality_score'] >= 60 else "⚠️  MODERATE"
        news_label = f"📰 {row['news_sentiment']:+.3f}" if row['has_news'] else "📰 None"
        tradingview_url = f"https://www.tradingview.com/chart/?symbol={row['ticker']}"
        
        print(f"{quality_label} - {row['ticker']} - Quality Score: {row['quality_score']}/100")
        print(f"   Price: ${row['close']} | Breakout: +{row['breakout_pct']}% | Volume: {row['volume_ratio']:.2f}x")
        print(f"   News: {news_label} ({row['news_count']} articles)")
        print(f"   📊 Chart: {tradingview_url}")
        print()
    
    # Display full table
    print("\n" + "=" * 80)
    print("DETAILED METRICS")
    print("=" * 80)
    print(df_results.to_string(index=False))
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f"smart_breakout_{strongest_sector[0].lower().replace(' ', '_')}_{timestamp}.csv"
    json_file = f"smart_breakout_{strongest_sector[0].lower().replace(' ', '_')}_{timestamp}.json"
    
    df_results.to_csv(csv_file, index=False)
    df_results.to_json(json_file, orient='records', indent=2)
    
    print("\n" + "=" * 80)
    print(f"✅ Results saved to:")
    print(f"   - {csv_file}")
    print(f"   - {json_file}")
    print("=" * 80)
    
    return df_results, strongest_sector[0]


if __name__ == "__main__":
    main()
