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


@st.cache_data(ttl=300, show_spinner=False)
def get_quote(ticker: str):
    """Return a dict of current price + key snapshot fields for a ticker."""
    t = yf.Ticker(ticker)
    info = t.fast_info
    try:
        slow = t.info
    except Exception:
        slow = {}
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
