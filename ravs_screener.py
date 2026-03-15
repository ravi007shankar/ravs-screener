#!/usr/bin/env python3
"""
RavsTrades Screener - Sector ETFs + Stocks
"""

import yfinance as yf
import json
from datetime import datetime
import os
from tickers import TICKERS

MIN_PRICE = 3.0
MIN_CHANGE_PCT = 0.01
MIN_AVG_VOLUME = 500000
MIN_MARKET_CAP = 300000000


def calculate_emas(prices, periods=[21, 50]):
    emas = {}
    for period in periods:
        if len(prices) >= period:
            ema = prices.ewm(span=period, adjust=False).mean().iloc[-1]
            emas[period] = float(ema)
    return emas


def scan_ticker(ticker, name=None, is_etf=False):
    """Scan any ticker (ETF or Stock)"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        info = stock.info
        
        if len(hist) < 50:
            return None
            
        price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2])
        change_pct = ((price - prev_close) / prev_close) * 100
        
        avg_volume_10d = float(hist['Volume'].tail(10).mean())
        current_volume = int(hist['Volume'].iloc[-1])
        rvol = current_volume / avg_volume_10d if avg_volume_10d > 0 else 0
        
        market_cap = info.get('marketCap', 0) or info.get('totalAssets', 0)
        if hasattr(market_cap, 'item'):
            market_cap = int(market_cap.item())
        else:
            market_cap = int(market_cap)
        
        # Skip filters for ETFs (they're benchmarks)
        if not is_etf:
            if price < MIN_PRICE:
                return None
            if abs(change_pct) < MIN_CHANGE_PCT:
                return None
            if avg_volume_10d < MIN_AVG_VOLUME:
                return None
            if market_cap < MIN_MARKET_CAP:
                return None
            
        emas = calculate_emas(hist['Close'])
        ema21 = emas.get(21, 0)
        ema50 = emas.get(50, 0)
        
        trend_bullish = (price > ema21) and (price > ema50)
        ema_aligned = ema21 > ema50
        
        # Conviction score
        conviction = 0
        
        if trend_bullish and ema_aligned:
            conviction += 30
        elif trend_bullish:
            conviction += 20
        elif ema_aligned:
            conviction += 10
            
        if rvol > 3.0:
            conviction += 25
        elif rvol > 2.0:
            conviction += 20
        elif rvol > 1.5:
            conviction += 15
        elif rvol > 1.0:
            conviction += 10
            
        if abs(change_pct) > 5:
            conviction += 25
        elif abs(change_pct) > 3:
            conviction += 20
        elif abs(change_pct) > 1:
            conviction += 15
        else:
            conviction += 10
            
        if market_cap > 10_000_000_000:
            conviction += 10
        elif market_cap > 1_000_000_000:
            conviction += 5
            
        conviction = min(conviction, 100)
        
        # Setup classification
        if abs(change_pct) > 5 and trend_bullish and rvol > 2:
            setup = "🔥 Strong"
        elif trend_bullish and rvol > 1.5:
            setup = "📈 Bullish"
        elif rvol > 2.0:
            setup = "⚡ Volume"
        elif trend_bullish:
            setup = "👍 Trend"
        else:
            setup = "⚠️ Weak"
            
        return {
            'ticker': ticker,
            'name': name or info.get('shortName', ticker),
            'price': round(price, 2),
            'change_pct': round(change_pct, 2),
            'rvol': round(rvol, 2),
            'volume': current_volume,
            'trend_bullish': trend_bullish,
            'ema_aligned': ema_aligned,
            'setup': setup,
            'conviction': conviction,
            'is_etf': is_etf
        }
        
    except Exception as e:
        print(f"❌ Error on {ticker}: {e}")
        return None


def run_screener():
    """Run full screener and return results"""
    print("=" * 70)
    print("🔥 RavsTrades Screener - Sector ETFs + Stocks")
    print("=" * 70)
    
    # === LAYER 1: SECTOR ETFs ===
    print("\n📊 SCANNING SECTOR ETFs (Money Flow)")
    print("-" * 70)
    
    sector_results = []
    for sector_name, etf_ticker in TICKERS["ETFS"].items():
        result = scan_ticker(etf_ticker, name=sector_name, is_etf=True)
        if result:
            result['sector_name'] = sector_name
            sector_results.append(result)
            trend_icon = "🟢" if result['trend_bullish'] else "🔴"
            print(f"{trend_icon} {sector_name:25} | {result['change_pct']:+6.2f}% | RVOL:{result['rvol']:4.1f}x | {result['setup']}")
    
    sector_results.sort(key=lambda x: (x['conviction'], abs(x['change_pct'])), reverse=True)
    hot_sectors = [s['sector_name'] for s in sector_results[:5]]
    
    print(f"\n🎯 HOT SECTORS: {', '.join(hot_sectors) if hot_sectors else 'None'}")
    
    # === LAYER 2: STOCKS ===
    print("\n" + "=" * 70)
    print("📈 SCANNING STOCKS")
    print("-" * 70)
    
    stock_results = []
    sector_map = {}
    for sector, tickers in TICKERS["BY_SECTOR"].items():
        for t in tickers:
            sector_map[t] = sector
    
    for ticker in TICKERS["STOCKS"]:
        result = scan_ticker(ticker)
        if result:
            sector = sector_map.get(ticker, "General")
            result['sector'] = sector
            
            # Boost if in hot sector
            if sector in hot_sectors:
                result['conviction'] = min(result['conviction'] + 15, 100)
                result['hot_sector'] = True
            else:
                result['hot_sector'] = False
                
            stock_results.append(result)
    
    stock_results.sort(key=lambda x: x['conviction'], reverse=True)
    
    # Display
    for s in stock_results[:25]:
        trend_icon = "🟢" if s['trend_bullish'] else "🔴"
        hot_icon = "🔥" if s.get('hot_sector') else "  "
        print(f"{hot_icon}{trend_icon} {s['ticker']:6} | {s['sector']:18} | {s['change_pct']:+6.2f}% | Conv:{s['conviction']:3}/100 | {s['setup']}")
    
    # Save
    output = {
        'timestamp': datetime.now().isoformat(),
        'hot_sectors': hot_sectors,
        'sector_etfs': sector_results,
        'stocks': {
            'total_scanned': len(TICKERS["STOCKS"]),
            'passed_filters': len(stock_results),
            'top_25': stock_results[:25]
        }
    }
    
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 70)
    print(f"💾 Saved | {len(sector_results)} sectors | {len(stock_results)} stocks")
    
    return output


if __name__ == "__main__":
    run_screener()
