#!/usr/bin/env python3
"""
RavsTrades Screener - Clean Version
"""

import yfinance as yf
import json
from datetime import datetime
import os

MIN_PRICE = 5
MIN_RVOL = 1.0
MIN_CHANGE = 1.0

TICKERS = [
    'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'AMD', 'COIN', 'GME',
    'EH', 'UAVS', 'DPRO', 'SPCE', 'RKLB', 'ASTS', 'VST', 'CEG', 'SMR', 'OKLO',
    'ENPH', 'SEDG', 'FSLR', 'NIO', 'RIVN', 'LCID', 'PLTR', 'CRWD', 'SNOW', 'ROKU',
    'ASML', 'LRCX', 'KLAC', 'AMAT', 'QCOM', 'MU', 'MRVL', 'NXPI', 'SWKS', 'ON',
    'MRNA', 'VRTX', 'REGN', 'GILD', 'AMGN', 'MSTR', 'RIOT', 'MARA', 'HUT', 'BITF'
]

DRONE_STOCKS = ['EH', 'UAVS', 'DPRO']
SPACE_STOCKS = ['SPCE', 'RKLB', 'ASTS']
DATACENTER_STOCKS = ['VST', 'CEG', 'SMR', 'OKLO']


def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if len(hist) < 2:
            return None
            
        price = float(hist['Close'].iloc[-1])
        prev = float(hist['Close'].iloc[-2])
        change = ((price - prev) / prev) * 100
        
        avg_vol = float(hist['Volume'].mean())
        curr_vol = float(hist['Volume'].iloc[-1])
        rvol = curr_vol / avg_vol if avg_vol > 0 else 0.0
        
        if price < MIN_PRICE or rvol < MIN_RVOL or abs(change) < MIN_CHANGE:
            return None
            
        sector = ""
        if ticker in DRONE_STOCKS:
            sector = "🚁 Drone"
        elif ticker in SPACE_STOCKS:
            sector = "🚀 Space"
        elif ticker in DATACENTER_STOCKS:
            sector = "🏢 Data Center"
            
        setup_type = f"{sector} Momentum" if sector else "Ravs Momentum"
        if change > 5:
            setup_type = f"{sector} Breakout" if sector else "🔥 Breakout"
            
        conviction = min(int(rvol * 20 + abs(change)), 100)
            
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'change_pct': round(change, 2),
            'rvol': round(rvol, 2),
            'volume': int(curr_vol),
            'setup_type': setup_type,
            'sector': sector,
            'entry': f"${round(price, 2)}",
            'stop': f"${round(price * 0.95, 2)}",
            'target': f"${round(price * 1.05, 2)}",
            'conviction': conviction,
            'risk_reward': 1.2,
            'is_breakout': bool(change > 5)
        }
    except Exception as e:
        print(f"Error on {ticker}: {e}")
        return None


def main():
    print("🔥 RavsTrades Screener Starting...")
    
    results = []
    for t in TICKERS:
        d = get_data(t)
        if d:
            results.append(d)
            print(f"✅ {d['ticker']}: {d['setup_type']} | {d['change_pct']:+.1f}% | Conviction {d['conviction']}")

    output = {
        'timestamp': datetime.now().isoformat(),
        'count': len(results),
        'stocks': sorted(results, key=lambda x: x['conviction'], reverse=True)[:25]
    }

    os.makedirs('public/data', exist_ok=True)
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n🎯 Found {len(results)} stocks")


if __name__ == "__main__":
    main()
