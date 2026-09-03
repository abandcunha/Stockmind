import streamlit as st
import pandas as pd

from db import get_session, WatchlistItem, init_db
from market_data import get_quote
from style import inject_css

init_db()
st.set_page_config(page_title="Sector Analysis", page_icon="🏭", layout="wide")
inject_css()
st.title("🏭 Sector & Sub-sector Analysis")

session = get_session()
items = session.query(WatchlistItem).all()
session.close()

if not items:
    st.info("Add stocks to your watchlist first — sector analysis is built from your watchlist.")
else:
    rows = []
    for item in items:
        try:
            quote = get_quote(item.ticker)
        except Exception:
            quote = {}
        current_price = quote.get("price")
        move_pct = None
        if current_price and item.watch_price:
            move_pct = (current_price - item.watch_price) / item.watch_price * 100
        rows.append({
            "Ticker": item.ticker,
            "Market": item.market,
            "Sector": item.sector or "Unclassified",
            "Sub-sector": item.sub_sector or "Unclassified",
            "Move %": move_pct,
            "P/E": quote.get("pe_ratio"),
            "Market Cap": quote.get("market_cap"),
        })

    df = pd.DataFrame(rows)

    st.subheader("Filter")
    markets = st.multiselect("Market", options=sorted(df["Market"].dropna().unique()), default=list(df["Market"].dropna().unique()))
    filtered = df[df["Market"].isin(markets)] if markets else df

    st.divider()
    st.subheader("Performance by sector")
    sector_summary = filtered.groupby("Sector").agg(
        stocks=("Ticker", "count"),
        avg_move_pct=("Move %", "mean"),
        avg_pe=("P/E", "mean"),
    ).reset_index().sort_values("avg_move_pct", ascending=False)
    st.dataframe(sector_summary, use_container_width=True, hide_index=True)
    if not sector_summary.empty:
        st.bar_chart(sector_summary.set_index("Sector")["avg_move_pct"])

    st.divider()
    st.subheader("Performance by sub-sector")
    subsector_summary = filtered.groupby(["Sector", "Sub-sector"]).agg(
        stocks=("Ticker", "count"),
        avg_move_pct=("Move %", "mean"),
        avg_pe=("P/E", "mean"),
    ).reset_index().sort_values("avg_move_pct", ascending=False)
    st.dataframe(subsector_summary, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("All stocks (raw)")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
