import streamlit as st
from db import init_db
from style import inject_css

st.set_page_config(page_title="StockMind", page_icon="📈", layout="wide")
init_db()
inject_css()

st.markdown(
    """
    <div style="padding: 1.5rem 0 0.5rem 0;">
        <h1>📈 StockMind</h1>
        <p style="font-size:1.05rem; opacity:0.75; margin-top:-0.5rem;">
            Your personal research hub — watchlist, stock &amp; sector analysis, and scenario modelling.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
cards = [
    (col1, "👀", "Watchlist", "Track entry price and see how far a stock has moved since you started watching."),
    (col2, "🔍", "Stock Analysis", "Fundamentals, ratios and price history for any ticker — search by name."),
    (col3, "🏭", "Sector Analysis", "Compare performance across sectors and sub-sectors in your watchlist."),
    (col4, "🧮", "Scenario Calculator", "DCF, target price, and what-if sensitivity modelling."),
]
for col, icon, title, desc in cards:
    with col:
        st.markdown(
            f"""
            <div class="sm-card" style="min-height:150px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <div class="sm-card-title">{title}</div>
                <div class="sm-card-sub">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

st.markdown("#### 🌐 Markets covered")
c1, c2, c3 = st.columns(3)
c1.markdown('<span class="sm-tag">🇦🇺 ASX</span> BHP.AX, CBA.AX, CSL.AX', unsafe_allow_html=True)
c2.markdown('<span class="sm-tag">🇺🇸 US</span> AAPL, MSFT, TSLA', unsafe_allow_html=True)
c3.markdown('<span class="sm-tag">🇮🇳 India</span> RELIANCE.NS, 500325.BO', unsafe_allow_html=True)

st.caption(
    "Use the search-by-name box on the Watchlist and Stock Analysis pages if you don't know a ticker — "
    "just type the company name and pick the right one, including which exchange, from the list."
)

st.info(
    "Data comes from Yahoo Finance (via yfinance) — free, but can lag a few minutes and "
    "occasionally rate-limits. Treat prices as indicative, not execution-grade.",
    icon="ℹ️",
)
