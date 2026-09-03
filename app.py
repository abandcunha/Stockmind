import streamlit as st
from db import init_db

st.set_page_config(page_title="StockMind", page_icon="📈", layout="wide")

init_db()

st.title("📈 StockMind")
st.caption("Your personal research hub — watchlist, stock & sector analysis, and scenario modelling.")

st.markdown(
    """
Use the pages in the left sidebar:

- **Watchlist** — add stocks with the price you started watching them at, and see how far they've moved since.
- **Stock Analysis** — pull up fundamentals, ratios and price history for any ticker (ASX / US / India).
- **Sector Analysis** — compare performance and metrics across sectors and sub-sectors in your watchlist.
- **Scenario Calculator** — build DCF / target-price / what-if scenarios and save them against a stock.

Ticker format reminder:
- ASX: `BHP.AX`
- US: `AAPL`
- India (NSE): `RELIANCE.NS`  /  India (BSE): `500325.BO`
"""
)

st.info(
    "Data comes from Yahoo Finance (via yfinance) — free, but can lag a few minutes and "
    "occasionally rate-limits. Treat prices as indicative, not execution-grade.",
    icon="ℹ️",
)
