import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str, period="3mo"):
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise ValueError("Symbol is required")

    ticker_symbol = normalized_symbol if normalized_symbol.endswith(".NS") else f"{normalized_symbol}.NS"
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(period=period)

    if df.empty:
        raise ValueError(f"No data found for symbol: {normalized_symbol}")

    df.reset_index(inplace=True)

    # Keep only relevant columns
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()

    return df