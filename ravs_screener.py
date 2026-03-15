#!/usr/bin/env python3
"""
RavsTrades Screener - TradingView Style
"""

import yfinance as yf
import json
from datetime import datetime
import os

# TradingView-style thresholds (from your screenshot)
MIN_PRICE = 3.0           # Price > 3 USD
MIN_CHANGE_PCT = 0.01     # Change > 0.01%
MIN_AVG_VOLUME = 500000   # Avg Volume 10D > 500K
MIN_MARKET_CAP = 300000000  # Market cap > 300M USD

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


def calculate_emas(prices, periods=[21, 50]):
    """Calculate EMAs for trend analysis"""
    emas = {}
    for period in periods:
        if len(prices) >= period:
            ema = prices.ewm(span=period, adjust=False).mean().iloc[-1]
            emas[period] = ema
    return emas


def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Get 60 days for proper EMA calculation
        hist = stock.history(period="60d")
        info = stock.info
        
        if len(hist) < 50:  # Need at least 50 days for EMA50
            return None
            
        # Current price and change
        price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2])
        change_pct = ((price - prev_close) / prev_close) * 100
        
        # Volume analysis (10-day average)
        avg_volume_10d = float(hist['Volume'].tail(10).mean())
        current_volume = float(hist['Volume'].iloc[-1])
        rvol = current_volume / avg_volume_10d if avg_volume_10d > 0 else 0
        
        # Market cap check
        market_cap = info.get('marketCap', 0)
        
        # Apply TradingView-style filters
        if price < MIN_PRICE:
            return None
        if abs(change_pct) < MIN_CHANGE_PCT:
            return None
        if avg_volume_10d < MIN_AVG_VOLUME:
            return None
        if market_cap < MIN_MARKET_CAP:
            return None
            
        # Calculate EMAs for trend alignment
        emas = calculate_emas(hist['Close'])
        ema21 = emas.get(21, 0)
        ema50 = emas.get(50, 0)
        
        # TradingView logic: EMA(50) < Price AND EMA(21) < Price (bullish trend)
        trend_bullish = (price > ema21) and (price > ema50)
        ema_aligned = ema21 > ema50  # Golden cross alignment
        
        # Sector tagging
        sector = ""
        if ticker in DRONE_STOCKS:
            sector = "🚁 Drone"
        elif ticker in SPACE_STOCKS:
            sector = "🚀 Space"
        elif ticker in DATACENTER_STOCKS:
            sector = "🏢 Data Center"
            
        # Enhanced conviction scoring (0-100)
        conviction = 0
        
        # Trend score (0-30)
        if trend_bullish and ema_aligned:
            conviction += 30
        elif trend_bullish:
            conviction += 20
        elif ema_aligned:
            conviction += 10
            
        # Volume score (0-25)
        if rvol > 3.0:
            conviction += 25
        elif rvol > 2.0:
            conviction += 20
        elif rvol > 1.5:
            conviction += 15
        elif rvol > 1.0:
            conviction += 10
            
        # Price action score (0-25)
        if change_pct > 5:
            conviction += 25
        elif change_pct > 3:
            conviction += 20
        elif change_pct > 1:
            conviction += 15
        elif change_pct > 0:
            conviction += 10
            
        # Market cap liquidity bonus (0-10)
        if market_cap > 10_000_000_000:  # >10B
            conviction += 10
        elif market_cap > 1_000_000_000:  # >1B
            conviction += 5
            
        # Sector momentum bonus (0-10)
        if sector and change_pct > 2:
            conviction += 10
            
        conviction = min(conviction, 100)
        
        # Setup classification
        if change_pct > 5 and trend_bullish and rvol > 2:
            setup_type = f"{sector} Breakout" if sector else "🔥 High Conviction Breakout"
        elif trend_bullish and rvol > 1.5:
            setup_type = f"{sector} Momentum" if sector else "📈 Trend Momentum"
        elif rvol > 2.0:
            setup_type = f"{sector} Volume Spike" if sector else "⚡ Volume Spike"
        else:
            setup_type = f"{sector} Watch" if sector else "👀 Watch List"
            
        # Risk management levels
        atr = float(hist['High'].tail(14).max() - hist['Low'].tail(14).min()) / 14
        stop_loss = round(price - (2 * atr), 2)
        target = round(price + (3 * atr), 2)
        risk_reward = round((target - price) / (price - stop_loss), 2) if (price - stop_loss) > 0 else 0
        
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'change_pct': round(change_pct, 2),
            'rvol': round(rvol, 2),
            'volume': int(current_volume),
            'avg_volume_10d': int(avg_volume_10d),
            'market_cap': market_cap,
            'ema21': round(ema21, 2),
            'ema50': round(ema50, 2),
            'trend_bullish': trend_bullish,
            'setup_type': setup_type,
            'sector': sector,
            'entry': f"${round(price, 2)}",
            'stop': f"${stop_loss}",
            'target': f"${target}",
            'conviction': conviction,
            'risk_reward': risk_reward,
            'is_breakout': bool(change_pct > 5 and rvol > 2)
        }
        
    except Exception as e:
        print(f"❌ Error on {ticker}: {e}")
        return None


def main():
    print("🔥 RavsTrades Screener (TradingView Style)")
    print("=" * 50)
    print(f"Filters: Price>${MIN_PRICE} | Change>{MIN_CHANGE_PCT}% | AvgVol>{MIN_AVG_VOLUME:,} | MarketCap>${MIN_MARKET_CAP/1e6:.0f}M")
    print("=" * 50)
    
    results = []
    filtered_count = 0
    
    for t in TICKERS:
        d = get_data(t)
        if d:
            results.append(d)
            trend_icon = "🟢" if d['trend_bullish'] else "🔴"
            print(f"{trend_icon} {d['ticker']:5} | {d['setup_type']:25} | {d['change_pct']:+6.2f}% | RVOL:{d['rvol']:4.1f}x | Conviction:{d['conviction']:3}/100")
        else:
            filtered_count += 1

    # Sort by conviction, then by change %
    results.sort(key=lambda x: (x['conviction'], x['change_pct']), reverse=True)
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'filters': {
            'min_price': MIN_PRICE,
            'min_change_pct': MIN_CHANGE_PCT,
            'min_avg_volume': MIN_AVG_VOLUME,
            'min_market_cap': MIN_MARKET_CAP
        },
        'count': len(results),
        'stocks': results[:25]
    }

    os.makedirs('public/data', exist_ok=True)
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 50)
    print(f"🎯 Found {len(results)} high-conviction stocks (filtered out {filtered_count})")
    print(f"💾 Saved to public/data/ravs_screener.json")
    
    if results:
        print(f"\n🏆 Top Pick: {results[0]['ticker']} - Conviction {results[0]['conviction']}/100")


if __name__ == "__main__":
    main()
