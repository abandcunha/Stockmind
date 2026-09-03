"""
Database layer for StockMind.

Uses SQLAlchemy so the same code works with:
- SQLite locally (default, file-based, for testing on your own machine)
- Postgres (e.g. a free Supabase project) once deployed, via the DATABASE_URL env var

Set the environment variable DATABASE_URL to a Postgres connection string
(e.g. "postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres")
when you deploy, and all your data lives there instead of on any one machine.
"""
import os
from datetime import datetime, date

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///stockmind.db")

# Supabase/Heroku-style URLs sometimes come as postgres:// — SQLAlchemy wants postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), nullable=False)          # e.g. BHP.AX, AAPL, RELIANCE.NS
    display_name = Column(String(100))
    market = Column(String(20))                            # ASX / US / IN / Other
    sector = Column(String(80))
    sub_sector = Column(String(80))
    watch_price = Column(Float, nullable=False)            # price when you started watching
    watch_date = Column(Date, default=date.today)
    currency = Column(String(10))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenarios = relationship("Scenario", back_populates="stock", cascade="all, delete-orphan")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("watchlist.id"))
    name = Column(String(120), nullable=False)
    scenario_type = Column(String(40))                     # "DCF", "Multiple", "What-if"
    assumptions_json = Column(Text)                         # JSON blob of inputs
    result_summary = Column(Text)                           # JSON blob of outputs
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("WatchlistItem", back_populates="scenarios")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20))
    title = Column(String(200))
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
