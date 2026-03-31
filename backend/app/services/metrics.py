import pandas as pd


def _as_float(value: float | int) -> float:
    return float(value) if pd.notna(value) else 0.0


def interpret_score(score: float) -> str:
    if score > 0.05:
        return "Strong"
    if score > 0:
        return "Moderate"
    return "Risky"


def _compute_trend_score(df: pd.DataFrame) -> float:
    first_close = df["Close"].iloc[0]
    last_close = df["Close"].iloc[-1]
    if pd.isna(first_close) or first_close == 0:
        return 0.0
    return _as_float((last_close - first_close) / first_close)


def _compute_volatility(df: pd.DataFrame) -> float:
    daily_returns = (df["Close"] - df["Open"]) / df["Open"]
    return _as_float(daily_returns.std())


def _compute_health_score(trend_score: float, volatility: float) -> float:
    return _as_float((trend_score * 0.6) + ((1 - volatility) * 0.4))


def add_metrics(df: pd.DataFrame):
    metrics_df = df.copy()
    metrics_df = metrics_df.dropna(subset=["Open", "Close"]).reset_index(drop=True)

    if metrics_df.empty:
        return metrics_df

    metrics_df["daily_return"] = (metrics_df["Close"] - metrics_df["Open"]) / metrics_df["Open"]
    metrics_df["ma_7"] = metrics_df["Close"].rolling(window=7).mean()
    metrics_df["volatility"] = metrics_df["daily_return"].rolling(window=7).std()

    trend_score = _compute_trend_score(metrics_df)
    volatility_value = _as_float(metrics_df["volatility"].iloc[-1])
    health_score = _compute_health_score(trend_score, volatility_value)

    metrics_df["trend_score"] = trend_score
    metrics_df["stock_health_score"] = health_score
    metrics_df["daily_return"] = metrics_df["daily_return"].fillna(0.0).astype(float)
    metrics_df["ma_7"] = metrics_df["ma_7"].fillna(0.0).astype(float)
    metrics_df["volatility"] = metrics_df["volatility"].fillna(0.0).astype(float)
    metrics_df["trend_score"] = metrics_df["trend_score"].fillna(0.0).astype(float)
    metrics_df["stock_health_score"] = metrics_df["stock_health_score"].fillna(0.0).astype(float)

    return metrics_df


def summary_metrics(df: pd.DataFrame):
    summary_df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()

    if summary_df.empty:
        return {
            "52_week_high": 0.0,
            "52_week_low": 0.0,
            "avg_close": 0.0,
            "volatility": 0.0,
            "trend_score": 0.0,
            "health_score": 0.0,
            "insight": "Risky",
        }

    volatility = _compute_volatility(summary_df)
    trend_score = _compute_trend_score(summary_df)
    health_score = _compute_health_score(trend_score, volatility)

    return {
        "52_week_high": _as_float(summary_df["High"].max()),
        "52_week_low": _as_float(summary_df["Low"].min()),
        "avg_close": _as_float(summary_df["Close"].mean()),
        "volatility": volatility,
        "trend_score": trend_score,
        "health_score": health_score,
        "insight": interpret_score(health_score),
    }