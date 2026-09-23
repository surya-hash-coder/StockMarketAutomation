import pandas as pd
import numpy as np
from pathlib import Path


# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "clean_market_data.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "market_analysis.csv"


# ==========================================================
# CONFIGURATION
# ==========================================================

INDEX_SYMBOLS = {
    "NIFTY50",
    "BANKNIFTY",
    "SENSEX"
}


# ==========================================================
# RSI - WILDER METHOD
# ==========================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ==========================================================
# MACD
# ==========================================================

def calculate_macd(series):

    ema12 = series.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = series.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd - signal

    return macd, signal, histogram


# ==========================================================
# ATR
# ==========================================================

def calculate_atr(group, period=14):

    high = group["high"]
    low = group["low"]
    close = group["close"]

    previous_close = close.shift(1)

    tr1 = high - low

    tr2 = (
        high - previous_close
    ).abs()

    tr3 = (
        low - previous_close
    ).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = true_range.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    return atr


# ==========================================================
# BOLLINGER BANDS
# ==========================================================

def calculate_bollinger(series, period=20):

    middle = series.rolling(
        period
    ).mean()

    std = series.rolling(
        period
    ).std()

    upper = middle + (
        2 * std
    )

    lower = middle - (
        2 * std
    )

    return middle, upper, lower


# ==========================================================
# TECHNICAL INDICATORS
# ==========================================================

def calculate_indicators(df):

    df = df.copy()

    # ------------------------------------------------------
    # DATE
    # ------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # MOVING AVERAGES
    # ------------------------------------------------------

    df["sma_20"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.rolling(20).mean()
        )
    )

    df["sma_50"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.rolling(50).mean()
        )
    )

    df["sma_200"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.rolling(200).mean()
        )
    )

    # ------------------------------------------------------
    # EMA
    # ------------------------------------------------------

    df["ema_20"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.ewm(
                span=20,
                adjust=False
            ).mean()
        )
    )

    df["ema_50"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.ewm(
                span=50,
                adjust=False
            ).mean()
        )
    )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    df["rsi"] = (
        df.groupby("symbol")["close"]
        .transform(calculate_rsi)
    )

    # ------------------------------------------------------
    # MACD
    # ------------------------------------------------------

    macd_results = []

    for symbol, group in df.groupby("symbol"):

        group = group.copy()

        macd, signal, histogram = calculate_macd(
            group["close"]
        )

        group["macd"] = macd
        group["macd_signal"] = signal
        group["macd_histogram"] = histogram

        macd_results.append(group)

    df = pd.concat(
        macd_results,
        ignore_index=True
    )

    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # ATR
    # ------------------------------------------------------

    atr_results = []

    for symbol, group in df.groupby("symbol"):

        group = group.copy()

        group["atr_14"] = calculate_atr(
            group
        )

        atr_results.append(group)

    df = pd.concat(
        atr_results,
        ignore_index=True
    )

    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # BOLLINGER BANDS
    # ------------------------------------------------------

    bollinger_results = []

    for symbol, group in df.groupby("symbol"):

        group = group.copy()

        middle, upper, lower = calculate_bollinger(
            group["close"]
        )

        group["bb_middle"] = middle
        group["bb_upper"] = upper
        group["bb_lower"] = lower

        bollinger_results.append(group)

    df = pd.concat(
        bollinger_results,
        ignore_index=True
    )

    df = df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------

    if "volume" in df.columns:

        df["volume_sma_20"] = (
            df.groupby("symbol")["volume"]
            .transform(
                lambda x: x.rolling(20).mean()
            )
        )

        df["volume_ratio"] = np.where(
            df["volume_sma_20"] > 0,
            df["volume"]
            / df["volume_sma_20"],
            np.nan
        )

        # Index volume is unavailable from the current source.
        index_mask = df["symbol"].isin(
            INDEX_SYMBOLS
        )

        df.loc[
            index_mask,
            "volume_ratio"
        ] = np.nan

    # ------------------------------------------------------
    # VOLATILITY
    # ------------------------------------------------------

    if "daily_return" in df.columns:

        # daily_return is already percentage-based.
        # DO NOT multiply the rolling standard deviation by 100.
        df["volatility_20"] = (
            df.groupby("symbol")["daily_return"]
            .transform(
                lambda x: x.rolling(20).std()
            )
        )

    # ------------------------------------------------------
    # RATE OF CHANGE
    # ------------------------------------------------------

    df["roc_20"] = (
        df.groupby("symbol")["close"]
        .transform(
            lambda x: x.pct_change(20) * 100
        )
    )

    # ------------------------------------------------------
    # ATR %
    # ------------------------------------------------------

    df["atr_percent"] = (
        df["atr_14"]
        / df["close"]
        * 100
    )

    return df


# ==========================================================
# TREND SCORE
# MAXIMUM = 30
# ==========================================================

def calculate_trend_score(row):

    score = 0

    # Price above SMA20
    if (
        pd.notna(row["close"])
        and pd.notna(row["sma_20"])
        and row["close"] > row["sma_20"]
    ):
        score += 7

    # Price above SMA50
    if (
        pd.notna(row["close"])
        and pd.notna(row["sma_50"])
        and row["close"] > row["sma_50"]
    ):
        score += 7

    # Price above SMA200
    if (
        pd.notna(row["close"])
        and pd.notna(row["sma_200"])
        and row["close"] > row["sma_200"]
    ):
        score += 8

    # EMA20 above EMA50
    if (
        pd.notna(row["ema_20"])
        and pd.notna(row["ema_50"])
        and row["ema_20"] > row["ema_50"]
    ):
        score += 8

    return score


# ==========================================================
# MOMENTUM SCORE
# MAXIMUM = 30
# ==========================================================

def calculate_momentum_score(row):

    score = 0

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if pd.notna(row["rsi"]):

        rsi = row["rsi"]

        if 55 <= rsi <= 70:
            score += 12

        elif 50 <= rsi < 55:
            score += 8

        elif 40 <= rsi < 50:
            score += 4

    # ------------------------------------------------------
    # MACD
    # ------------------------------------------------------

    if (
        pd.notna(row["macd"])
        and pd.notna(row["macd_signal"])
    ):

        if row["macd"] > row["macd_signal"]:

            score += 10

    # ------------------------------------------------------
    # ROC
    # ------------------------------------------------------

    if pd.notna(row["roc_20"]):

        if row["roc_20"] > 5:

            score += 8

        elif row["roc_20"] > 0:

            score += 4

    return min(score, 30)


# ==========================================================
# VOLUME SCORE
# MAXIMUM = 15
# ==========================================================

def calculate_volume_score(row):

    # Index volume unavailable
    if row["symbol"] in INDEX_SYMBOLS:

        return np.nan

    if pd.isna(row["volume_ratio"]):

        return np.nan

    ratio = row["volume_ratio"]

    if ratio >= 1.5:

        return 15

    elif ratio >= 1.2:

        return 10

    elif ratio >= 1.0:

        return 5

    return 0


# ==========================================================
# QUALITY / CONFIRMATION SCORE
# MAXIMUM = 15
# ==========================================================

def calculate_quality_score(row):

    score = 0

    # ------------------------------------------------------
    # Price above EMA20
    # ------------------------------------------------------

    if (
        pd.notna(row["close"])
        and pd.notna(row["ema_20"])
        and row["close"] > row["ema_20"]
    ):
        score += 4

    # ------------------------------------------------------
    # MACD histogram positive
    # ------------------------------------------------------

    if pd.notna(row["macd_histogram"]):

        if row["macd_histogram"] > 0:
            score += 4

    # ------------------------------------------------------
    # Price relative to Bollinger middle band
    # ------------------------------------------------------

    if (
        pd.notna(row["close"])
        and pd.notna(row["bb_middle"])
        and row["close"] > row["bb_middle"]
    ):
        score += 3

    # ------------------------------------------------------
    # ROC positive
    # ------------------------------------------------------

    if pd.notna(row["roc_20"]):

        if row["roc_20"] > 0:
            score += 2

    # ------------------------------------------------------
    # RSI confirmation
    # ------------------------------------------------------

    if pd.notna(row["rsi"]):

        if 50 <= row["rsi"] <= 70:
            score += 2

    return min(score, 15)


# ==========================================================
# VOLATILITY / RISK SCORE
# MAXIMUM = 10
#
# Higher score = more controlled volatility
# ==========================================================

def calculate_risk_score(row):

    if pd.isna(row["volatility_20"]):

        return np.nan

    volatility = row["volatility_20"]

    if volatility < 1.5:

        return 10

    elif volatility < 2.5:

        return 8

    elif volatility < 4:

        return 5

    elif volatility < 6:

        return 2

    return 0


# ==========================================================
# MARKET REGIME
# ==========================================================

def determine_market_regime(row):

    required = [
        "close",
        "sma_20",
        "sma_50",
        "sma_200"
    ]

    if any(
        pd.isna(row[column])
        for column in required
    ):

        return "Insufficient Data"

    close = row["close"]
    sma20 = row["sma_20"]
    sma50 = row["sma_50"]
    sma200 = row["sma_200"]

    if (
        close > sma20
        and sma20 > sma50
        and sma50 > sma200
    ):

        return "Bullish Trend"

    elif (
        close < sma20
        and sma20 < sma50
        and sma50 < sma200
    ):

        return "Bearish Trend"

    return "Sideways / Mixed"


# ==========================================================
# MOMENTUM STATE
# ==========================================================

def determine_momentum_state(row):

    rsi = row["rsi"]
    macd = row["macd"]
    signal = row["macd_signal"]

    if (
        pd.isna(rsi)
        or pd.isna(macd)
        or pd.isna(signal)
    ):

        return "Insufficient Data"

    if (
        rsi >= 55
        and macd > signal
    ):

        return "Strong Positive"

    elif (
        rsi >= 50
        and macd > signal
    ):

        return "Positive"

    elif (
        rsi < 40
        and macd < signal
    ):

        return "Weak"

    return "Neutral"


# ==========================================================
# VOLATILITY STATE
# ==========================================================

def determine_volatility_state(row):

    volatility = row["volatility_20"]

    if pd.isna(volatility):

        return "Insufficient Data"

    if volatility < 1.5:

        return "Low"

    elif volatility < 3:

        return "Normal"

    elif volatility < 5:

        return "High"

    return "Very High"


# ==========================================================
# NORMALIZED TECHNICAL SCORE
#
# TREND       = 30
# MOMENTUM    = 30
# VOLUME      = 15
# QUALITY     = 15
# RISK        = 10
#
# TOTAL       = 100
# ==========================================================

def calculate_technical_score(row):

    components = []

    # Trend
    if pd.notna(row["trend_score"]):

        components.append(
            (
                row["trend_score"],
                30
            )
        )

    # Momentum
    if pd.notna(row["momentum_score"]):

        components.append(
            (
                row["momentum_score"],
                30
            )
        )

    # Volume
    if pd.notna(row["volume_score"]):

        components.append(
            (
                row["volume_score"],
                15
            )
        )

    # Quality
    if pd.notna(row["quality_score"]):

        components.append(
            (
                row["quality_score"],
                15
            )
        )

    # Risk
    if pd.notna(row["risk_score"]):

        components.append(
            (
                row["risk_score"],
                10
            )
        )

    if not components:

        return np.nan

    earned = sum(
        item[0]
        for item in components
    )

    possible = sum(
        item[1]
        for item in components
    )

    return round(
        (earned / possible) * 100,
        2
    )


# ==========================================================
# SCORE INTERPRETATION
# ==========================================================

def generate_signal(score, row):

    required = [
        "sma_50",
        "sma_200",
        "rsi",
        "macd",
        "macd_signal"
    ]

    if any(
        pd.isna(row[column])
        for column in required
    ):

        return "Insufficient Data"

    if pd.isna(score):

        return "Insufficient Data"

    if score >= 75:

        return "Strong Setup"

    elif score >= 60:

        return "Positive"

    elif score >= 40:

        return "Neutral"

    return "Weak"


# ==========================================================
# EXPLANATION ENGINE
# ==========================================================

def generate_explanation(row):

    reasons = []
    warnings = []

    # ------------------------------------------------------
    # TREND
    # ------------------------------------------------------

    if row["trend_score"] >= 24:

        reasons.append(
            "Strong trend alignment"
        )

    elif row["trend_score"] >= 15:

        reasons.append(
            "Moderate trend alignment"
        )

    else:

        warnings.append(
            "Trend alignment is weak"
        )

    # ------------------------------------------------------
    # MOMENTUM
    # ------------------------------------------------------

    if row["momentum_score"] >= 22:

        reasons.append(
            "Momentum indicators are positive"
        )

    elif row["momentum_score"] >= 12:

        reasons.append(
            "Momentum is moderately positive"
        )

    else:

        warnings.append(
            "Momentum confirmation is limited"
        )

    # ------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------

    if row["symbol"] in INDEX_SYMBOLS:

        warnings.append(
            "Volume confirmation unavailable for index"
        )

    elif pd.notna(row["volume_score"]):

        if row["volume_score"] >= 10:

            reasons.append(
                "Volume supports the current move"
            )

        elif row["volume_score"] == 0:

            warnings.append(
                "Volume is below confirmation threshold"
            )

    # ------------------------------------------------------
    # QUALITY
    # ------------------------------------------------------

    if row["quality_score"] >= 11:

        reasons.append(
            "Multiple indicators confirm the setup"
        )

    elif row["quality_score"] < 5:

        warnings.append(
            "Technical confirmation is limited"
        )

    # ------------------------------------------------------
    # VOLATILITY
    # ------------------------------------------------------

    if pd.notna(row["risk_score"]):

        if row["risk_score"] >= 8:

            reasons.append(
                "Volatility is relatively controlled"
            )

        elif row["risk_score"] <= 2:

            warnings.append(
                "Volatility is elevated"
            )

    # ------------------------------------------------------
    # COMBINE
    # ------------------------------------------------------

    result = []

    if reasons:

        result.append(
            "Positive factors: "
            + "; ".join(reasons)
        )

    if warnings:

        result.append(
            "Watch: "
            + "; ".join(warnings)
        )

    return " | ".join(result)


# ==========================================================
# GENERATE ALL ANALYTICS
# ==========================================================

def generate_scores(df):

    df = df.copy()

    # ------------------------------------------------------
    # COMPONENT SCORES
    # ------------------------------------------------------

    df["trend_score"] = df.apply(
        calculate_trend_score,
        axis=1
    )

    df["momentum_score"] = df.apply(
        calculate_momentum_score,
        axis=1
    )

    df["volume_score"] = df.apply(
        calculate_volume_score,
        axis=1
    )

    df["quality_score"] = df.apply(
        calculate_quality_score,
        axis=1
    )

    df["risk_score"] = df.apply(
        calculate_risk_score,
        axis=1
    )

    # ------------------------------------------------------
    # NORMALIZED SCORE
    # ------------------------------------------------------

    df["technical_score"] = df.apply(
        calculate_technical_score,
        axis=1
    )

    # ------------------------------------------------------
    # MARKET REGIME
    # ------------------------------------------------------

    df["market_regime"] = df.apply(
        determine_market_regime,
        axis=1
    )

    # ------------------------------------------------------
    # MOMENTUM STATE
    # ------------------------------------------------------

    df["momentum_state"] = df.apply(
        determine_momentum_state,
        axis=1
    )

    # ------------------------------------------------------
    # VOLATILITY STATE
    # ------------------------------------------------------

    df["volatility_state"] = df.apply(
        determine_volatility_state,
        axis=1
    )

    return df


# ==========================================================
# SIGNALS + EXPLANATIONS
# ==========================================================

def generate_signals(df):

    df = df.copy()

    df["signal"] = df.apply(
        lambda row: generate_signal(
            row["technical_score"],
            row
        ),
        axis=1
    )

    df["analysis_explanation"] = df.apply(
        generate_explanation,
        axis=1
    )

    return df


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print("======================================")
    print("STOCK MARKET ANALYTICS ENGINE")
    print("======================================")

    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    print()
    print("Loading cleaned market data...")

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Loaded {len(df)} records"
    )

    # ------------------------------------------------------
    # INDICATORS
    # ------------------------------------------------------

    print()
    print("Calculating technical indicators...")

    df = calculate_indicators(
        df
    )

    # ------------------------------------------------------
    # SCORES
    # ------------------------------------------------------

    print(
        "Calculating technical scores..."
    )

    df = generate_scores(
        df
    )

    # ------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------

    print(
        "Generating signals..."
    )

    df = generate_signals(
        df
    )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ------------------------------------------------------
    # LATEST DATA
    # ------------------------------------------------------

    latest = (
        df.sort_values("date")
        .groupby("symbol")
        .tail(1)
        .sort_values("symbol")
    )

    # ------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------

    print()
    print("======================================")
    print("ANALYTICS ENGINE V4 COMPLETE")
    print("======================================")

    print(
        f"Records: {len(df)}"
    )

    print(
        f"Symbols: {df['symbol'].nunique()}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print()
    print("Latest Market Analysis:")
    print()

    display_columns = [
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

    print(
        latest[
            display_columns
        ].to_string(
            index=False
        )
    )

    print()
    print("Analysis Explanations:")
    print()

    for _, row in latest.iterrows():

        print(
            f"{row['symbol']}: "
            f"{row['analysis_explanation']}"
        )


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    main()
