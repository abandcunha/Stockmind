"""
Shared visual styling for StockMind — a single CSS injection so every page
looks consistent, plus small helpers for colored "move" badges and market flags.
"""
import streamlit as st

MARKET_FLAGS = {
    "ASX (Australia)": "🇦🇺",
    "US (NASDAQ)": "🇺🇸",
    "US (NYSE)": "🇺🇸",
    "US (NYSE Arca)": "🇺🇸",
    "US (NYSE American)": "🇺🇸",
    "India (NSE)": "🇮🇳",
    "India (BSE)": "🇮🇳",
}


def market_flag(market: str) -> str:
    return MARKET_FLAGS.get(market, "🌐")


def inject_css():
    st.markdown(
        """
        <style>
        /* Overall page polish */
        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }
        h1 {
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }
        h2, h3 {
            font-weight: 700 !important;
        }

        /* Card container used across pages */
        .sm-card {
            background: linear-gradient(180deg, rgba(127,127,127,0.06) 0%, rgba(127,127,127,0.02) 100%);
            border: 1px solid rgba(127,127,127,0.18);
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 0.8rem;
            transition: border-color 0.15s ease;
        }
        .sm-card:hover {
            border-color: rgba(127,127,127,0.4);
        }
        .sm-card-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }
        .sm-card-sub {
            font-size: 0.82rem;
            opacity: 0.65;
            margin-bottom: 0.5rem;
        }
        .sm-price {
            font-size: 1.6rem;
            font-weight: 800;
        }
        .sm-move-up {
            color: #16a34a;
            font-weight: 700;
        }
        .sm-move-down {
            color: #dc2626;
            font-weight: 700;
        }
        .sm-move-flat {
            color: #9ca3af;
            font-weight: 700;
        }
        .sm-tag {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            background: rgba(99,102,241,0.12);
            color: #6366f1;
            margin-right: 0.35rem;
        }

        /* Metric styling */
        div[data-testid="stMetric"] {
            background: rgba(127,127,127,0.05);
            border: 1px solid rgba(127,127,127,0.15);
            border-radius: 12px;
            padding: 0.7rem 0.9rem;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def move_badge(move_pct):
    if move_pct is None:
        return '<span class="sm-move-flat">—</span>'
    cls = "sm-move-up" if move_pct > 0 else ("sm-move-down" if move_pct < 0 else "sm-move-flat")
    arrow = "▲" if move_pct > 0 else ("▼" if move_pct < 0 else "→")
    return f'<span class="{cls}">{arrow} {move_pct:+.2f}%</span>'
