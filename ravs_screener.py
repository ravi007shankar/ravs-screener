#!/usr/bin/env python3
"""
RavsTrades High-Quality Momentum Screener
Only A+ setups with institutional backing
Includes: Drones, Space, Data Center, AI Infrastructure
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

# HIGH-QUALITY CRITERIA
MIN_PRICE = 10              # Higher quality stocks
MIN_MARKET_CAP = 1_000_000_000  # $1B+ (institutional grade)
MIN_VOLUME = 1_000_000      # 1M+ daily volume
MIN_RVOL = 2.0              # 2x+ relative volume (institutional activity)
MIN_CHANGE = 3.0            # 3%+ move (real momentum)
MAX_STOCKS = 25             # Only top 25 best setups

# COMPLETE UNIVERSE - All sectors
RAVS_UNIVERSE = [
    # === MEGA CAP TECH ===
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'TSM',
    'AMD', 'NFLX', 'CRM', 'ORCL', 'ADBE', 'INTU', 'PANW', 'CRWD', 'SNOW',
    'NOW', 'SHOP', 'SQ', 'PLTR', 'DDOG', 'MDB', 'NET', 'FSLY',
    
    # === SEMICONDUCTORS ===
    'ASML', 'LRCX', 'KLAC', 'AMAT', 'QCOM', 'MU', 'MRVL', 'NXPI', 'SWKS', 'ON',
    'ENTG', 'ICLR', 'CCMP', 'SLAB', 'RMBS', 'DIOD', 'PDFS', 'SIMO',
    
    # === GROWTH/MOMENTUM ===
    'ROKU', 'TWLO', 'OKTA', 'ZM', 'DOCU', 'ABNB', 'UBER', 'LYFT', 'DASH', 
    'RBLX', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST', 'LMND', 'ROOT', 'TOST',
    
    # === CLEAN ENERGY ===
    'ENPH', 'SEDG', 'FSLR', 'NXT', 'ARRY', 'NOVA', 'RUN', 'SPWR', 'MAXN',
    'SHLS', 'AMPS', 'GPRE', 'REGI', 'GEVO', 'CLNE',
    
    # === BIOTECH/PHARMA ===
    'MRNA', 'BNTX', 'VRTX', 'REGN', 'BIIB', 'GILD', 'AMGN', 'SGEN', 'INCY',
    'BMRN', 'ALNY', 'IONS', 'SRPT', 'VIR', 'BEAM', 'CRSP', 'EDIT', 'NTLA',
    
    # === CRYPTO/BLOCKCHAIN ===
    'MSTR', 'COIN', 'RIOT', 'MARA', 'HUT', 'BITF', 'CLSK', 'ARBK', 'CORZ',
    'BTBT', 'SDIG', 'WULF', 'IREN', 'DMG', 'HIVE',
    
    # === EV/AUTO ===
    'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'FSR', 'GOEV', 'WKHS', 'ARVL',
    'PSNY', 'MULN', 'CENN', 'KNDI',
    
    # === CHINESE TECH ===
    'BABA', 'JD', 'PDD', 'TME', 'BIDU', 'DIDI', 'ZH', 'FUTU', 'TIGR', 'VIPS',
    'MOMO', 'YY', 'HUYA', 'DOYU', 'BZ', 'QFIN', 'LX', 'AIH', 'JFU',
    
    # === MEME/MOMENTUM ===
    'GME', 'AMC', 'BB', 'NOK', 'BBBY', 'SPCE', 'TLRY', 'SNDL', 'KOSS', 'EXPR',
    'NAKD', 'CTRM', 'ZOM', 'IDEX', 'NNDM', 'AGTC', 'OCGN', 'SENS',
    
    # === FINANCIALS/FINTECH ===
    'GS', 'MS', 'BLK', 'C', 'BAC', 'WFC', 'JPM', 'AXP', 'COF', 'SCHW',
    'IBKR', 'TROW', 'BLK', 'STT', 'BEN', 'NTRS', 'KEY', 'CFG', 'RF', 'HBAN',
    
    # === INDUSTRIALS/MATERIALS ===
    'CAT', 'DE', 'NUE', 'STLD', 'CLF', 'X', 'MT', 'FCX', 'SCCO', 'TECK',
    'RS', 'ATI', 'CRS', 'CMC', 'TMST', 'WOR', 'HY', 'CENX', 'AA', 'KALU',
    
    # === RETAIL/CONSUMER ===
    'COST', 'TGT', 'WMT', 'HD', 'LOW', 'NKE', 'LULU', 'RH', 'BBY', 'AZO',
    'ORLY', 'AAP', 'DG', 'DLTR', 'BIG', 'TJX', 'ROST', 'BURL', 'LE', 'ANF',
    
    # === ENERGY ===
    'XOM', 'CVX', 'COP', 'EOG', 'PXD', 'OXY', 'MPC', 'VLO', 'PSX', 'ET',
    'MPLX', 'EPD', 'ETP', 'WMB', 'KMI', 'OKE', 'TRGP', 'CNX', 'RRC', 'SWN',
    
    # === REITS/REAL ESTATE ===
    'AMT', 'PLD', 'CCI', 'EQIX', 'DLR', 'PSA', 'O', 'WPC', 'VICI', 'EXR',
    'CUBE', 'REXR', 'FR', 'EGP', 'MAA', 'UDR', 'CPT', 'AVB', 'ESS', 'EQR',
    
    # === AIRLINES/TRAVEL ===
    'DAL', 'UAL', 'AAL', 'LUV', 'JBLU', 'ALK', 'SAVE', 'MESA', 'SKYW', 'HA',
    'CCL', 'RCL', 'NCLH', 'LIND', 'VTR', 'WYNN', 'MGM', 'CZR', 'BYD', 'PENN',
    
    # === HEALTHCARE ===
    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'DHR', 'BMY',
    'CI', 'HUM', 'CVS', 'WBA', 'RAD', 'COR', 'CAH', 'MCK', 'ABC', 'HSIC',
    
    # === FOOD/BEVERAGE ===
    'KO', 'PEP', 'MCD', 'SBUX', 'YUM', 'CMG', 'DPZ', 'WING', 'CAVA', 'NDAQ',
    'DRI', 'CAKE', 'EAT', 'TXRH', 'BLMN', 'DIN', 'PLAY', 'BJRI', 'RRGB', 'DENN',
    
    # === GAMING/ESPORTS ===
    'ATVI', 'EA', 'TTWO', 'RBLX', 'U', 'SNOW', 'NVDA', 'AMD', 'INTC', 'TCEHY',
    
    # === SPACE/DEFENSE ===
    'LMT', 'NOC', 'GD', 'RTX', 'BA', 'HII', 'TDG', 'HEI', 'CW',
    
    # === STREAMING/MEDIA ===
    'NFLX', 'DIS', 'PARA', 'FOX', 'WBD', 'ROKU', 'T', 'VZ', 'CMCSA', 'CHTR',
    
    # === CYBERSECURITY ===
    'PANW', 'FTNT', 'CYBR', 'ZS', 'SPLK', 'OKTA', 'NET', 'RPD', 'TENB',
    
    # === E-COMMERCE ===
    'AMZN', 'ETSY', 'EBAY', 'W', 'CHWY', 'CVNA', 'VRM', 'REAL', 'LEAF',
    
    # === CANNABIS ===
    'TLRY', 'CGC', 'ACB', 'CRON', 'GTBIF', 'CURLF', 'TCNNF', 'VRNOF', 'PLNHF',
    
    # === 3D PRINTING ===
    'DDD', 'SSYS', 'DM', 'MKFG', 'VLD', 'MTLS', 'NNDM', 'PRLB', 'ONON',
    
    # === EV CHARGING ===
    'CHPT', 'BLNK', 'EVGO', 'VLTA', 'WBX', 'SPWR', 'ENPH', 'SEDG', 'FSLR', 'NOVA',
    
    # === 🚁 DRONE STOCKS ===
    'EH',      # EHang - autonomous aerial vehicles
    'UAVS',    # AgEagle Aerial Systems
    'DPRO',    # Draganfly
    'TAKOF',   # Drone Delivery Canada
    'AMPX',    # Amprius Technologies - drone batteries
    'KULR',    # KULR Technology - battery safety
    'NNDM',    # Nano Dimension - 3D printed electronics
    
    # === 🚀 SPACE STOCKS ===
    'SPCE',    # Virgin Galactic
    'RKLB',    # Rocket Lab
    'ASTS',    # AST SpaceMobile
    'SATL',    # Satellogic
    'SPIR',    # Spire Global
    'BKSY',    # BlackSky
    'LLAP',    # Terran Orbital
    'MYNA',    # Mynaric - laser communication
    'REDW',    # Redwire - space infrastructure
    'VORB',    # Virgin Orbit
    
    # === 🏢 DATA CENTER / AI INFRASTRUCTURE ===
    'VST',     # Vistra - power for AI data centers
    'CEG',     # Constellation Energy - nuclear power
    'SMR',     # NuScale Power - small modular reactors
    'OKLO',    # Oklo - advanced nuclear
    'BWXT',    # BWX Technologies - nuclear components
    'NNE',     # Nano Nuclear Energy
    'RGTI',    # Rigetti Computing - quantum
    'IONQ',    # IonQ - quantum computing
    'QBTS',    # D-Wave Quantum
    'CORZ',    # CoreWeave - AI cloud infrastructure
    'GPU',     # Aligned Data Centers
    
    # === 🤖 AI CHIP / PHOTONICS ===
    'ARM',     # ARM Holdings
    'COHR',    # Coherent - photonics
    'LITE',    # Lumentum - optical networking
    'ACMR',    # ACM Research - semiconductor equipment
    'CAMT',    # Camtek - inspection
    'KLIC',    # Kulicke & Soffa - chip bonding
    'UCTT',    # Ultra Clean Holdings
    'PDFS',    # PDF Solutions
    'SIMO',    # Silicon Motion
    'MXL',     # MaxLinear
]

# Sector definitions for classification
DRONE_STOCKS = ['EH', 'UAVS', 'DPRO', 'TAKOF', 'AMPX', 'KULR', 'NNDM']
SPACE_STOCKS = ['SPCE', 'RKLB', 'ASTS', 'SATL', 'SPIR', 'BKSY', 'LLAP', 'MYNA', 'REDW', 'VORB']
DATACENTER_STOCKS = ['VST', 'CEG', 'SMR', 'OKLO', 'BWXT', 'NNE', 'RGTI', 'IONQ', 'QBTS', 'CORZ', 'GPU']
AI_CHIP_STOCKS = ['ARM', 'COHR', 'LITE', 'ACMR', 'CAMT', 'KLIC', 'UCTT', 'PDFS', 'SIMO', 'MXL']

def get_stock_data(ticker):
    """Get high-quality stock data"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        market_cap = info.get('marketCap', 0)
        
        # Strict filters
        if current_price < MIN_PRICE:
            return None
        if market_cap < MIN_MARKET_CAP:
            return None
            
        # Get 20 days for EMA calculation
        hist = stock.history(period="20d", interval="1d")
        if len(hist) < 15:
            return None
            
        # Calculate EMAs
        ema_9 = hist['Close'].ewm(span=9).mean().iloc[-1]
        ema_20 = hist['Close'].ewm(span=20).mean().iloc[-1]
        ema_50 = hist['Close'].ewm(span=50).mean().iloc[-1] if len(hist) >= 50 else ema_20
        
        # Must be above key MAs (trend alignment)
        if current_price < ema_20:
            return None
            
        # Volume analysis
        avg_volume_20d = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        
        if avg_volume_20d < MIN_VOLUME:
            return None
            
        rvol = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0
        
        if rvol < MIN_RVOL:
            return None
            
        # Price change
        prev_close = hist['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        if change_pct < MIN_CHANGE:
            return None
            
        # 20-day high for breakout detection
        high_20d = hist['High'].max()
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'change_pct': round(change_pct, 2),
            'rvol': round(rvol, 2),
            'volume': int(current_volume),
            'avg_volume': int(avg_volume_20d),
            'market_cap': market_cap,
            'ema_9': round(ema_9, 2),
            'ema_20': round(ema_20, 2),
            'high_20d': round(high_20d, 2),
            'trend_aligned': current_price > ema_50,
        }
        
    except Exception as e:
        return None

def classify_setup(data):
    """Classify high-quality setup with sector awareness"""
    ticker = data['ticker']
    change = data['change_pct']
    rvol = data['rvol']
    price = data['price']
    high_20d = data['high_20d']
    
    # Determine sector
    sector_emoji = ""
    sector_name = ""
    if ticker in DRONE_STOCKS:
        sector_emoji = "🚁"
        sector_name = "Drone"
    elif ticker in SPACE_STOCKS:
        sector_emoji = "🚀"
        sector_name = "Space"
    elif ticker in DATACENTER_STOCKS:
        sector_emoji = "🏢"
        sector_name = "Data Center"
    elif ticker in AI_CHIP_STOCKS:
        sector_emoji = "🤖"
        sector_name = "AI Chip"
    
    # Breakout detection (within 2% of 20-day high)
    is_breakout = price > high_20d * 0.98
    
    # Quality scoring
    quality_score = 0
    
    # RVOL component (0-30 points)
    if rvol >= 4.0:
        quality_score += 30
    elif rvol >= 3.0:
        quality_score += 28
    elif rvol >= 2.5:
        quality_score += 25
    else:
        quality_score += 20
    
    # Change component (0-25 points)
    if change >= 8:
        quality_score += 25
    elif change >= 5:
        quality_score += 22
    elif change >= 4:
        quality_score += 18
    else:
        quality_score += 15
    
    # Trend component (0-20 points)
    if data['trend_aligned']:
        quality_score += 20
    else:
        quality_score += 10
    
    # Setup type with sector
    if is_breakout and change >= 5:
        if sector_name:
            setup_type = f"{sector_emoji} {sector_name} Breakout"
        else:
            setup_type = "🔥 Ravs Breakout"
        quality_score += 25
    elif is_breakout:
        if sector_name:
            setup_type = f"{sector_emoji} {sector_name} Breakout"
        else:
            setup_type = "Ravs Breakout"
        quality_score += 20
    elif change >= 5 and rvol >= 2.5:
        if sector_name:
            setup_type = f"{sector_emoji} {sector_name} Momentum"
        else:
            setup_type = "Ravs Momentum"
        quality_score += 15
    else:
        if sector_name:
            setup_type = f"{sector_emoji} {sector_name} Trend"
        else:
            setup_type = "Ravs Trend"
        quality_score += 10
    
    conviction = min(quality_score, 100)
    
    # Risk management - tight stops for high conviction
    if is_breakout:
        stop_price = data['ema_9'] * 0.98  # Stop below 9 EMA
    else:
        stop_price = price * 0.95  # 5% stop
    
    target_price = price * 1.08  # 8% target
    
    entry = f"${price:.2f}"
    stop = f"${round(stop_price, 2)}"
    target = f"${round(target_price, 2)}"
    
    # Risk/Reward ratio
    risk = price - stop_price
    reward = target_price - price
    rr_ratio = round(reward / risk, 2) if risk > 0 else 0
    
    return {
        **data,
        'setup_type': setup_type,
        'sector': sector_name,
        'sector_emoji': sector_emoji,
        'is_breakout': is_breakout,
        'entry': entry,
        'stop': stop,
        'target': target,
        'conviction': conviction,
        'risk_reward': rr_ratio
    }

def run_ravs_screener():
    """Main high-quality screener"""
    print(f"🔥 RavsTrades HIGH-QUALITY Screener")
    print(f"Scanning {len(RAVS_UNIVERSE)} stocks...")
    print(f"Criteria: Price ${MIN_PRICE}+ | MCap ${MIN_MARKET_CAP/1e9:.0f}B+ | RVOL {MIN_RVOL}x+ | Change +{MIN_CHANGE}%+")
    print(f"Sectors: 🚁 Drones | 🚀 Space | 🏢 Data Center | 🤖 AI Chip\n")
    
    results = []
    
    for i, ticker in enumerate(RAVS_UNIVERSE, 1):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(RAVS_UNIVERSE)} | Found: {len(results)}")
            
        data = get_stock_data(ticker)
        if not data:
            continue
            
        enriched = classify_setup(data)
        
        # Only A+ setups (conviction >= 70, R/R >= 1.5)
        if enriched['conviction'] >= 70 and enriched['risk_reward'] >= 1.5:
            results.append(enriched)
            print(f"✅ {ticker}: {enriched['setup_type']} | +{enriched['change_pct']}% | RVOL {enriched['rvol']}x | Conviction {enriched['conviction']}/100 | R/R {enriched['risk_reward']}:1")
    
    # Sort by conviction, then by RVOL
    results = sorted(results, key=lambda x: (x['conviction'], x['rvol']), reverse=True)[:MAX_STOCKS]
    
    output = {
        'scanner_name': 'RavsTrades High-Quality Screener',
        'version': '3.0',
        'timestamp': datetime.now().isoformat(),
        'universe_size': len(RAVS_UNIVERSE),
        'criteria': {
            'min_price': MIN_PRICE,
            'min_market_cap': f"${MIN_MARKET_CAP/1e9:.0f}B",
            'min_volume': f"{MIN_VOLUME/1e6:.0f}M",
            'min_rvol': MIN_RVOL,
            'min_change': f"{MIN_CHANGE}%",
            'min_conviction': 70
        },
        'count': len(results),
        'stocks': results
    }
    
    os.makedirs('public/data', exist_ok=True)
    
    with open('public/data/ravs_screener.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n🎯 Complete! Found {len(results)} HIGH-QUALITY setups")
    print(f"Saved to public/data/ravs_screener.json")
    
    if results:
        print(f"\n🏆 TOP SETUPS:")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r['ticker']}: {r['setup_type']} | ${r['price']} | +{r['change_pct']}% | Conviction {r['conviction']}/100 | R/R {r['risk_reward']}:1")
    
    return results

if __name__ == "__main__":
    run_ravs_screener()
