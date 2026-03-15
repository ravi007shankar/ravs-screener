#!/usr/bin/env python3
"""
RavsTrades Web UI - Flask Backend
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from threading import Thread
from ravs_screener import run_screener
from tickers import TICKERS

app = Flask(__name__)
CORS(app)

TICKERS_FILE = 'user_tickers.json'
RESULTS_FILE = 'public/data/ravs_screener.json'


def load_user_tickers():
    """Load user-added tickers"""
    if os.path.exists(TICKERS_FILE):
        with open(TICKERS_FILE, 'r') as f:
            return json.load(f)
    return {"stocks": [], "etfs": []}


def save_user_tickers(data):
    with open(TICKERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    """Get all screener data"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "No data yet"})


@app.route('/api/run', methods=['POST'])
def manual_run():
    """Manually run screener"""
    def run():
        run_screener()
    Thread(target=run).start()
    return jsonify({"status": "started"})


@app.route('/api/tickers', methods=['GET'])
def get_tickers():
    """Get all available tickers"""
    return jsonify({
        'base': TICKERS,
        'user': load_user_tickers()
    })


@app.route('/api/tickers/stock', methods=['POST'])
def add_stock():
    """Add a stock ticker"""
    data = request.json
    ticker = data.get('ticker', '').upper().strip()
    sector = data.get('sector', 'General')
    
    if not ticker or len(ticker) > 5:
        return jsonify({'error': 'Invalid ticker'}), 400
    
    user_data = load_user_tickers()
    if ticker not in user_data['stocks']:
        user_data['stocks'].append(ticker)
        save_user_tickers(user_data)
        
        # Add to sector in TICKERS
        if sector in TICKERS['BY_SECTOR']:
            if ticker not in TICKERS['BY_SECTOR'][sector]:
                TICKERS['BY_SECTOR'][sector].append(ticker)
        else:
            TICKERS['BY_SECTOR'][sector] = [ticker]
        
        if ticker not in TICKERS['STOCKS']:
            TICKERS['STOCKS'].append(ticker)
    
    Thread(target=run_screener).start()
    return jsonify({'success': True})


@app.route('/api/tickers/stock/<ticker>', methods=['DELETE'])
def remove_stock(ticker):
    """Remove a stock ticker"""
    ticker = ticker.upper()
    user_data = load_user_tickers()
    
    if ticker in user_data['stocks']:
        user_data['stocks'].remove(ticker)
        save_user_tickers(user_data)
    
    if ticker in TICKERS['STOCKS']:
        TICKERS['STOCKS'].remove(ticker)
    
    for sector_list in TICKERS['BY_SECTOR'].values():
        if ticker in sector_list:
            sector_list.remove(ticker)
    
    Thread(target=run_screener).start()
    return jsonify({'success': True})


if __name__ == '__main__':
    # Run initial screener
    if not os.path.exists(RESULTS_FILE):
        print("Running initial screener...")
        run_screener()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
