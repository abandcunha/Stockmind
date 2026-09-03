import streamlit as st
from datetime import date

from db import get_session, WatchlistItem, init_db
from market_data import get_quote, guess_market

init_db()
st.set_page_config(page_title="Watchlist", page_icon="👀", layout="wide")
st.title("👀 Watchlist")

with st.expander("➕ Add a stock to your watchlist", expanded=False):
    with st.form("add_stock"):
        col1, col2, col3 = st.columns(3)
        ticker = col1.text_input("Ticker (e.g. BHP.AX, AAPL, RELIANCE.NS)").strip().upper()
        watch_price = col2.number_input("Price when you started watching", min_value=0.0, step=0.01)
        watch_date = col3.date_input("Date you started watching", value=date.today())

        col4, col5 = st.columns(2)
        sector = col4.text_input("Sector (optional — auto-filled if left blank)")
        sub_sector = col5.text_input("Sub-sector / industry (optional)")

        notes = st.text_area("Notes / thesis")
        submitted = st.form_submit_button("Add to watchlist")

        if submitted:
            if not ticker or watch_price <= 0:
                st.error("Please provide a ticker and a valid watch price.")
            else:
                quote = {}
                try:
                    quote = get_quote(ticker)
                except Exception:
                    pass
                s = get_session()
                item = WatchlistItem(
                    ticker=ticker,
                    display_name=quote.get("long_name") or ticker,
                    market=guess_market(ticker),
                    sector=sector or quote.get("sector"),
                    sub_sector=sub_sector or quote.get("industry"),
                    watch_price=watch_price,
                    watch_date=watch_date,
                    currency=quote.get("currency"),
                    notes=notes,
                )
                s.add(item)
                s.commit()
                s.close()
                st.success(f"Added {ticker} to your watchlist.")
                st.rerun()

st.divider()

session = get_session()
items = session.query(WatchlistItem).order_by(WatchlistItem.created_at.desc()).all()
session.close()

if not items:
    st.info("Your watchlist is empty. Add your first stock above.")
else:
    rows = []
    for item in items:
        quote = {}
        try:
            quote = get_quote(item.ticker)
        except Exception:
            pass
        current_price = quote.get("price")
        move_pct = None
        if current_price and item.watch_price:
            move_pct = (current_price - item.watch_price) / item.watch_price * 100

        rows.append({
            "id": item.id,
            "Ticker": item.ticker,
            "Name": item.display_name,
            "Market": item.market,
            "Sector": item.sector,
            "Sub-sector": item.sub_sector,
            "Watch price": item.watch_price,
            "Watch date": item.watch_date,
            "Current price": current_price,
            "Move since watched": f"{move_pct:+.2f}%" if move_pct is not None else "—",
            "Currency": item.currency,
        })

    import pandas as pd
    df = pd.DataFrame(rows).drop(columns=["id"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Remove a stock")
    to_remove = st.selectbox(
        "Select a ticker to remove",
        options=[r["id"] for r in rows],
        format_func=lambda i: next(r["Ticker"] for r in rows if r["id"] == i),
    )
    if st.button("Remove selected stock", type="secondary"):
        s = get_session()
        obj = s.get(WatchlistItem, to_remove)
        if obj:
            s.delete(obj)
            s.commit()
        s.close()
        st.rerun()
