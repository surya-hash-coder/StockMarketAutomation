import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
from pathlib import Path


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Stock Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# DATABASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "database" / "stock_market.db"

DB_PATH = f"sqlite:///{DB_FILE}"

engine = create_engine(DB_PATH)


# ==========================================================
# CUSTOM THEME
# ==========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1120;
    }

    section[data-testid="stSidebar"] {
        background-color: #080d18;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# LOAD DATA FROM SQLITE
# ==========================================================

@st.cache_data(ttl=300)
def load_analysis():

    query = """
        SELECT *
        FROM market_analysis
        ORDER BY date DESC
    """

    return pd.read_sql(
        query,
        engine
    )


df = load_analysis()


# ==========================================================
# VALIDATION
# ==========================================================

if df.empty:

    st.error(
        "❌ No market analysis data found in SQLite database."
    )

    st.stop()


df["date"] = pd.to_datetime(
    df["date"]
)


latest_date = df["date"].max()


latest = (
    df[
        df["date"] == latest_date
    ]
    .copy()
    .sort_values(
        "technical_score",
        ascending=False
    )
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📊 Market Terminal")

    st.caption(
        "Automated Market Intelligence"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📈 Market Overview",
            "🔎 Stock Scanner",
            "📊 Technical Analysis"
        ]
    )

    st.divider()

    if st.button(
        "🔄 Refresh Data",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    st.caption("Latest Data")

    st.write(
        latest_date.strftime("%Y-%m-%d")
    )

    st.caption("Data Source")

    st.write(
        "SQLite Database"
    )

    st.caption("Analytics")

    st.write(
        "Technical Engine V4"
    )


# ==========================================================
# HEADER
# ==========================================================

st.title(
    "📊 Stock Market Intelligence"
)

st.caption(
    "Automated technical analysis • "
    "Rule-based decision support"
)

st.divider()


# ==========================================================
# COMMON DATA
# ==========================================================

indices = [
    "NIFTY50",
    "BANKNIFTY",
    "SENSEX"
]

index_data = latest[
    latest["symbol"].isin(indices)
].copy()

stocks = latest[
    ~latest["symbol"].isin(indices)
].copy()


# ==========================================================
# HELPER — SIGNAL DISPLAY
# ==========================================================

def display_signal(signal):

    if signal == "Strong Setup":

        st.success(
            f"🚀 {signal}"
        )

    elif signal == "Positive":

        st.success(
            f"🟢 {signal}"
        )

    elif signal == "Neutral":

        st.warning(
            f"🟡 {signal}"
        )

    else:

        st.error(
            f"🔴 {signal}"
        )


# ==========================================================
# PAGE 1 — MARKET OVERVIEW
# ==========================================================

if page == "📈 Market Overview":

    st.header(
        "Market Overview"
    )

    st.caption(
        f"Market snapshot for "
        f"{latest_date.strftime('%d %b %Y')}"
    )

    # ------------------------------------------------------
    # INDEX METRICS
    # ------------------------------------------------------

    cols = st.columns(3)

    for col, symbol in zip(
        cols,
        indices
    ):

        row = index_data[
            index_data["symbol"] == symbol
        ]

        with col:

            if row.empty:

                st.metric(
                    symbol,
                    "N/A"
                )

                continue

            data = row.iloc[0]

            price = data["close"]
            score = data["technical_score"]
            signal = data["signal"]

            st.metric(
                label=symbol,
                value=f"{price:,.2f}",
                delta=f"Score {score:.0f}/100"
            )

            display_signal(
                signal
            )

            st.caption(
                f"Regime: {data['market_regime']}"
            )

            st.caption(
                f"Momentum: {data['momentum_state']}"
            )

    st.divider()

    # ------------------------------------------------------
    # MARKET SCORE
    # ------------------------------------------------------

    st.subheader(
        "🎯 Market Technical Score"
    )

    score_data = index_data[
        [
            "symbol",
            "technical_score"
        ]
    ].copy()

    fig = px.bar(
        score_data,
        x="symbol",
        y="technical_score",
        text="technical_score"
    )

    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120",
        font_color="#cbd5e1",
        yaxis=dict(
            range=[0, 100],
            title="Score"
        ),
        xaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ------------------------------------------------------
    # MARKET REGIME
    # ------------------------------------------------------

    st.subheader(
        "🌐 Market Regime"
    )

    regime_counts = (
        index_data["market_regime"]
        .value_counts()
        .reset_index()
    )

    regime_counts.columns = [
        "regime",
        "count"
    ]

    fig_regime = px.bar(
        regime_counts,
        x="regime",
        y="count",
        text="count"
    )

    fig_regime.update_layout(
        template="plotly_dark",
        height=350,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120"
    )

    st.plotly_chart(
        fig_regime,
        use_container_width=True
    )

    # ------------------------------------------------------
    # SIGNAL DISTRIBUTION
    # ------------------------------------------------------

    st.subheader(
        "🚦 Current Signal Distribution"
    )

    signal_counts = (
        latest["signal"]
        .value_counts()
        .reset_index()
    )

    signal_counts.columns = [
        "signal",
        "count"
    ]

    fig2 = px.pie(
        signal_counts,
        names="signal",
        values="count",
        hole=0.55
    )

    fig2.update_layout(
        template="plotly_dark",
        height=450,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ------------------------------------------------------
    # TOP SCORES
    # ------------------------------------------------------

    st.subheader(
        "🏆 Highest Technical Scores"
    )

    top_stocks = stocks.head(5)

    if len(top_stocks) > 0:

        cols = st.columns(
            min(5, len(top_stocks))
        )

        for col, (_, stock) in zip(
            cols,
            top_stocks.iterrows()
        ):

            with col:

                st.metric(
                    stock["symbol"],
                    f'{stock["technical_score"]:.0f}/100'
                )

                st.caption(
                    stock["signal"]
                )

                st.caption(
                    stock["market_regime"]
                )


# ==========================================================
# PAGE 2 — STOCK SCANNER
# ==========================================================

elif page == "🔎 Stock Scanner":

    st.header(
        "🔎 Stock Scanner"
    )

    st.caption(
        "Stocks ranked using the V4 rule-based "
        "technical scoring system."
    )

    st.divider()

    # ------------------------------------------------------
    # FILTER
    # ------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        signal_filter = st.selectbox(
            "Signal",
            [
                "All",
                "Strong Setup",
                "Positive",
                "Neutral",
                "Weak"
            ]
        )

    with col2:

        min_score = st.slider(
            "Minimum Technical Score",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )

    scanner = stocks.copy()

    if signal_filter != "All":

        scanner = scanner[
            scanner["signal"] == signal_filter
        ]

    scanner = scanner[
        scanner["technical_score"] >= min_score
    ]

    scanner = scanner.sort_values(
        "technical_score",
        ascending=False
    )

    st.write(
        f"**{len(scanner)} stocks found**"
    )

    st.divider()

    # ------------------------------------------------------
    # STOCK CARDS
    # ------------------------------------------------------

    for _, stock in scanner.iterrows():

        with st.container(
            border=True
        ):

            top1, top2, top3 = st.columns(
                [2, 2, 1]
            )

            with top1:

                st.subheader(
                    stock["symbol"]
                )

                st.write(
                    f'₹{stock["close"]:,.2f}'
                )

                st.caption(
                    f'Regime: {stock["market_regime"]}'
                )

            with top2:

                display_signal(
                    stock["signal"]
                )

                st.caption(
                    f'Momentum: {stock["momentum_state"]}'
                )

                st.caption(
                    f'Volatility: {stock["volatility_state"]}'
                )

            with top3:

                st.metric(
                    "Technical Score",
                    f'{stock["technical_score"]:.0f}/100'
                )

            st.divider()

            # ----------------------------------------------
            # V4 SCORE BREAKDOWN
            # ----------------------------------------------

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:

                st.metric(
                    "Trend",
                    f'{stock["trend_score"]:.0f}/30'
                )

            with c2:

                st.metric(
                    "Momentum",
                    f'{stock["momentum_score"]:.0f}/30'
                )

            with c3:

                volume = stock["volume_score"]

                if pd.isna(volume):

                    st.metric(
                        "Volume",
                        "N/A"
                    )

                else:

                    st.metric(
                        "Volume",
                        f'{volume:.0f}/15'
                    )

            with c4:

                st.metric(
                    "Quality",
                    f'{stock["quality_score"]:.0f}/15'
                )

            with c5:

                st.metric(
                    "Risk",
                    f'{stock["risk_score"]:.0f}/10'
                )

            st.divider()

            # ----------------------------------------------
            # INDICATORS
            # ----------------------------------------------

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "RSI",
                    f'{stock["rsi"]:.1f}'
                )

            with c2:

                st.metric(
                    "ROC 20",
                    f'{stock["roc_20"]:.2f}%'
                )

            with c3:

                st.metric(
                    "ATR %",
                    f'{stock["atr_percent"]:.2f}%'
                )

            with c4:

                st.metric(
                    "20D Volatility",
                    f'{stock["volatility_20"]:.2f}%'
                )

            # ----------------------------------------------
            # EXPLANATION
            # ----------------------------------------------

            st.info(
                f"💡 {stock['analysis_explanation']}"
            )


# ==========================================================
# PAGE 3 — TECHNICAL ANALYSIS
# ==========================================================

else:

    st.header(
        "📊 Technical Analysis"
    )

    st.caption(
        "Detailed price, trend, momentum and volatility analysis."
    )

    # ------------------------------------------------------
    # STOCK SELECTOR
    # ------------------------------------------------------

    stock_names = stocks[
        "symbol"
    ].tolist()

    if not stock_names:

        st.warning(
            "No individual stocks available."
        )

        st.stop()

    selected_stock = st.selectbox(
        "Select Stock",
        stock_names
    )

    # ------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------

    history = df[
        df["symbol"] == selected_stock
    ].copy()

    history = history.sort_values(
        "date"
    )

    current = history.iloc[-1]

    # ------------------------------------------------------
    # CURRENT SNAPSHOT
    # ------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Price",
            f'₹{current["close"]:,.2f}'
        )

    with c2:

        st.metric(
            "RSI",
            f'{current["rsi"]:.1f}'
        )

    with c3:

        st.metric(
            "Technical Score",
            f'{current["technical_score"]:.0f}/100'
        )

    with c4:

        st.metric(
            "Signal",
            current["signal"]
        )

    st.caption(
        f"Market Regime: {current['market_regime']} • "
        f"Momentum: {current['momentum_state']} • "
        f"Volatility: {current['volatility_state']}"
    )

    st.info(
        f"💡 {current['analysis_explanation']}"
    )

    st.divider()

    # ------------------------------------------------------
    # V4 SCORE BREAKDOWN
    # ------------------------------------------------------

    st.subheader(
        "🎯 V4 Score Breakdown"
    )

    score_cols = st.columns(5)

    score_items = [
        (
            "Trend",
            current["trend_score"],
            30
        ),
        (
            "Momentum",
            current["momentum_score"],
            30
        ),
        (
            "Volume",
            current["volume_score"],
            15
        ),
        (
            "Quality",
            current["quality_score"],
            15
        ),
        (
            "Risk",
            current["risk_score"],
            10
        )
    ]

    for col, (
        name,
        value,
        maximum
    ) in zip(
        score_cols,
        score_items
    ):

        with col:

            if pd.isna(value):

                st.metric(
                    name,
                    "N/A"
                )

            else:

                st.metric(
                    name,
                    f"{value:.0f}/{maximum}"
                )

    st.divider()

    # ------------------------------------------------------
    # PRICE + MOVING AVERAGES
    # ------------------------------------------------------

    st.subheader(
        "📈 Price & Moving Averages"
    )

    fig_price = go.Figure()

    fig_price.add_trace(
        go.Candlestick(
            x=history["date"],
            open=history["open"],
            high=history["high"],
            low=history["low"],
            close=history["close"],
            name="Price"
        )
    )

    moving_averages = [
        ("sma_20", "SMA 20"),
        ("sma_50", "SMA 50"),
        ("sma_200", "SMA 200")
    ]

    for column, name in moving_averages:

        if column in history.columns:

            fig_price.add_trace(
                go.Scatter(
                    x=history["date"],
                    y=history[column],
                    name=name,
                    mode="lines"
                )
            )

    fig_price.update_layout(
        template="plotly_dark",
        height=600,
        paper_bgcolor="#0b1120",
        plot_bgcolor="#0b1120",
        hovermode="x unified",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    st.subheader(
        "📊 Relative Strength Index"
    )

    if "rsi" in history.columns:

        fig_rsi = go.Figure()

        fig_rsi.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["rsi"],
                name="RSI",
                mode="lines"
            )
        )

        fig_rsi.add_hline(
            y=70,
            line_dash="dash",
            annotation_text="Overbought 70"
        )

        fig_rsi.add_hline(
            y=50,
            line_dash="dot",
            annotation_text="Midline 50"
        )

        fig_rsi.add_hline(
            y=30,
            line_dash="dash",
            annotation_text="Oversold 30"
        )

        fig_rsi.update_layout(
            template="plotly_dark",
            height=350,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            yaxis=dict(
                range=[0, 100]
            ),
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_rsi,
            use_container_width=True
        )

    # ------------------------------------------------------
    # MACD
    # ------------------------------------------------------

    st.subheader(
        "📉 MACD"
    )

    if "macd" in history.columns:

        fig_macd = go.Figure()

        fig_macd.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["macd"],
                name="MACD",
                mode="lines"
            )
        )

        if "macd_signal" in history.columns:

            fig_macd.add_trace(
                go.Scatter(
                    x=history["date"],
                    y=history["macd_signal"],
                    name="Signal",
                    mode="lines"
                )
            )

        if "macd_histogram" in history.columns:

            fig_macd.add_trace(
                go.Bar(
                    x=history["date"],
                    y=history["macd_histogram"],
                    name="Histogram"
                )
            )

        fig_macd.update_layout(
            template="plotly_dark",
            height=400,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_macd,
            use_container_width=True
        )

    # ------------------------------------------------------
    # VOLATILITY / ATR
    # ------------------------------------------------------

    st.subheader(
        "📐 Volatility"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if "atr" in history.columns:

            st.metric(
                "ATR",
                f'{current["atr"]:.2f}'
            )

    with c2:

        if "atr_percent" in history.columns:

            st.metric(
                "ATR %",
                f'{current["atr_percent"]:.2f}%'
            )

    with c3:

        if "volatility_20" in history.columns:

            st.metric(
                "20D Volatility",
                f'{current["volatility_20"]:.2f}%'
            )

    # ------------------------------------------------------
    # BOLLINGER BANDS
    # ------------------------------------------------------

    if all(
        column in history.columns
        for column in [
            "bb_upper",
            "bb_middle",
            "bb_lower"
        ]
    ):

        st.subheader(
            "📏 Bollinger Bands"
        )

        fig_bb = go.Figure()

        fig_bb.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["close"],
                name="Price",
                mode="lines"
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["bb_upper"],
                name="Upper Band",
                mode="lines"
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["bb_middle"],
                name="Middle Band",
                mode="lines"
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=history["date"],
                y=history["bb_lower"],
                name="Lower Band",
                mode="lines"
            )
        )

        fig_bb.update_layout(
            template="plotly_dark",
            height=450,
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_bb,
            use_container_width=True
        )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "📊 Stock Market Intelligence • "
    "Rule-based technical analysis • "
    "Decision-support system • "
    "Not financial advice"
)
