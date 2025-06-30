Stock Factor Screener

Multi‑factor quality, value & growth screening for equity portfolios, built with Python, yfinance & Alpha Vantage.

Overview

StockFactorScreener.py automates collection, normalisation and scoring of fundamental metrics for a list of stock tickers. It produces:

Value metrics – Forward/Trailing P‑E, Price‑to‑Book, EBIT / Total‑Enterprise‑Value

Profitability metrics – ROE, ROA, Gross‑Profit‑to‑Assets (GPOA), Gross Profit Margin (GPMAR), Cash‑Flow‑over‑Assets (CFOA)

Growth metrics – CAGR of EPS, GPOA, ROE, ROA, CFOA, GPMAR plus earnings variability (EVAR)

Optional factor Z‑scores across Value, Profitability & Growth

A timestamped Excel workbook with all raw metrics and portfolio weights

Detailed logs for full traceability

Primary data comes from Yahoo Finance with Alpha Vantage as the fall‑back source. Heavy requests are processed concurrently using Python’s ThreadPoolExecutor.

Features

⚡ Thread‑pool concurrency for faster data retrieval

🔧 Pluggable JSON config – change tickers, weights, look‑back periods & API keys without editing code

📊 Excel output suited for further analysis or portfolio construction

🪵 Rich, configurable logging via Logging_config.json

📦 Self‑contained – no database or external services beyond data APIs

Quick start

git clone https://github.com/<your‑org>/stock‑factor‑screener.git
cd stock‑factor‑screener
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ScreenerConfig.example.json ScreenerConfig.json  # edit with your API key & tickers
python StockFactorScreener.py

A new Excel workbook will appear in the gen/ folder when the run completes.

Requirements

Python 3.10.4

Install them in one go:

pip install -r requirements.txt

Configuration (ScreenerConfig.json)

{
  "AlphaVantage": {
    "API_Key": "YOUR_ALPHA_VANTAGE_KEY",
    "Base_URL": "https://www.alphavantage.co/query"
  },
  "Earnings_Period": 5,
  "Tickers_and_Weights": [
    { "ticker": "AAPL", "weight": 0.10 },
    { "ticker": "MSFT", "weight": 0.08 }
  ],
  "Stock_Quality_Excel_Filename": "S&P600_Quality"
}

API_Key – free keys available at alphavantage.co

Earnings_Period – look‑back window (years) for growth/variability metrics

Tickers_and_Weights – initial portfolio weights used in output tables

Stock_Quality_Excel_Filename – base filename for Excel reports in gen/

Logging

Behaviour is controlled by Logging_config.json (standard logging dictConfig). By default a rolling file named StockFactorScreener.log is created alongside the script.

Output

Excel workbook: gen/YYYY-MM-DD_<base‑name>.xlsx

One row per ticker with all raw & derived metrics

Original portfolio weights preserved

Log file: step‑by‑step trace, API diagnostics and runtime stats

Roadmap

Add CLI flags (--config, --threads, etc.)

Publish Docker image for reproducible deployments

Integrate composite MSCI‑style factor scores

Unit tests (pytest) & GitHub Actions CI

Disclaimer

This software is for informational purposes only and does not constitute investment advice. Data may be incomplete or inaccurate; use at your own risk.

License

Copyright © 2025 Ivan Antunovic. All rights reserved. See LICENSE for details.

Contributing

Pull requests are welcome! For substantial changes, please open an issue first to discuss what you would like to change.

Author

Your Name – ivantun05@gmail.com

