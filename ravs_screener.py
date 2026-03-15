#!/usr/bin/env python3
"""
RavsTrades Momentum Screener - TradingView Style
Matches your TradingView filters: Price >$3, RVOL >0.5, Positive change
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

# TradingView-style criteria (relaxed)
MIN_PRICE = 3
MIN_MARKET_CAP = 100_000_000  # $100M
MIN_VOLUME = 200_000          # 200K average
MIN_RVOL = 0.5                # 0.5x like TradingView shows
MAX_STOCKS = 100

# Top liquid stocks (expand as needed)
RAVS_UNIVERSE = [
    # Mag 7 + Large Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'TSM',
    'AMD', 'NFLX', 'CRM', 'ORCL', 'ADBE', 'INTU', 'PANW', 'CRWD', 'SNOW',
    'NOW', 'TEAM', 'SHOP', 'SQ', 'PLTR', 'DDOG', 'MDB', 'NET', 'FSLY',
    'TWLO', 'OKTA', 'ZM', 'DOCU', 'ABNB', 'UBER', 'LYFT', 'DASH', 'RBLX',
    # Semiconductors
    'ASML', 'LRCX', 'KLAC', 'AMAT', 'QCOM', 'MU', 'MRVL', 'NXPI', 'SWKS', 'ON',
    'ENTG', 'ICLR', 'CCMP', 'SLAB', 'RMBS', 'DIOD', 'PDFS', 'SIMO',
    # Growth/Momentum
    'ROKU', 'TWLO', 'OKTA', 'ZM', 'DOCU', 'ABNB', 'UBER', 'LYFT', 'DASH', 
    'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST', 'LMND', 'ROOT', 'TOST',
    # Clean Energy
    'ENPH', 'SEDG', 'FSLR', 'NXT', 'ARRY', 'NOVA', 'RUN', 'SPWR', 'MAXN',
    'SHLS', 'AMPS', 'GPRE', 'REGI', 'GEVO', 'CLNE',
    # Biotech/Pharma
    'MRNA', 'BNTX', 'VRTX', 'REGN', 'BIIB', 'GILD', 'AMGN', 'SGEN', 'INCY',
    'BMRN', 'ALNY', 'IONS', 'SRPT', 'VIR', 'BEAM', 'CRSP', 'EDIT', 'NTLA',
    # Crypto/Blockchain
    'MSTR', 'COIN', 'RIOT', 'MARA', 'HUT', 'BITF', 'CLSK', 'ARBK', 'CORZ',
    'BTBT', 'SDIG', 'WULF', 'IREN', 'DMG', 'HIVE',
    # EV/Auto
    'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'GOEV', 'WKHS', 'ARVL',
    'PSNY', 'MULN', 'CENN', 'KNDI',
    # Chinese Tech
    'BABA', 'JD', 'PDD', 'TME', 'BIDU', 'DIDI', 'ZH', 'FUTU', 'TIGR', 'VIPS',
    'MOMO', 'YY', 'HUYA', 'DOYU', 'BZ', 'QFIN', 'LX', 'AIH', 'JFU',
    # Meme/Momentum
    'GME', 'AMC', 'BB', 'NOK', 'BBBY', 'SPCE', 'TLRY', 'SNDL', 'KOSS', 'EXPR',
    'NAKD', 'CTRM', 'ZOM', 'IDEX', 'NNDM', 'AGTC', 'OCGN', 'SENS',
    # Financials/Fintech
    'GS', 'MS', 'BLK', 'C', 'BAC', 'WFC', 'JPM', 'AXP', 'COF', 'SCHW',
    'IBKR', 'TROW', 'BLK', 'STT', 'BEN', 'NTRS', 'KEY', 'CFG', 'RF', 'HBAN',
    # Industrials/Materials
    'CAT', 'DE', 'NUE', 'STLD', 'CLF', 'X', 'MT', 'FCX', 'SCCO', 'TECK',
    'RS', 'ATI', 'CRS', 'CMC', 'TMST', 'WOR', 'HY', 'CENX', 'AA', 'KALU',
    # Retail/Consumer
    'COST', 'TGT', 'WMT', 'HD', 'LOW', 'NKE', 'LULU', 'RH', 'BBY', 'AZO',
    'ORLY', 'AAP', 'DG', 'DLTR', 'BIG', 'TJX', 'ROST', 'BURL', 'LE', 'ANF',
    # Energy
    'XOM', 'CVX', 'COP', 'EOG', 'PXD', 'OXY', 'MPC', 'VLO', 'PSX', 'ET',
    'MPLX', 'EPD', 'ETP', 'WMB', 'KMI', 'OKE', 'TRGP', 'CNX', 'RRC', 'SWN',
    # REITs/Real Estate
    'AMT', 'PLD', 'CCI', 'EQIX', 'DLR', 'PSA', 'O', 'WPC', 'VICI', 'EXR',
    'CUBE', 'REXR', 'FR', 'EGP', 'MAA', 'UDR', 'CPT', 'AVB', 'ESS', 'EQR',
    # Airlines/Travel
    'DAL', 'UAL', 'AAL', 'LUV', 'JBLU', 'ALK', 'SAVE', 'MESA', 'SKYW', 'HA',
    'CCL', 'RCL', 'NCLH', 'LIND', 'VTR', 'WYNN', 'MGM', 'CZR', 'BYD', 'PENN',
    # Healthcare
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'DHR', 'BMY',
    'CI', 'HUM', 'CVS', 'WBA', 'RAD', 'COR', 'CAH', 'MCK', 'ABC', 'HSIC',
    # Food/Beverage
    'KO', 'PEP', 'MCD', 'SBUX', 'YUM', 'CMG', 'DPZ', 'WING', 'CAVA', 'NDAQ',
    'DRI', 'CAKE', 'EAT', 'TXRH', 'BLMN', 'DIN', 'PLAY', 'BJRI', 'RRGB', 'DENN',
    # Gaming/Esports
    'ATVI', 'EA', 'TTWO', 'U', 'SNOW', 'NVDA', 'AMD', 'INTC', 'TCEHY',
    # Space/Defense
    'LMT', 'NOC', 'GD', 'RTX', 'BA', 'HII', 'TDG', 'HEI', 'CW', 'SPCE',
    # Streaming/Media
    'NFLX', 'DIS', 'PARA', 'FOX', 'WBD', 'ROKU', 'T', 'VZ', 'CMCSA', 'CHTR',
    # Cybersecurity
    'PANW', 'FTNT', 'CYBR', 'ZS', 'SPLK', 'OKTA', 'NET', 'RPD', 'TENB',
    # E-commerce
    'AMZN', 'ETSY', 'EBAY', 'W', 'CHWY', 'CVNA', 'VRM', 'REAL', 'LEAF',
    # Cannabis
    'TLRY', 'CGC', 'ACB', 'CRON', 'GTBIF', 'CURLF', 'TCNNF', 'VRNOF', 'PLNHF',
    # 3D Printing
    'DDD', 'SSYS', 'DM', 'MKFG', 'VLD', 'MTLS', 'NNDM', 'PRLB', 'ONON',
    # EV Charging
    'CHPT', 'BLNK', 'EVGO', 'VLTA', 'WBX', 'SPWR', 'ENPH', 'SEDG', 'FSLR', 'NOVA',
]

def get_stock_data(ticker):
    """Get stock data - TradingView style"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        market_cap = info.get('marketCap', 0)
        
        # Basic filters
        if current_price < MIN_PRICE:
            return None
        if market_cap < MIN_MARKET_CAP:
            return None
            
        # Get 10 days history (TradingView uses 10-day avg)
        hist = stock.history(period="10d", interval="1d")
        if len(hist) < 5:
            return None
            
        # TradingView Relative Volume = Today / 10-Day Average
        avg_volume_10d = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        
        if avg_volume_10d < MIN_VOLUME:
            return None
            
        rvol = current_volume / avg_volume_10d if avg_volume_10d > 0 else 0
        
        # Much lower threshold like TradingView
        if rvol < MIN_RVOL:
            return None
            
        # Price change
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1]
        current_price = hist['Close'].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # Must have positive change (like your TradingView filter)
        if change_pct <= 0:
            return None
            
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'change_pct': round(change_pct, 2),
            'rvol': round(rvol, 2),
            'volume': int(current_volume),
            'avg_volume': int(avg_volume_10d),
            'market_cap': market_cap,
        }
        
    except Exception as e:
        print(f"Error on {ticker}: {str(e)[:50]}")
        return None

def classify_setup(data):
    """Classify setup type and calculate conviction"""
    change = data['change_pct']
    rvol = data['rvol']
    
    # Setup types based on momentum
    if change > 5 and rvol > 1.5:
        setup_type = "🔥 Ravs Breakout"
        conviction = min(70 + int(change), 95)
    elif change > 3:
        setup_type = "Ravs Momentum"
        conviction = min(50 + int(change * 2), 85)
    elif rvol > 1.0:
        setup_type = "Ravs Volume"
        conviction = min(40 + int(rvol * 15), 75)
    else:
        setup_type = "Ravs Watch"
        conviction = min(25 + int(change), 60)
    
    # Simple entry/stop/target
    current = data['price']
    entry = f"${current:.2f}"
    stop = f"${round(current * 0.97, 2)}"
    target = f"${round(current * 1.05, 2)}"
    
    return {
        **data,
        'setup_type': setup_type,
        'entry': entry,
        'stop': stop,
        'target': target,
        'conviction': conviction,
        'risk_reward': round(5/3, 2)  # 5% target / 3% stop
    }

def run_ravs_screener():
    """Main screener"""
    print(f"🔥 RavsTrades Momentum Screener")
    print(f"Scanning {len(RAVS_UNIVERSE)} stocks...")
    print(f"Criteria: Price ${MIN_PRICE}+ | RVOL {MIN_RVOL}x+ | Change >0%\n")
    
    results = []
    
    for i, ticker in enumerate(RAVS_UNIVERSE, 1):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(RAVS_UNIVERSE)} | Found: {len(results)}")
            
        data = get_stock_data(ticker)
        if not data:
            continue
            
        # Classify setup
        enriched = classify_setup(data)
        
        # Include all with conviction >= 20 (much lower)
        if enriched['conviction'] >= 20:
            results.append(enriched)
            print(f"✅ {ticker}: {enriched['setup_type']} | +{enriched['change_pct']}% | RVOL {enriched['rvol']}x | {enriched['conviction']}/100")
    
    # Sort by conviction
    results = sorted(results, key=lambda x: x['conviction'], reverse=True)[:MAX_STOCKS]
    
    # Prepare output
    output = {
        'scanner_name': 'RavsTrades Momentum Screener',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'universe_size': len(RAVS_UNIVERSE),
        'criteria': {
            'min_price': MIN_PRICE,
            'min_market_cap': MIN_MARKET_CAP,
            'min_volume': MIN_VOLUME,
            'min_rvol': MIN_RVOL
        },
        'count': len(results),
        'stocks': results
    }
    
    # Save
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n🎯 Complete! Found {len(results)} setups")
    print(f"Saved to public/data/ravs_screener.json")
    
    if results:
        print(f"\nTop 5 setups:")
        for r in results[:5]:
            print(f"  {r['ticker']}: {r['setup_type']} | ${r['price']} | +{r['change_pct']}% | Conviction {r['conviction']}")
    
    return results

if __name__ == "__main__":
    run_ravs_screener()
