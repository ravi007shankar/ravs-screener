#!/usr/bin/env python3
"""
RavsTrades High-Quality Momentum Screener
Relaxed criteria for testing - keeps drone, space, data center focus
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

# RELAXED CRITERIA - will show results even on weekends
MIN_PRICE = 5               # Was $10
MIN_MARKET_CAP = 100_000_000  # Was $1B, now $100M
MIN_VOLUME = 500_000        # Was 1M, now 500K
MIN_RVOL = 1.0              # Was 2.0, now 1.0x
MIN_CHANGE = 1.0            # Was 3%, now 1%
MAX_STOCKS = 30             # Show top 30

# FOCUSED UNIVERSE - Drones, Space, Data Center + quality liquid stocks
RAVS_UNIVERSE = [
    # === 🚁 DRONE STOCKS (Priority) ===
    'EH', 'UAVS', 'DPRO', 'TAKOF', 'AMPX', 'KULR', 'NNDM',
    
    # === 🚀 SPACE STOCKS (Priority) ===
    'SPCE', 'RKLB', 'ASTS', 'SATL', 'SPIR', 'BKSY', 'LLAP', 'MYNA', 'REDW', 'VORB',
    
    # === 🏢 DATA CENTER / AI INFRASTRUCTURE (Priority) ===
    'VST', 'CEG', 'SMR', 'OKLO', 'BWXT', 'NNE', 'RGTI', 'IONQ', 'QBTS', 'CORZ', 'GPU',
    
    # === 🤖 AI CHIP / PHOTONICS ===
    'ARM', 'COHR', 'LITE', 'ACMR', 'CAMT', 'KLIC', 'UCTT', 'PDFS', 'SIMO', 'MXL',
    
    # === LIQUID LARGE CAPS (for baseline) ===
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'AMD', 'NFLX',
    'CRM', 'ORCL', 'ADBE', 'PANW', 'CRWD', 'SNOW', 'PLTR', 'COIN', 'SHOP', 'ROKU',
    
    # === SEMICONDUCTORS ===
    'ASML', 'LRCX', 'KLAC', 'AMAT', 'QCOM', 'MU', 'MRVL', 'NXPI', 'SWKS', 'ON',
    
    # === CLEAN ENERGY ===
    'ENPH', 'SEDG', 'FSLR', 'NXT', 'NOVA', 'RUN', 'SPWR',
    
    # === EV / AUTO ===
    'NIO', 'RIVN', 'LCID', 'FSR',
    
    # === CRYPTO ===
    'MSTR', 'RIOT', 'MARA', 'HUT', 'BITF', 'CLSK',
    
    # === BIOTECH ===
    'MRNA', 'VRTX', 'REGN', 'GILD', 'AMGN',
    
    # === MEME / MOMENTUM ===
    'GME', 'AMC', 'BB', 'TLRY',
]

# Sector definitions
DRONE_STOCKS = ['EH', 'UAVS', 'DPRO', 'TAKOF', 'AMPX', 'KULR', 'NNDM']
SPACE_STOCKS = ['SPCE', 'RKLB', 'ASTS', 'SATL', 'SPIR', 'BKSY', 'LLAP', 'MYNA', 'REDW', 'VORB']
DATACENTER_STOCKS = ['VST', 'CEG', 'SMR', 'OKLO', 'BWXT', 'NNE', 'RGTI', 'IONQ', 'QBTS', 'CORZ', 'GPU']
AI_CHIP_STOCKS = ['ARM', 'COHR', 'LITE', 'ACMR', 'CAMT', 'KLIC', 'UCTT', 'PDFS', 'SIMO', 'MXL']

def get_stock_data(ticker):
    """Get stock data - relaxed criteria"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        market_cap = info.get('marketCap', 0)
        
        # Relaxed filters
        if current_price < MIN_PRICE:
            return None
        if market_cap < MIN_MARKET_CAP:
            return None
            
        # Get 10 days history
        hist = stock.history(period="10d", interval="1d")
        if len(hist) < 5:
            return None
            
        # Calculate EMAs
        ema_9 = hist['Close'].ewm(span=9).mean().iloc[-1]
        ema_20 = hist['Close'].ewm(span=20).mean().iloc[-1]
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        
        if avg_volume < MIN_VOLUME:
            return None
            
        rvol = current_volume / avg_volume if avg_volume > 0 else 0
        
        if rvol < MIN_RVOL:
            return None
            
        # Price change
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        if abs(change_pct) < MIN_CHANGE:  # Any movement, positive or negative
            return None
            
        # 20-day high/low
        high_20d = hist['High'].max()
        low_20d = hist['Low'].min()
        
        return {
    'ticker': ticker,
    'price': float(price),              # Convert numpy types
    'change_pct': float(change_pct),
    'rvol': float(rvol),
    'volume': int(current_volume),
    'avg_volume': int(avg_volume),
    'market_cap': int(market_cap),
    'ema_9': float(ema_9),
    'ema_20': float(ema_20),
    'high_20d': float(high_20d),
    'low_20d': float(low_20d),
    'above_ema20': bool(current_price > ema_20),  # Convert to Python bool
}
        
    except Exception as e:
        return None

def classify_setup(data):
    """Classify setup with sector awareness - relaxed"""
    ticker = data['ticker']
    change = data['change_pct']
    rvol = data['rvol']
    price = data['price']
    high_20d = data['high_20d']
    
    # Determine sector
    sector_emoji = ""
    sector_name = ""
    is_priority = False
    
    if ticker in DRONE_STOCKS:
        sector_emoji = "🚁"
        sector_name = "Drone"
        is_priority = True
    elif ticker in SPACE_STOCKS:
        sector_emoji = "🚀"
        sector_name = "Space"
        is_priority = True
    elif ticker in DATACENTER_STOCKS:
        sector_emoji = "🏢"
        sector_name = "Data Center"
        is_priority = True
    elif ticker in AI_CHIP_STOCKS:
        sector_emoji = "🤖"
        sector_name = "AI Chip"
        is_priority = True
    
    # Breakout detection
    is_breakout = price > high_20d * 0.98
    
    # Relaxed conviction scoring
    conviction = 0
    
    # Base score from RVOL (0-40 points)
    conviction += min(int(rvol * 10), 40)
    
    # Change score (0-30 points)
    conviction += min(int(abs(change) * 3), 30)
    
    # Trend score (0-20 points)
    if data['above_ema20']:
        conviction += 20
    else:
        conviction += 10
    
    # Setup type bonus (0-10 points)
    if is_breakout:
        setup_type = f"{sector_emoji} {sector_name} Breakout" if sector_name else "🔥 Breakout"
        conviction += 10
    elif is_priority and abs(change) > 3:
        setup_type = f"{sector_emoji} {sector_name} Momentum" if sector_name else "Momentum"
        conviction += 8
    elif is_priority:
        setup_type = f"{sector_emoji} {sector_name}" if sector_name else "Trend"
        conviction += 5
    else:
        setup_type = "Ravs Watch"
    
    conviction = min(conviction, 100)
    
    # Entry/stop/target
    entry = f"${price:.2f}"
    stop = f"${round(price * 0.95, 2)}"
    target = f"${round(price * 1.06, 2)}"
    
    # Risk/Reward
    risk = price * 0.05
    reward = price * 0.06
    rr_ratio = round(reward / risk, 1) if risk > 0 else 1.2
    
 return {
    **data,
    'setup_type': setup_type,
    'sector': sector_name,
    'sector_emoji': sector_emoji,
    'is_breakout': bool(is_breakout),  # Convert to Python bool
    'is_priority': bool(is_priority),   # Convert to Python bool
    'entry': entry,
    'stop': stop,
    'target': target,
    'conviction': int(conviction),      # Ensure int
    'risk_reward': float(rr_ratio)      # Ensure float
}

def run_ravs_screener():
    """Main screener - relaxed for testing"""
    print(f"🔥 RavsTrades Screener (Relaxed)")
    print(f"Scanning {len(RAVS_UNIVERSE)} stocks...")
    print(f"Priority: 🚁 Drones | 🚀 Space | 🏢 Data Center | 🤖 AI Chip")
    print(f"Criteria: Price ${MIN_PRICE}+ | RVOL {MIN_RVOL}x+ | Change {MIN_CHANGE}%+\n")
    
    results = []
    
    for i, ticker in enumerate(RAVS_UNIVERSE, 1):
        if i % 20 == 0:
            print(f"Progress: {i}/{len(RAVS_UNIVERSE)} | Found: {len(results)}")
            
        data = get_stock_data(ticker)
        if not data:
            continue
            
        enriched = classify_setup(data)
        
        # Relaxed threshold - show conviction 40+
        if enriched['conviction'] >= 40:
            results.append(enriched)
            print(f"✅ {ticker}: {enriched['setup_type']} | {enriched['change_pct']:+.1f}% | RVOL {enriched['rvol']}x | Conviction {enriched['conviction']}")
    
    # Sort: priority sectors first, then by conviction
    results = sorted(results, key=lambda x: (-x['is_priority'], -x['conviction']))[:MAX_STOCKS]
    
    output = {
        'scanner_name': 'RavsTrades Screener',
        'version': '3.1-relaxed',
        'timestamp': datetime.now().isoformat(),
        'universe_size': len(RAVS_UNIVERSE),
        'criteria': {
            'min_price': MIN_PRICE,
            'min_market_cap': f"${MIN_MARKET_CAP/1e6:.0f}M",
            'min_volume': f"{MIN_VOLUME/1e6:.0f}M",
            'min_rvol': MIN_RVOL,
            'min_change': f"{MIN_CHANGE}%",
            'min_conviction': 40
        },
        'count': len(results),
        'stocks': results
    }
    
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n🎯 Complete! Found {len(results)} setups")
    print(f"Saved to public/data/ravs_screener.json")
    
    if results:
        print(f"\nTop setups:")
        for r in results[:5]:
            print(f"  {r['ticker']}: {r['setup_type']} | ${r['price']} | {r['change_pct']:+.1f}% | Conviction {r['conviction']}")
    
    return results

if __name__ == "__main__":
    run_ravs_screener()
