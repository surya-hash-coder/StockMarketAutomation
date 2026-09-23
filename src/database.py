import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATABASE_DIR / "stock_market.db"

CLEAN_DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "clean_market_data.csv"
)

ANALYSIS_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "market_analysis.csv"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

engine = create_engine(
    f"sqlite:///{DB_FILE}"
)


# ==========================================
# LOAD MARKET DATA
# ==========================================

def load_market_data():

    print("Loading clean market data...")

    df = pd.read_csv(
        CLEAN_DATA_FILE
    )

    print(
        f"Market records: {len(df)}"
    )

    return df


# ==========================================
# LOAD ANALYSIS DATA
# ==========================================

def load_analysis_data():

    print("Loading market analysis...")

    df = pd.read_csv(
        ANALYSIS_FILE
    )

    print(
        f"Analysis records: {len(df)}"
    )

    return df


# ==========================================
# SAVE MARKET DATA
# ==========================================

def save_market_data(df):

    print()
    print("Saving market data to SQLite...")

    df.to_sql(
        "market_data",
        engine,
        if_exists="replace",
        index=False
    )

    print("[OK] market_data table created")


# ==========================================
# SAVE ANALYSIS DATA
# ==========================================

def save_analysis_data(df):

    print()
    print("Saving analysis data to SQLite...")

    df.to_sql(
        "market_analysis",
        engine,
        if_exists="replace",
        index=False
    )

    print("[OK] market_analysis table created")


# ==========================================
# DATABASE VALIDATION
# ==========================================

def validate_database():

    print()
    print("================================")
    print("DATABASE VALIDATION")
    print("================================")

    with engine.connect() as connection:

        # ----------------------------------
        # RECORD COUNTS
        # ----------------------------------

        market_count = connection.execute(
            text(
                "SELECT COUNT(*) FROM market_data"
            )
        ).scalar()

        analysis_count = connection.execute(
            text(
                "SELECT COUNT(*) FROM market_analysis"
            )
        ).scalar()

        symbol_count = connection.execute(
            text(
                """
                SELECT COUNT(DISTINCT symbol)
                FROM market_data
                """
            )
        ).scalar()

        # ----------------------------------
        # ANALYSIS COLUMNS
        # ----------------------------------

        columns = connection.execute(
            text(
                "PRAGMA table_info(market_analysis)"
            )
        ).fetchall()

        analysis_columns = [
            row[1]
            for row in columns
        ]

    print(
        f"Market records in DB: {market_count}"
    )

    print(
        f"Analysis records in DB: {analysis_count}"
    )

    print(
        f"Symbols in DB: {symbol_count}"
    )

    print()
    print("V4 analysis columns:")

    required_v4_columns = [
        "trend_score",
        "momentum_score",
        "volume_score",
        "quality_score",
        "risk_score",
        "technical_score",
        "market_regime",
        "momentum_state",
        "volatility_state",
        "signal",
        "analysis_explanation"
    ]

    all_columns_present = True

    for column in required_v4_columns:

        if column in analysis_columns:

            print(
                f"[OK] {column}"
            )

        else:

            print(
                f"[ERROR] {column} MISSING"
            )

            all_columns_present = False

    print()

    if all_columns_present:

        print(
            "[OK] V4 schema validation PASSED"
        )

    else:

        print(
            "[ERROR] V4 schema validation FAILED"
        )


# ==========================================
# SHOW LATEST SIGNALS
# ==========================================

def show_latest_signals():

    print()
    print("================================")
    print("LATEST MARKET ANALYSIS")
    print("================================")
    print()

    query = """
        SELECT
            symbol,
            date,
            close,
            rsi,
            trend_score,
            momentum_score,
            volume_score,
            quality_score,
            risk_score,
            technical_score,
            market_regime,
            momentum_state,
            volatility_state,
            signal,
            analysis_explanation

        FROM market_analysis

        WHERE date IN (
            SELECT MAX(date)
            FROM market_analysis AS latest
            WHERE latest.symbol = market_analysis.symbol
        )

        ORDER BY symbol
    """

    df = pd.read_sql(
        query,
        engine
    )

    print(
        df[
            [
                "symbol",
                "close",
                "rsi",
                "trend_score",
                "momentum_score",
                "volume_score",
                "quality_score",
                "risk_score",
                "technical_score",
                "market_regime",
                "momentum_state",
                "volatility_state",
                "signal"
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print("Explanations:")
    print()

    for _, row in df.iterrows():

        print(
            f"{row['symbol']}: "
            f"{row['analysis_explanation']}"
        )


# ==========================================
# DATABASE HEALTH CHECK
# ==========================================

def database_health_check():

    print()
    print("================================")
    print("DATABASE HEALTH CHECK")
    print("================================")

    with engine.connect() as connection:

        null_scores = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM market_analysis
                WHERE technical_score IS NULL
                """
            )
        ).scalar()

        invalid_scores = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM market_analysis
                WHERE technical_score < 0
                   OR technical_score > 100
                """
            )
        ).scalar()

    print(
        f"Rows with NULL technical score: {null_scores}"
    )

    print(
        f"Rows with invalid technical score: {invalid_scores}"
    )

    if null_scores == 0:

        print(
            "[OK] NULL technical score validation PASSED"
        )

    else:

        print(
            "[ERROR] NULL technical score validation FAILED"
        )

    if invalid_scores == 0:

        print(
            "[OK] Technical score range validation PASSED"
        )

    else:

        print(
            "[ERROR] Technical score range validation FAILED"
        )


# ==========================================
# MAIN
# ==========================================

def main():

    print()
    print("================================")
    print("STOCK MARKET DATABASE V4")
    print("================================")
    print()

    # --------------------------------------
    # LOAD
    # --------------------------------------

    market_data = load_market_data()

    analysis_data = load_analysis_data()

    # --------------------------------------
    # SAVE
    # --------------------------------------

    save_market_data(
        market_data
    )

    save_analysis_data(
        analysis_data
    )

    # --------------------------------------
    # VALIDATION
    # --------------------------------------

    validate_database()

    database_health_check()

    # --------------------------------------
    # SHOW RESULTS
    # --------------------------------------

    show_latest_signals()

    # --------------------------------------
    # COMPLETE
    # --------------------------------------

    print()
    print("================================")
    print("DATABASE V4 SETUP COMPLETE")
    print("================================")

    print(
        f"Database: {DB_FILE}"
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    main()
