import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# SYMBOLS
# ==========================================

SYMBOLS = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "RELIANCE": "RELIANCE.NS",
    "ICICIBANK": "ICICIBANK.NS",
}


# ==========================================
# COLLECT MARKET DATA
# ==========================================

def collect_market_data():

    print("Starting market data collection...")
    print()

    results = []

    for name, ticker in SYMBOLS.items():

        print(f"Fetching {name} ({ticker})...")

        try:

            data = yf.download(
                ticker,
                period="2y",
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                print(f"⚠ No data received for {name}")
                continue

            # ----------------------------------
            # Handle yfinance MultiIndex columns
            # ----------------------------------

            if isinstance(data.columns, pd.MultiIndex):

                data.columns = data.columns.get_level_values(0)

            # ----------------------------------
            # Reset index
            # ----------------------------------

            data = data.reset_index()

            # ----------------------------------
            # Add symbol
            # ----------------------------------

            data["Symbol"] = name

            # ----------------------------------
            # Keep only required columns
            # ----------------------------------

            required_columns = [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Adj Close",
                "Volume",
                "Symbol"
            ]

            data = data[
                [column for column in required_columns if column in data.columns]
            ]

            results.append(data)

            print(f"[OK] {name} collected: {len(data)} records")
        except Exception as e:

            print(f"[ERROR] Error collecting {name}: {e}")

        print()

    # ==========================================
    # COMBINE ALL SYMBOLS
    # ==========================================

    if not results:

        print("❌ No market data collected.")
        return

    final_data = pd.concat(
        results,
        ignore_index=True
    )

    # ==========================================
    # SORT DATA
    # ==========================================

    final_data = final_data.sort_values(
        ["Symbol", "Date"]
    ).reset_index(drop=True)

    # ==========================================
    # SAVE RAW DATA
    # ==========================================

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = RAW_DIR / f"market_data_{timestamp}.csv"

    final_data.to_csv(
        output_file,
        index=False
    )

    # ==========================================
    # SUMMARY
    # ==========================================

    print("================================")
    print("MARKET DATA COLLECTION COMPLETE")
    print("================================")

    print(f"Total records: {len(final_data)}")
    print(f"Symbols: {final_data['Symbol'].nunique()}")

    print()
    print("Records by symbol:")

    print(
        final_data["Symbol"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print(f"Saved: {output_file}")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    collect_market_data()