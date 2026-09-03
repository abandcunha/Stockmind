import json
import streamlit as st
import pandas as pd

from db import get_session, WatchlistItem, Scenario, init_db
from market_data import get_quote

init_db()
st.set_page_config(page_title="Scenario Calculator", page_icon="🧮", layout="wide")
st.title("🧮 Scenario Calculator")

session = get_session()
watchlist = session.query(WatchlistItem).all()
session.close()

tab_dcf, tab_multiple, tab_whatif, tab_saved = st.tabs(
    ["DCF (Discounted Cash Flow)", "Target Price (P/E Multiple)", "What-if Sensitivity", "Saved Scenarios"]
)

# ---------- DCF ----------
with tab_dcf:
    st.write("Estimate an intrinsic value per share from projected free cash flows.")
    col1, col2 = st.columns(2)
    ticker = col1.text_input("Ticker (optional, for reference/saving)", key="dcf_ticker").strip().upper()
    shares_out = col2.number_input("Shares outstanding (millions)", min_value=0.0, value=1000.0)

    c1, c2, c3 = st.columns(3)
    fcf0 = c1.number_input("Current annual free cash flow (millions)", value=100.0)
    growth = c2.number_input("Growth rate, years 1-5 (%)", value=10.0) / 100
    terminal_growth = c3.number_input("Terminal growth rate (%)", value=2.5) / 100

    c4, c5, c6 = st.columns(3)
    discount_rate = c4.number_input("Discount rate / WACC (%)", value=9.0) / 100
    years = c5.number_input("Projection years", min_value=1, max_value=15, value=5, step=1)
    net_debt = c6.number_input("Net debt (millions, subtract from value)", value=0.0)

    if st.button("Calculate DCF value"):
        cash_flows = []
        cf = fcf0
        for y in range(1, int(years) + 1):
            cf = cf * (1 + growth)
            cash_flows.append(cf)

        pv_cash_flows = [cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows, start=1)]
        terminal_value = cash_flows[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)

        enterprise_value = sum(pv_cash_flows) + pv_terminal
        equity_value = enterprise_value - net_debt
        value_per_share = equity_value / shares_out if shares_out else None

        st.success(f"Estimated intrinsic value per share: **{value_per_share:,.2f}**")
        st.write(f"Enterprise value: {enterprise_value:,.1f}m | Equity value: {equity_value:,.1f}m")

        if ticker:
            try:
                current = get_quote(ticker).get("price")
                if current and value_per_share:
                    upside = (value_per_share - current) / current * 100
                    st.info(f"Current price: {current:.2f} → implied upside/downside: {upside:+.1f}%")
            except Exception:
                pass

        if ticker and st.checkbox("Save this DCF scenario", key="save_dcf"):
            match = next((w for w in watchlist if w.ticker == ticker), None)
            s = get_session()
            s.add(Scenario(
                stock_id=match.id if match else None,
                name=f"DCF — {ticker}",
                scenario_type="DCF",
                assumptions_json=json.dumps({
                    "fcf0": fcf0, "growth": growth, "terminal_growth": terminal_growth,
                    "discount_rate": discount_rate, "years": years, "net_debt": net_debt,
                    "shares_out": shares_out,
                }),
                result_summary=json.dumps({"value_per_share": value_per_share, "enterprise_value": enterprise_value}),
            ))
            s.commit()
            s.close()
            st.success("Scenario saved.")

# ---------- Target price via multiple ----------
with tab_multiple:
    st.write("Estimate a target price by applying a P/E (or other) multiple to a projected earnings figure.")
    col1, col2, col3 = st.columns(3)
    ticker_m = col1.text_input("Ticker (optional)", key="mult_ticker").strip().upper()
    eps_forecast = col2.number_input("Forecast EPS", value=1.0)
    target_multiple = col3.number_input("Target P/E multiple", value=15.0)

    if st.button("Calculate target price"):
        target_price = eps_forecast * target_multiple
        st.success(f"Implied target price: **{target_price:,.2f}**")
        if ticker_m:
            try:
                current = get_quote(ticker_m).get("price")
                if current:
                    upside = (target_price - current) / current * 100
                    st.info(f"Current price: {current:.2f} → implied upside/downside: {upside:+.1f}%")
            except Exception:
                pass

        if ticker_m and st.checkbox("Save this scenario", key="save_mult"):
            match = next((w for w in watchlist if w.ticker == ticker_m), None)
            s = get_session()
            s.add(Scenario(
                stock_id=match.id if match else None,
                name=f"Target Price — {ticker_m}",
                scenario_type="Multiple",
                assumptions_json=json.dumps({"eps_forecast": eps_forecast, "target_multiple": target_multiple}),
                result_summary=json.dumps({"target_price": target_price}),
            ))
            s.commit()
            s.close()
            st.success("Scenario saved.")

# ---------- What-if sensitivity ----------
with tab_whatif:
    st.write("See how target price / valuation reacts across a range of two assumptions at once.")
    col1, col2 = st.columns(2)
    base_eps = col1.number_input("Base forecast EPS", value=1.0, key="wi_eps")
    base_multiple = col2.number_input("Base P/E multiple", value=15.0, key="wi_mult")

    eps_range = st.slider("EPS range to test (± %)", 0, 100, 20)
    mult_range = st.slider("Multiple range to test (± %)", 0, 100, 20)

    eps_values = [base_eps * f for f in [1 - eps_range/100, 1 - eps_range/200, 1, 1 + eps_range/200, 1 + eps_range/100]]
    mult_values = [base_multiple * f for f in [1 - mult_range/100, 1 - mult_range/200, 1, 1 + mult_range/200, 1 + mult_range/100]]

    table = pd.DataFrame(
        [[round(e * m, 2) for m in mult_values] for e in eps_values],
        index=[f"EPS {e:.2f}" for e in eps_values],
        columns=[f"×{m:.1f}" for m in mult_values],
    )
    st.write("Target price sensitivity grid (rows = EPS, columns = multiple):")
    st.dataframe(table, use_container_width=True)

# ---------- Saved scenarios ----------
with tab_saved:
    session = get_session()
    scenarios = session.query(Scenario).order_by(Scenario.created_at.desc()).all()
    session.close()
    if not scenarios:
        st.info("No saved scenarios yet.")
    else:
        for sc in scenarios:
            with st.expander(f"{sc.name} ({sc.scenario_type}) — {sc.created_at.strftime('%Y-%m-%d')}"):
                st.write("Assumptions:")
                st.json(json.loads(sc.assumptions_json or "{}"))
                st.write("Result:")
                st.json(json.loads(sc.result_summary or "{}"))
                if st.button("Delete", key=f"del_{sc.id}"):
                    s = get_session()
                    obj = s.get(Scenario, sc.id)
                    if obj:
                        s.delete(obj)
                        s.commit()
                    s.close()
                    st.rerun()
