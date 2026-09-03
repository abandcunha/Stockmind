import streamlit as st
from datetime import date

from db import get_session, WatchlistItem, init_db
from market_data import get_quote, search_by_name
from style import inject_css, market_flag, move_badge

init_db()
st.set_page_config(page_title="Watchlist", page_icon="👀", layout="wide")
inject_css()
st.title("👀 Watchlist")

# ---------------------------------------------------------------------------
# Search by company name
# ---------------------------------------------------------------------------
st.subheader("🔎 Search by company name")
name_query = st.text_input("Type a company name (e.g. Reliance, Commonwealth Bank, Apple)", key="wl_name_search")
picked_ticker = None

if name_query:
    matches = search_by_name(name_query)
    if matches:
        distinct_markets = {m["market"] for m in matches if m.get("market")}
        if len(distinct_markets) > 1:
            st.warning(
                f"Found this name on {len(distinct_markets)} different markets — pick the exact one you mean below."
            )
        options = {
            f"{market_flag(m['market'])} {m['name']} — {m['symbol']}  ·  {m['market']}": m["symbol"]
            for m in matches
        }
        choice = st.selectbox("Matching stocks — pick one", options=list(options.keys()), key="wl_name_choice")
        picked_ticker = options[choice]
        st.caption(f"Selected ticker: **{picked_ticker}**")
    else:
        st.caption("No matches found — try a different spelling, or enter the ticker directly below.")

# ---------------------------------------------------------------------------
# Add to watchlist
# ---------------------------------------------------------------------------
with st.expander("➕ Add a stock to your watchlist", expanded=True):
    with st.form("add_stock"):
        col1, col2, col3 = st.columns(3)
        ticker = col1.text_input(
            "Ticker (e.g. BHP.AX, AAPL, RELIANCE.NS)",
            value=picked_ticker or "",
        ).strip().upper()
        watch_price = col2.number_input("Price when you started watching", min_value=0.0, step=0.01)
        watch_date = col3.date_input("Date you started watching", value=date.today())

        col4, col5 = st.columns(2)
        sector = col4.text_input("Sector (optional — auto-filled if left blank)")
        sub_sector = col5.text_input("Sub-sector / industry (optional)")

        notes = st.text_area("Notes / thesis")
        submitted = st.form_submit_button("Add to watchlist", use_container_width=True)

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
                    market=quote.get("market") or "Unknown",
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

# ---------------------------------------------------------------------------
# Watchlist display
# ---------------------------------------------------------------------------
session = get_session()
items = session.query(WatchlistItem).order_by(WatchlistItem.created_at.desc()).all()
session.close()

header_col1, header_col2 = st.columns([4, 1])
header_col1.subheader(f"Your stocks ({len(items)})")
refresh_clicked = header_col2.button("🔄 Refresh market info", use_container_width=True,
                                      help="Re-checks each stock's market/exchange and currency from live data — fixes any stocks added before the market-detection update.")

if refresh_clicked and items:
    s = get_session()
    fixed = 0
    for item in items:
        obj = s.get(WatchlistItem, item.id)
        try:
            q = get_quote(obj.ticker)
        except Exception:
            q = {}
        new_market = q.get("market")
        new_currency = q.get("currency")
        if new_market and new_market != obj.market:
            obj.market = new_market
            fixed += 1
        if new_currency and new_currency != obj.currency:
            obj.currency = new_currency
        if not obj.sector and q.get("sector"):
            obj.sector = q.get("sector")
        if not obj.sub_sector and q.get("industry"):
            obj.sub_sector = q.get("industry")
    s.commit()
    s.close()
    st.success(f"Refreshed {len(items)} stock(s) — corrected market on {fixed}.")
    st.rerun()

if not items:
    st.info("Your watchlist is empty. Add your first stock above.")
else:
    view = st.radio("View as", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")

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
            "Move %": move_pct,
            "Currency": item.currency or quote.get("currency") or "",
        })

    if view == "Cards":
        cols = st.columns(3)
        for i, r in enumerate(rows):
            with cols[i % 3]:
                flag = market_flag(r["Market"])
                price_str = f"{r['Current price']:.2f} {r['Currency']}" if r["Current price"] else "—"
                watch_str = f"{r['Watch price']:.2f} {r['Currency']}"
                st.markdown(
                    f"""
                    <div class="sm-card">
                        <span class="sm-tag">{flag} {r['Market'] or 'Unknown'}</span>
                        <div class="sm-card-title" style="margin-top:0.5rem;">{r['Name'] or r['Ticker']}</div>
                        <div class="sm-card-sub">{r['Ticker']} · {r['Sector'] or 'Uncategorised'}</div>
                        <div class="sm-price">{price_str}</div>
                        <div style="margin-top:0.2rem;">{move_badge(r['Move %'])}
                            <span style="opacity:0.6; font-size:0.8rem;"> since {watch_str} on {r['Watch date']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        import pandas as pd
        display_rows = []
        for r in rows:
            display_rows.append({
                "Ticker": r["Ticker"],
                "Name": r["Name"],
                "Market": f"{market_flag(r['Market'])} {r['Market']}",
                "Sector": r["Sector"],
                "Sub-sector": r["Sub-sector"],
                "Watch price": f"{r['Watch price']:.2f} {r['Currency']}",
                "Watch date": r["Watch date"],
                "Current price": f"{r['Current price']:.2f} {r['Currency']}" if r["Current price"] else "—",
                "Move since watched": f"{r['Move %']:+.2f}%" if r["Move %"] is not None else "—",
            })
        df = pd.DataFrame(display_rows)
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
