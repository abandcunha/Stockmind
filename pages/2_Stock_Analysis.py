import streamlit as st
from db import get_session, Note, init_db
from market_data import get_quote, get_history, search_by_name
from style import inject_css, market_flag

init_db()
st.set_page_config(page_title="Stock Analysis", page_icon="🔍", layout="wide")
inject_css()
st.title("🔍 Stock Analysis")

st.subheader("🔎 Search by company name")
name_query = st.text_input("Type a company name (e.g. Reliance, Commonwealth Bank, Apple)", key="sa_name_search")
picked_ticker = ""
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
        choice = st.selectbox("Matching stocks — pick one", options=list(options.keys()), key="sa_name_choice")
        picked_ticker = options[choice]
    else:
        st.caption("No matches found — try a different spelling, or enter the ticker directly below.")

ticker = st.text_input(
    "Or enter a ticker directly (e.g. BHP.AX, AAPL, RELIANCE.NS)",
    value=picked_ticker,
).strip().upper()

if ticker:
    try:
        quote = get_quote(ticker)
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}: {e}")
        quote = None

    if quote and quote.get("price"):
        flag = market_flag(quote.get("market"))
        st.markdown(
            f'<span class="sm-tag">{flag} {quote.get("market") or "Unknown market"}</span>',
            unsafe_allow_html=True,
        )
        st.subheader(f"{quote.get('long_name') or ticker} ({ticker})")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price", f"{quote['price']:.2f} {quote.get('currency') or ''}")
        c2.metric("P/E (trailing)", f"{quote['pe_ratio']:.2f}" if quote.get("pe_ratio") else "—")
        c3.metric("52w High", f"{quote['52w_high']:.2f}" if quote.get("52w_high") else "—")
        c4.metric("52w Low", f"{quote['52w_low']:.2f}" if quote.get("52w_low") else "—")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Market Cap", f"{quote['market_cap']:,}" if quote.get("market_cap") else "—")
        c6.metric("Dividend Yield", f"{quote['dividend_yield']*100:.2f}%" if quote.get("dividend_yield") else "—")
        c7.metric("Beta", f"{quote['beta']:.2f}" if quote.get("beta") else "—")
        c8.metric("EPS", f"{quote['eps']:.2f}" if quote.get("eps") else "—")

        st.caption(f"Sector: {quote.get('sector') or '—'}  |  Industry: {quote.get('industry') or '—'}")

        st.divider()
        period = st.select_slider("Price history period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")
        hist = get_history(ticker, period=period)
        if not hist.empty:
            st.line_chart(hist["Close"])
        else:
            st.warning("No price history available.")

        st.divider()
        st.subheader("Notes on this stock")
        session = get_session()
        notes = session.query(Note).filter(Note.ticker == ticker).order_by(Note.created_at.desc()).all()
        session.close()

        with st.form("add_note"):
            title = st.text_input("Note title")
            body = st.text_area("Note body")
            if st.form_submit_button("Save note") and body:
                s = get_session()
                s.add(Note(ticker=ticker, title=title, body=body))
                s.commit()
                s.close()
                st.rerun()

        for n in notes:
            with st.expander(f"{n.title or 'Untitled'} — {n.created_at.strftime('%Y-%m-%d')}"):
                st.write(n.body)
    else:
        st.warning("No data found — check the ticker format (see reminder on the home page).")
else:
    st.info("Enter a ticker above to see fundamentals, price history and your notes.")
