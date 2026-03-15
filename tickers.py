#!/usr/bin/env python3
"""
RavsTrades Ticker Lists - Sectors + Stocks
"""

# SECTOR ETFs - Track money flow/rotation
SECTOR_ETFS = {
    "Technology": "XLK",
    "Semiconductors": "SMH",
    "Software": "IGV",
    "Cybersecurity": "CIBR",
    "AI & Robotics": "BOTZ",
    "Biotech": "XBI",
    "Healthcare": "XLV",
    "Financial": "XLF",
    "Fintech": "FINX",
    "Energy": "XLE",
    "Solar": "TAN",
    "Nuclear": "NLR",
    "Uranium": "URA",
    "Oil & Gas": "XOP",
    "Industrials": "XLI",
    "Aerospace": "ITA",
    "Defense": "PPA",
    "Materials": "XLB",
    "Gold Miners": "GDX",
    "Silver": "SLV",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Retail": "XRT",
    "Gaming": "BJK",
    "ESports": "NERD",
    "Blockchain": "BLOK",
    "Crypto": "BITO",
    "Internet": "FDN",
    "Cloud Computing": "SKYY",
    "5G": "FIVG",
    "Space": "UFO",
    "Drone": "IFLY",
    "Electric Vehicles": "DRIV",
    "Battery & Lithium": "LIT",
    "Clean Energy": "ICLN",
    "Genomics": "ARKG",
    "Fintech Innovation": "ARKF",
    "Innovation": "ARKK",
    "Web3": "WIII",
    "Metaverse": "META",
    "Quantum Computing": "QTUM",
    "Nanotech": "PXN",
}

# INDIVIDUAL STOCKS by Sector
STOCKS_BY_SECTOR = {
    "AI": ["NVDA", "AMD", "PLTR", "PATH", "SOUN", "BBAI", "AI", "ARM", "MSFT", "GOOGL", "META", "AMZN", "IBM", "ORCL"],
    
    "Semiconductors": ["NVDA", "AMD", "ASML", "AVGO", "INTC", "QCOM", "MU", "MRVL", "NXPI", "SWKS", "ON", "LRCX", "KLAC", "AMAT", "TXN", "ADI"],
    
    "Software": ["MSFT", "GOOGL", "META", "ORCL", "CRM", "ADBE", "NOW", "SNOW", "DDOG", "NET", "OKTA", "ZS", "CRWD", "PLTR", "PATH"],
    
    "Cybersecurity": ["CRWD", "PANW", "FTNT", "CYBR", "S", "OKTA", "ZS", "NET", "DDOG", "QLYS", "TENB"],
    
    "Cloud": ["AMZN", "MSFT", "GOOGL", "CRM", "NOW", "SNOW", "DDOG", "NET", "FSLY", "TWLO"],
    
    "Biotech": ["MRNA", "VRTX", "REGN", "GILD", "AMGN", "BIIB", "ILMN", "CRSP", "EDIT", "NTLA", "BEAM", "VCEL"],
    
    "Pharma": ["JNJ", "PFE", "MRK", "LLY", "ABBV", "BMY", "AZN", "NVO", "RPRX"],
    
    "Fintech": ["SQ", "PYPL", "SOFI", "UPST", "AFRM", "HOOD", "COIN", "NU", "PAGS", "DLO"],
    
    "Crypto": ["MSTR", "RIOT", "MARA", "HUT", "BITF", "CORZ", "BTBT", "CLSK", "WULF", "IREN", "COIN"],
    
    "EV": ["TSLA", "NIO", "RIVN", "LCID", "XPEV", "LI", "FSR", "GOEV", "MULN", "PSNY"],
    
    "Energy": ["XOM", "CVX", "COP", "EOG", "MPC", "VLO", "PSX", "OXY", "DVN", "FANG"],
    
    "Solar": ["ENPH", "SEDG", "FSLR", "RUN", "NOVA", "SPWR", "MAXN", "ARRY", "SHLS"],
    
    "Nuclear": ["VST", "CEG", "SMR", "OKLO", "NRG", "BWXT", "CCJ", "URA", "LEU"],
    
    "Data Center": ["VST", "CEG", "SMR", "OKLO", "DLR", "EQIX", "AMT", "CCI", "SBAC", "COR"],
    
    "Space": ["SPCE", "RKLB", "ASTS", "LMT", "NOC", "RTX", "BA", "AJRD", "MNTS", "VORB"],
    
    "Drone": ["EH", "UAVS", "DPRO", "AVAV"],
    
    "Defense": ["LMT", "NOC", "RTX", "GD", "BA", "HII", "LDOS", "KTOS", "AXON"],
    
    "Gaming": ["TTWO", "EA", "RBLX", "DKNG", "PENN", "CHDN", "IGT", "BYD", "CZR", "MGM"],
    
    "Retail": ["AMZN", "WMT", "TGT", "COST", "HD", "LOW", "BBY", "TJX", "ROST", "BURL"],
    
    "China Tech": ["BABA", "JD", "PDD", "NIO", "XPEV", "LI", "BIDU", "TCEHY", "DIDI", "BILI"],
    
    "Meme": ["GME", "AMC", "BB", "BBBY", "KOSS", "NAKD", "EXPR", "SPRT", "WOOF"],
    
    "Quantum": ["IBM", "GOOGL", "MSFT", "IONQ", "RGTI", "QBTS", "ARQQ"],
}

# Flatten all stocks for main list
ALL_STOCKS = []
seen = set()
for sector, tickers in STOCKS_BY_SECTOR.items():
    for t in tickers:
        if t not in seen:
            seen.add(t)
            ALL_STOCKS.append(t)

# Export
TICKERS = {
    "ETFS": SECTOR_ETFS,
    "STOCKS": ALL_STOCKS,
    "BY_SECTOR": STOCKS_BY_SECTOR
}
