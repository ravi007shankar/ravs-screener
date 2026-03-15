#!/usr/bin/env python3
"""
RavsTrades Momentum Screener
Scans 500+ stocks for high-conviction momentum setups
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

# Ravs Criteria
MIN_PRICE = 3
MIN_MARKET_CAP = 300_000_000
MIN_VOLUME = 500_000
MIN_RVOL = 1.5
MAX_STOCKS = 50

RAVS_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'TSM',
    'AMD', 'NFLX', 'CRM', 'ORCL', 'ADBE', 'INTU', 'PANW', 'CRWD', 'SNOW',
    'PLTR', 'COIN', 'ROKU', 'SQ', 'SHOP', 'DDOG', 'MDB', 'NET', 'FSLY',
    'TWLO', 'OKTA', 'ZM', 'DOCU', 'ABNB', 'UBER', 'LYFT', 'DASH', 'RBLX',
    'ENPH', 'SEDG', 'FSLR', 'NXT', 'ARRY', 'NOVA', 'RUN', 'SPWR', 'MAXN',
    'MRNA', 'BNTX', 'VRTX', 'REGN', 'BIIB', 'GILD', 'AMGN', 'SGEN', 'INCY',
    'MSTR', 'HOOD', 'RIOT', 'MARA', 'HUT', 'BITF', 'CLSK', 'ARBK', 'CORZ',
    'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'GOEV', 'WKHS', 'ARVL',
    'BABA', 'JD', 'PDD', 'TME', 'BIDU', 'DIDI', 'ZH', 'FUTU', 'TIGR',
    'GME', 'AMC', 'BB', 'NOK', 'SPCE', 'TLRY', 'SNDL', 'KOSS', 'EXPR',
    'GS', 'MS', 'BLK', 'C', 'BAC', 'WFC', 'JPM', 'AXP', 'COF', 'SOFI',
    'CAT', 'DE', 'NUE', 'STLD', 'CLF', 'X', 'MT', 'FCX', 'SCCO', 'TECK',
    'COST', 'TGT', 'WMT', 'HD', 'LOW', 'NKE', 'LULU', 'RH', 'BBY', 'AZO',
    'XOM', 'CVX', 'COP', 'EOG', 'PXD', 'OXY', 'MPC', 'VLO', 'PSX', 'ET',
    'AMT', 'PLD', 'CCI', 'EQIX', 'DLR', 'PSA', 'O', 'WPC', 'VICI', 'EXR',
    'DAL', 'UAL', 'AAL', 'LUV', 'JBLU', 'ALK', 'SAVE', 'MESA', 'SKYW', 'HA',
    'CCL', 'RCL', 'NCLH', 'LIND', 'WYNN', 'MGM', 'CZR', 'BYD', 'PENN',
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'DHR', 'BMY',
    'KO', 'PEP', 'MCD', 'SBUX', 'YUM', 'CMG', 'DPZ', 'WING', 'CAVA',
    'ATVI', 'EA', 'TTWO', 'U', 'RBLX', 'NVDA', 'AMD', 'INTC',
    'LMT', 'NOC', 'GD', 'RTX', 'BA', 'HII', 'TDG', 'HEI', 'CW', 'SPCE',
    'NFLX', 'DIS', 'PARA', 'FOX', 'WBD', 'ROKU', 'T', 'VZ', 'CMCSA', 'CHTR',
    'PANW', 'FTNT', 'CYBR', 'ZS', 'SPLK', 'OKTA', 'NET', 'RPD', 'TENB',
    'AMZN', 'ETSY', 'EBAY', 'W', 'CHWY', 'CVNA', 'VRM', 'REAL',
    'TLRY', 'CGC', 'ACB', 'CRON', 'GTBIF', 'CURLF', 'TCNNF',
    'DDD', 'SSYS', 'DM', 'MKFG', 'VLD', 'MTLS', 'NNDM', 'PRLB',
    'CHPT', 'BLNK', 'EVGO', 'VLTA', 'WBX', 'SPWR', 'ENPH', 'SEDG',
    'ASML', 'LRCX', 'KLAC', 'AMAT', 'QCOM', 'MU', 'MRVL', 'NXPI', 'SWKS', 'ON',
    'NOW', 'TEAM', 'ATLASSIAN', 'ZEN', 'PLAN', 'SMAR', 'WORK'
]

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        market_cap = info.get('marketCap', 0)
        
        if current_price < MIN_PRICE or market_cap < MIN_MARKET_CAP:
            return None
            
        hist = stock.history(period="20d", interval="1d")
        if len(hist) < 15:
            return None
            
        avg_volume_20d = hist['Volume'].mean()
        
        today = stock.history(period="1d", interval="5m", prepost=True)
        if today.empty:
            return None
            
        current_volume = today['Volume'].sum()
        
        rvol = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0
        
        if avg_volume_20d < MIN_VOLUME or rvol < MIN_RVOL:
            return None
            
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        if abs(change_pct) < 0.5:
            return None
            
        high_20d = hist['High'].max()
        low_20d = hist['Low'].min()
        
        ema_9 = hist['Close'].ewm(span=9).mean().iloc[-1]
        ema_21 = hist['Close'].ewm(span=21).mean().iloc[-1]
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'change_pct': round(change_pct, 2),
            'volume': int(current_volume),
            'avg_volume_20d': int(avg_volume_20d),
            'rvol': round(rvol, 2),
            'market_cap': market_cap,
            'high_20d': round(high_20d, 2),
            'low_20d': round(low_20d, 2),
            'ema_9': round(ema_9, 2),
            'ema_21': round(ema_21, 2),
            'prev_close': round(prev_close, 2)
        }
        
    except Exception as e:
        return None

def find_ravs_levels(data):
    try:
        ticker = data['ticker']
        stock = yf.Ticker(ticker)
        
        hist = stock.history(period="20d", interval="1h")
        if hist.empty:
            return data
            
        current = data['price']
        
        highs = hist['High'].rolling(window=3, center=True).max()
        swing_highs = hist[hist['High'] == highs]['High'].values
        
        lows = hist['Low'].rolling(window=3, center=True).min()
        swing_lows = hist[hist['Low'] == lows]['Low'].values
        
        vwap_daily = (hist['Close'] * hist['Volume']).sum() / hist['Volume'].sum()
        
        ema_9 = data['ema_9']
        ema_21 = data['ema_21']
        
        def cluster(levels, threshold=0.015):
            if len(levels) == 0:
                return []
            levels = sorted(set([round(l, 2) for l in levels if l > 0]))
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if (level - current_cluster[-1]) / current_cluster[-1] < threshold:
                    current_cluster.append(level)
                else:
                    clusters.append(round(sum(current_cluster) / len(current_cluster), 2))
                    current_cluster = [level]
                    
            clusters.append(round(sum(current_cluster) / len(current_cluster), 2))
            return sorted(clusters)
        
        resistance_levels = cluster(swing_highs)
        support_levels = cluster(swing_lows)
        
        valid_resistance = [r for r in resistance_levels if r > current * 1.005]
        valid_support = [s for s in support_levels if s < current * 0.995]
        
        nearest_resistance = min(valid_resistance) if valid_resistance else data['high_20d']
        nearest_support = max(valid_support) if valid_support else data['low_20d']
        
        setup_type = "None"
        entry = ""
        stop = ""
        target = ""
        setup_quality = 0
        
        if current > nearest_resistance * 0.998 and data['rvol'] >= 2.5:
            setup_type = "Ravs Breakout"
            entry = f"${current:.2f}"
            stop = f"${max(nearest_support, round(current * 0.97, 2)):.2f}"
            target = f"${round(nearest_resistance * 1.05, 2)}"
            setup_quality = 40
            
        elif current > data['ema_21'] and current < nearest_resistance * 0.95 and data['rvol'] >= 2.0:
            setup_type = "Ravs Pullback"
            entry = f"${current:.2f}"
            stop = f"${round(nearest_support * 0.98, 2)}"
            target = f"${round(nearest_resistance * 0.98, 2)}"
            setup_quality = 35
            
        elif current > data['ema_9'] * 0.99 and current < data['ema_9'] * 1.01 and data['rvol'] >= 2.0:
            setup_type = "Ravs EMA Bounce"
            entry = f"${current:.2f}"
            stop = f"${round(data['ema_21'], 2)}"
            target = f"${round(nearest_resistance, 2)}"
            setup_quality = 30
            
        elif current > data['high_20d'] * 0.995 and data['rvol'] >= 2.0:
            setup_type = "Ravs Range Break"
            entry = f"${current:.2f}"
            stop = f"${round(data['high_20d'] * 0.98, 2)}"
            target = f"${round(current * 1.08, 2)}"
            setup_quality = 38
        
        rvol_score = min(data['rvol'] * 12, 35)
        change_score = min(abs(data['change_pct']) * 1.5, 20)
        trend_score = 15 if current > data['ema_21'] else 5
        setup_score = setup_quality
        volume_score = 10 if data['volume'] > 2000000 else 5
        
        conviction = min(rvol_score + change_score + trend_score + setup_score + volume_score, 100)
        
        return {
            **data,
            'ravs_resistance': nearest_resistance,
            'ravs_support': nearest_support,
            'ravs_vwap': round(vwap_daily, 2),
            'setup_type': setup_type,
            'entry': entry,
            'stop': stop,
            'target': target,
            'conviction': conviction,
            'risk_reward': round((float(target.replace('$', '')) - current) / (current - float(stop.replace('$', ''))), 2) if target and stop else 0
        }
        
    except Exception as e:
        return {**data, 'setup_type': 'Error', 'conviction': 0}

def run_ravs_screener():
    print(f"🔥 RavsTrades Momentum Screener")
    print(f"Scanning {len(RAVS_UNIVERSE)} stocks...\n")
    
    results = []
    
    for i, ticker in enumerate(RAVS_UNIVERSE, 1):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(RAVS_UNIVERSE)} | Found: {len(results)} setups")
            
        data = get_stock_data(ticker)
        if not data:
            continue
            
        enriched = find_ravs_levels(data)
        
        if enriched['conviction'] >= 40 and enriched['setup_type'] != "None":
            results.append(enriched)
            print(f"✅ {ticker}: {enriched['setup_type']} | {enriched['conviction']}/100")
    
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values('conviction', ascending=False).head(MAX_STOCKS)
    
    output = {
        'scanner_name': 'RavsTrades Momentum Screener',
        'version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'universe_size': len(RAVS_UNIVERSE),
        'count': len(results_df),
        'stocks': results_df.to_dict('records') if not results_df.empty else []
    }
    
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n🎯 Complete! Found {len(results_df)} setups")
    if not results_df.empty:
        print(f"Top: {results_df.iloc[0]['ticker']} - {results_df.iloc[0]['setup_type']}")
    
    return results_df

if __name__ == "__main__":
    run_ravs_screener()
