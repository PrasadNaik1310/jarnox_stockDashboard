from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from ..services.data_fetcher import fetch_stock_data
from ..services.metrics import add_metrics, summary_metrics

router = APIRouter(prefix="/stocks", tags=["stocks"])

COMPANIES = ["INFY", "TCS", "RELIANCE", "HDFCBANK"]


def _safe_json_records(df: pd.DataFrame) -> list[dict]:
    records_df = df.copy()
    if "Date" in records_df.columns:
        records_df["Date"] = pd.to_datetime(records_df["Date"]).dt.strftime("%Y-%m-%d")

    records_df = records_df.where(pd.notnull(records_df), None)
    return records_df.to_dict(orient="records")


@router.get("/companies")
def get_companies() -> dict:
    return {"companies": COMPANIES}


@router.get("/data/{symbol}")
def get_processed_stock_data(symbol: str) -> dict:
    try:
        raw_df = fetch_stock_data(symbol=symbol, period="3mo")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch stock data") from exc

    processed_df = add_metrics(raw_df).tail(30)
    return {
        "symbol": symbol.upper(),
        "data": _safe_json_records(processed_df),
    }


@router.get("/summary/{symbol}")
def get_stock_summary(symbol: str) -> dict:
    try:
        raw_df = fetch_stock_data(symbol=symbol, period="1y")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch stock data") from exc

    summary = summary_metrics(raw_df)
    return {"symbol": symbol.upper(), "summary": summary}


@router.get("/compare")
def compare_stocks(
    symbol1: str = Query(..., min_length=1),
    symbol2: str = Query(..., min_length=1),
) -> dict:
    try:
        df1 = fetch_stock_data(symbol=symbol1, period="3mo")
        df2 = fetch_stock_data(symbol=symbol2, period="3mo")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch stock data") from exc

    clean_df1 = df1.dropna(subset=["Close"]).reset_index(drop=True)
    clean_df2 = df2.dropna(subset=["Close"]).reset_index(drop=True)

    if clean_df1.empty or clean_df2.empty:
        raise HTTPException(status_code=404, detail="Insufficient data to compare symbols")

    first_close_1 = float(clean_df1["Close"].iloc[0])
    first_close_2 = float(clean_df2["Close"].iloc[0])

    return_1 = 0.0 if first_close_1 == 0 else float((clean_df1["Close"].iloc[-1] - first_close_1) / first_close_1)
    return_2 = 0.0 if first_close_2 == 0 else float((clean_df2["Close"].iloc[-1] - first_close_2) / first_close_2)
    return_diff = round(float(return_1 - return_2), 4)
    return_diff_percentage = abs(return_diff * 100)

    symbol1_upper = symbol1.upper()
    symbol2_upper = symbol2.upper()

    if return_1 > return_2:
        winner = symbol1_upper
        insight = f"{symbol1_upper} outperformed {symbol2_upper} by {return_diff_percentage:.2f}% over the selected period"
    elif return_2 > return_1:
        winner = symbol2_upper
        insight = f"{symbol2_upper} outperformed {symbol1_upper} by {return_diff_percentage:.2f}% over the selected period"
    else:
        winner = "TIE"
        insight = f"{symbol1_upper} and {symbol2_upper} performed equally over the selected period"

    return {
        "symbol1": symbol1_upper,
        "symbol2": symbol2_upper,
        "return_diff": return_diff,
        "winner": winner,
        "insight": insight,
    }
