# 📈 Stock Market Intelligence Automation

An automated Python-based stock market intelligence system that collects market data, cleans and processes it, calculates technical indicators, generates transparent rule-based technical signals, stores the results in SQLite, and presents them through an interactive Streamlit dashboard.

The project is designed as a **local-first, low-cost market analysis pipeline** that can be automated using Windows Task Scheduler.

> **Disclaimer:** This project is for educational and research purposes only. The technical signals are rule-based indicators and should not be considered financial advice or recommendations to buy or sell securities.

---

## 🚀 Features

* 📥 Automated market data collection
* 🧹 Data cleaning and preprocessing
* 📊 Technical indicator calculation
* 🧠 Rule-based technical scoring system
* 📈 Trend, momentum, volume, quality and risk scoring
* 🗄️ SQLite database storage
* 🖥️ Interactive Streamlit dashboard
* 📉 Candlestick and technical indicator charts
* 🔎 Stock scanner with signal and score filters
* 📝 Automated analysis explanations
* 📋 Pipeline execution logs
* ⚙️ Single-command pipeline execution
* 💻 Designed to run locally with free/open-source Python tools

---

## 🏗️ System Architecture

```text
             ┌─────────────────────┐
             │    Market Data      │
             │     Provider        │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   Data Collector    │
             │    collector.py     │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │    Data Cleaner     │
             │     cleaner.py      │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Technical Analytics │
             │     analytics.py    │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │    SQLite Database  │
             │     database.py     │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Streamlit Dashboard │
             │     dashboard.py    │
             └─────────────────────┘
```

---

## 📂 Project Structure

```text
StockMarketAutomation/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│
├── logs/
│
├── src/
│   ├── collector.py
│   ├── cleaner.py
│   ├── analytics.py
│   ├── database.py
│   └── dashboard.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📊 Market Coverage

The current configuration monitors:

### Market Indices

* NIFTY 50
* Bank NIFTY
* SENSEX

### Stocks

* TCS
* Infosys
* HDFC Bank
* Reliance Industries
* ICICI Bank

The symbol list can be modified in `src/collector.py`.

---

## 📐 Technical Analysis

The analytics engine calculates several commonly used technical indicators.

### Trend Indicators

* SMA 20
* SMA 50
* SMA 200
* EMA 20
* EMA 50

### Momentum Indicators

* RSI
* MACD
* MACD Signal
* MACD Histogram
* ROC 20

### Volatility Indicators

* ATR
* ATR %
* 20-day volatility
* Bollinger Bands

### Volume Analysis

* Volume ratio

---

# 🧠 Technical Scoring System

The project uses a transparent rule-based scoring model.

The maximum score is:

```text
Trend       → 30 points
Momentum    → 30 points
Volume      → 15 points
Quality     → 15 points
Risk        → 10 points
────────────────────────
Total       → 100 points
```

## Signal Classification

```text
75 – 100  → Strong Setup
60 – 74   → Positive
40 – 59   → Neutral
0  – 39   → Weak
```

These labels describe the output of the project's predefined rules. They are **not investment recommendations**.

---

## 📈 Market Regime

The system identifies the current technical regime using moving-average relationships.

### Bullish Trend

```text
Close > SMA20 > SMA50 > SMA200
```

### Bearish Trend

```text
Close < SMA20 < SMA50 < SMA200
```

### Otherwise

```text
Sideways / Mixed
```

---

## 💡 Momentum State

Momentum is classified using RSI and MACD.

```text
Strong Positive
Positive
Neutral
Weak
```

The classification is based on predefined conditions in `analytics.py`.

---

## ⚠️ Volatility State

The system categorizes 20-day volatility as:

```text
Low
Normal
High
Very High
```

This provides additional context when interpreting technical signals.

---

# 🖥️ Dashboard

The Streamlit dashboard provides several sections.

## Market Overview

Displays:

* Latest market data
* Technical scores
* Market regimes
* Signal distribution
* Top scoring stocks

## Stock Scanner

Allows filtering stocks by:

* Signal
* Minimum technical score

It also displays:

* Trend score
* Momentum score
* Volume score
* Quality score
* Risk score
* RSI
* ROC
* ATR %
* Volatility
* Market regime
* Momentum state

## Technical Analysis

For an individual symbol, the dashboard provides:

* Candlestick chart
* SMA 20 / 50 / 200
* RSI
* MACD
* ATR
* ATR %
* Bollinger Bands
* 20-day volatility
* Technical score breakdown
* Automated explanation

---

# ⚙️ Installation

## Requirements

Recommended:

```text
Python 3.11+
Git
Windows / Linux / macOS
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/surya-hash-coder/StockMarketAutomation.git
```

Then:

```bash
cd StockMarketAutomation
```

Replace the repository URL with your actual GitHub repository if the repository name is different.

---

## 2. Create Virtual Environment

### Windows

```cmd
python -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

You should see:

```text
(.venv)
```

in your terminal.

---

## 3. Install Dependencies

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

# ▶️ Run the Pipeline

Run:

```cmd
python main.py
```

The pipeline performs:

```text
1. Market Data Collection
2. Data Cleaning
3. Technical Analytics
4. SQLite Database Update
```

The generated database is:

```text
database/stock_market.db
```

Logs are stored in:

```text
logs/
```

---

# 🖥️ Start the Dashboard

After running the pipeline:

```cmd
python -m streamlit run src\dashboard.py
```

Open:

```text
http://localhost:8501
```

The dashboard will load the latest data from SQLite.

---

# 🔄 Complete Workflow

The normal workflow is:

```cmd
python main.py
```

then:

```cmd
python -m streamlit run src\dashboard.py
```

In production-like local usage, the first command can be scheduled using **Windows Task Scheduler**.

---

# 🗄️ Database

The project uses SQLite through SQLAlchemy.

Database:

```text
database/stock_market.db
```

### Tables

#### `market_data`

Contains cleaned historical market data.

Example fields:

```text
date
symbol
open
high
low
close
adj_close
volume
daily_return
```

#### `market_analysis`

Contains technical analysis results.

Example fields:

```text
date
symbol
rsi
macd
macd_signal
atr
technical_score
trend_score
momentum_score
volume_score
quality_score
risk_score
market_regime
momentum_state
volatility_state
signal
analysis_explanation
```

---

# 🔐 Git & Data Safety

Generated files are intentionally excluded from Git.

The repository should not contain:

```text
.venv/
*.db
*.csv
*.log
__pycache__/
```

The `.gitignore` file prevents these local/generated files from being committed.

After cloning the project, the user can generate fresh data by running:

```cmd
python main.py
```

---

# 🧪 Project Validation

The database pipeline performs validation checks including:

* Market record count
* Analysis record count
* Symbol count
* Required V4 analytics columns
* NULL technical scores
* Technical score range validation

The technical score is expected to remain within:

```text
0 – 100
```

---

# 🛠️ Technology Stack

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Core programming language |
| Pandas     | Data processing           |
| NumPy      | Numerical calculations    |
| yfinance   | Market data collection    |
| SQLAlchemy | Database interaction      |
| SQLite     | Local database            |
| Streamlit  | Dashboard                 |
| Plotly     | Interactive charts        |

---

# 📌 Future Improvements

Planned improvements include:

* [ ] Automated daily execution
* [ ] Windows Task Scheduler integration
* [ ] Telegram morning market summary
* [ ] Email notifications
* [ ] More stocks and indices
* [ ] Sector-level analysis
* [ ] Backtesting engine
* [ ] Strategy performance evaluation
* [ ] Historical signal tracking
* [ ] Alert system
* [ ] More robust market-data provider
* [ ] Optional local LLM-generated market summaries
* [ ] Portfolio tracking
* [ ] Automated report generation

---

# 🎯 Project Objective

The main objective of this project is to build an end-to-end **data engineering + analytics + automation workflow** using Python.

It demonstrates:

```text
Data Collection
       ↓
Data Cleaning
       ↓
Feature Engineering
       ↓
Technical Analysis
       ↓
Rule-Based Scoring
       ↓
Database Storage
       ↓
Data Visualization
       ↓
Automation
```

The project can also serve as a practical learning project for:

* Python development
* Data analysis
* SQL
* Automation
* API/data collection
* Database management
* Dashboard development
* Software testing

---

# ⚠️ Disclaimer

This project is created for **educational, research, and software-development purposes**.

The technical indicators, scores, signals, and classifications generated by this project are based on predefined rules and historical market data.

They should **not be treated as financial advice or guaranteed predictions of future market performance**.

Always perform independent research and consult a qualified financial professional before making investment decisions.

---

# 👨‍💻 Author

**Jay Surya**

B.Sc. Information Technology

GitHub:
https://github.com/surya-hash-coder

---

⭐ If you find this project useful, consider giving the repository a star.
