import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_market_data():

    files = sorted(RAW_DIR.glob("market_data_*.csv"))

    if not files:
        print("❌ No market data CSV found.")
        return

    latest_file = files[-1]

    print(f"Reading: {latest_file.name}")

    df = pd.read_csv(latest_file)

    print(f"Raw records: {len(df)}")

    # -----------------------------
    # Clean column names
    # -----------------------------

    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    # -----------------------------
    # Convert date
    # -----------------------------

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # -----------------------------
    # Remove duplicate records
    # -----------------------------

    duplicate_columns = []

    if "symbol" in df.columns:
        duplicate_columns.append("symbol")

    if "date" in df.columns:
        duplicate_columns.append("date")

    if duplicate_columns:
        df = df.drop_duplicates(
            subset=duplicate_columns
        )

    # -----------------------------
    # Convert numeric columns
    # -----------------------------

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume"
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # -----------------------------
    # Remove invalid rows
    # -----------------------------

    if "close" in df.columns:
        df = df[df["close"].notna()]

    if "symbol" in df.columns:
        df = df[df["symbol"].notna()]

    # -----------------------------
    # Sort
    # -----------------------------

    sort_columns = []

    if "symbol" in df.columns:
        sort_columns.append("symbol")

    if "date" in df.columns:
        sort_columns.append("date")

    if sort_columns:
        df = df.sort_values(sort_columns)

    # -----------------------------
    # Calculate daily return
    # -----------------------------

    if "close" in df.columns:

        df["daily_return"] = (
            df.groupby("symbol")["close"]
            .pct_change() * 100
        )

    # -----------------------------
    # Save cleaned data
    # -----------------------------

    output_file = (
        PROCESSED_DIR /
        "clean_market_data.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()
    print("================================")
    print("DATA CLEANING COMPLETE")
    print("================================")
    print(f"Clean records: {len(df)}")
    print(f"Saved: {output_file}")
    print()
    print("Columns:")
    print(list(df.columns))


if __name__ == "__main__":
    clean_market_data()