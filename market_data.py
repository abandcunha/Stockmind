"""
Free market data helpers, built on yfinance (no API key required).

Ticker suffix conventions:
  ASX (Australia):    BHP.AX, CBA.AX, CSL.AX
  US (NYSE/NASDAQ):   AAPL, MSFT, TSLA   (no suffix)
  India (NSE):        RELIANCE.NS, TCS.NS
  India (BSE):        500325.BO
"""
import streamlit as st
import yfinance as yf
import pandas as pd


# Maps Yahoo Finance's raw exchange codes to a human-readable market label.
# Yahoo's codes are inconsistent across endpoints, so this covers the common ones;
# anything unrecognized falls back to the raw code rather than a wrong guess.
EXCHANGE_TO_MARKET = {
    "NSI": "India (NSE)", "NSE": "India (NSE)",
    "BSE": "India (BSE)", "BOM": "India (BSE)",
    "ASX": "ASX (Australia)",
    "NMS": "US (NASDAQ)", "NGM": "US (NASDAQ)", "NCM": "US (NASDAQ)",
    "NYQ": "US (NYSE)", "PCX": "US (NYSE Arca)", "ASE": "US (NYSE American)",
}


def exchange_to_market(exchange_code: str) -> str:
    if not exchange_code:
        return "Unknown"
    return EXCHANGE_TO_MARKET.get(exchange_code.upper(), exchange_code)


@st.cache_data(ttl=300, show_spinner=False)
def get_quote(ticker: str):
    """Return a dict of current price + key snapshot fields for a ticker."""
    t = yf.Ticker(ticker)
    info = t.fast_info
    try:
        slow = t.info
    except Exception:
        slow = {}
    exchange_code = getattr(info, "exchange", None) or slow.get("exchange")
    return {
        "ticker": ticker,
        "price": getattr(info, "last_price", None) or slow.get("currentPrice"),
        "currency": getattr(info, "currency", None) or slow.get("currency"),
        "sector": slow.get("sector"),
        "industry": slow.get("industry"),
        "market_cap": slow.get("marketCap"),
        "pe_ratio": slow.get("trailingPE"),
        "forward_pe": slow.get("forwardPE"),
        "dividend_yield": slow.get("dividendYield"),
        "52w_high": slow.get("fiftyTwoWeekHigh"),
        "52w_low": slow.get("fiftyTwoWeekLow"),
        "beta": slow.get("beta"),
        "eps": slow.get("trailingEps"),
        "long_name": slow.get("longName") or slow.get("shortName"),
        "exchange_code": exchange_code,
        "market": exchange_to_market(exchange_code),
    }


@st.cache_data(ttl=900, show_spinner=False)
def get_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    hist = t.history(period=period)
    return hist


def guess_market(ticker: str) -> str:
    if ticker.upper().endswith(".AX"):
        return "ASX"
    if ticker.upper().endswith(".NS") or ticker.upper().endswith(".BO"):
        return "India"
    return "US"


@st.cache_data(ttl=3600, show_spinner=False)
def search_by_name(query: str, max_results: int = 8):
    """
    Look up tickers by company name (e.g. "Reliance", "Commonwealth Bank", "Apple").
    Returns a list of dicts: {symbol, name, exchange, type}.
    """
    if not query or len(query.strip()) < 2:
        return []
    try:
        results = yf.Search(query, max_results=max_results).quotes
    except Exception:
        return []

    out = []
    for r in results:
        symbol = r.get("symbol")
        if not symbol:
            continue
        exchange_code = r.get("exchange") or ""
        out.append({
            "symbol": symbol,
            "name": r.get("shortname") or r.get("longname") or symbol,
            "exchange": exchange_code,
            "market": exchange_to_market(exchange_code) if exchange_code else (r.get("exchDisp") or ""),
            "type": r.get("quoteType") or r.get("typeDisp") or "",
        })
    return out
