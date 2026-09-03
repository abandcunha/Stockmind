# StockMind

A personal stock research hub: watchlist with entry-price tracking, single-stock
fundamentals, sector/sub-sector comparison, and a scenario calculator (DCF, target
price, what-if sensitivity). Built the same way as Teachflow — a local Python/Streamlit
app — but designed to be deployed for free so nothing lives only on your laptop.

## Running locally (optional, for testing)

```bash
pip install -r requirements.txt
streamlit run app.py
```

This uses a local SQLite file (`stockmind.db`) by default.

## Deploying for free so it's not stuck on your PC

This takes about 15-20 minutes, one time, and costs nothing.

### 1. Create a free database (Supabase)

1. Go to supabase.com and sign up free.
2. Create a new project (pick any name/region, set a database password — save it).
3. Once it's ready, go to Project Settings → Database → Connection string → URI.
4. Copy that string. It looks like:
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with the password you set.

This is where all your watchlist, notes and scenarios will actually live — safe even if
your laptop dies, and shared across any device you log in from.

### 2. Put this code on GitHub

1. Create a free GitHub account if you don't have one.
2. Create a new repository (e.g. `stockmind`), and upload all the files in this folder
   (`app.py`, `db.py`, `market_data.py`, `pages/`, `requirements.txt`).

### 3. Deploy on Streamlit Community Cloud (free)

1. Go to share.streamlit.io and sign in with GitHub.
2. Click "New app", pick your `stockmind` repo, branch `main`, main file `app.py`.
3. Before deploying, click "Advanced settings" → "Secrets" and add:
   ```
   DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres"
   ```
4. Deploy. You'll get a permanent URL like `https://stockmind-yourname.streamlit.app`
   that you can open from your phone, work laptop, anywhere.
5. In `db.py`, the app reads `DATABASE_URL` from the environment — Streamlit Cloud
   automatically exposes secrets as environment variables, so no code changes are needed.

### Keeping it updated

Any time you want to change the app, edit the files in your GitHub repo (or push from
your machine) — Streamlit Cloud redeploys automatically within a minute or two.

## Notes on the data

- Market data comes from Yahoo Finance via the free `yfinance` library — no API key,
  but it can lag a few minutes and occasionally rate-limits on heavy use. If you outgrow
  it, the `market_data.py` file is the only place that would need to change to swap in
  a paid provider (e.g. Alpha Vantage, Polygon, Twelve Data).
- Ticker formats: ASX `BHP.AX`, US `AAPL`, India NSE `RELIANCE.NS` / BSE `500325.BO`.

## What's included

- **Watchlist** — add a ticker with the price/date you started watching; see live
  price and % move since then.
- **Stock Analysis** — fundamentals (P/E, market cap, dividend yield, beta, EPS,
  52-week range), price history chart, and free-text notes per ticker.
- **Sector Analysis** — aggregates your watchlist by sector and sub-sector, average
  move %, average P/E, with a bar chart comparison.
- **Scenario Calculator** — DCF valuation, target-price-via-multiple, and a two-variable
  what-if sensitivity grid; scenarios can be saved and reviewed later.

## Roadmap ideas (not built yet, easy to add later)

- Portfolio-level (not just watchlist) position sizing and weighted returns.
- Alerts (e.g. email/notification when a stock moves past a threshold).
- Peer comparison tables within a sub-sector.
- CSV import/export of your watchlist.
