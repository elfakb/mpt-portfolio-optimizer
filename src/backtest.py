# backtest.py - 5 yıllık backtest + aylık rebalancing simülasyonu

import pandas as pd

from src.config import PROCESSED_PATH, REBALANCE_FREQUENCY
from src.mean_variance import optimize_max_sharpe

from src.data_loader import load_prices  # dosyanın en üstüne ekle (yoksa)
from src.config import MAX_CRYPTO_WEIGHT, MIN_GOLD_WEIGHT
def get_benchmark_returns(prices, benchmark="SPY", initial_value=100000):

    full_prices = load_prices()  # her zaman tüm 30 varlığı içeren tam veri seti
    benchmark_prices = full_prices[benchmark]

    # Kullanıcının seçtiği veri aralığıyla hizala (varsa)
    benchmark_prices = benchmark_prices.reindex(prices.index).ffill().bfill()

    normalized = benchmark_prices / benchmark_prices.iloc[0] * initial_value
    return normalized.to_frame(name="portfolio_value")

def load_prices():
    return pd.read_csv(PROCESSED_PATH, index_col=0, parse_dates=True)


def get_rebalance_dates(prices, freq=REBALANCE_FREQUENCY):
    """Her ayın ilk trading gününü rebalancing tarihi olarak alır."""
    return prices.resample(freq).first().index


from src.risk_parity import optimize_risk_parity  # dosyanın en üstüne ekle


def run_backtest(prices, strategy="max_sharpe", initial_value=100000, lookback_days=252,
                  max_crypto=None, min_gold=None):
    """
    strategy: "max_sharpe" veya "risk_parity"
    """
    rebalance_dates = get_rebalance_dates(prices)
    portfolio_value = initial_value
    history = []

    for i in range(len(rebalance_dates) - 1):
        current_date = rebalance_dates[i]
        next_date = rebalance_dates[i + 1]

        train_data = prices.loc[:current_date].tail(lookback_days)
        if len(train_data) < 30:
            continue

        try:
            if strategy == "max_sharpe":
                if max_crypto is not None:
                    weights, _ = optimize_max_sharpe(train_data,max_crypto = MAX_CRYPTO_WEIGHT, min_gold = MIN_GOLD_WEIGHT)
                else:
                    weights, _ = optimize_max_sharpe(train_data,max_crypto = MAX_CRYPTO_WEIGHT, min_gold = MIN_GOLD_WEIGHT)
            else:  # risk_parity
                weights = optimize_risk_parity(train_data)
        except Exception:
            continue

        period_prices = prices.loc[current_date:next_date]
        period_returns = period_prices.pct_change().dropna()

        weight_array = pd.Series(weights)
        daily_portfolio_returns = period_returns[weight_array.index] @ weight_array

        for date, ret in daily_portfolio_returns.items():
            portfolio_value *= (1 + ret)
            history.append({"date": date, "portfolio_value": portfolio_value})

    return pd.DataFrame(history).set_index("date")


from src.config import RISK_FREE_RATE

def backtest_performance_summary(history):
    values = history["portfolio_value"]
    total_return = values.iloc[-1] / values.iloc[0] - 1

    daily_returns = values.pct_change().dropna()
    annual_return = (1 + total_return) ** (252 / len(values)) - 1
    annual_vol = daily_returns.std() * (252 ** 0.5)
    sharpe = (annual_return - RISK_FREE_RATE) / annual_vol

    running_max = values.cummax()
    drawdown = (values - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }


if __name__ == "__main__":
    prices = load_prices()
    history = run_backtest(prices)
    summary = backtest_performance_summary(history)

    print(f"Başlangıç: 100,000 USD -> Bitiş: {history['portfolio_value'].iloc[-1]:,.0f} USD")
    print(f"Toplam Getiri: {summary['total_return']:.2%}")
    print(f"Yıllık Getiri: {summary['annual_return']:.2%}")
    print(f"Yıllık Volatilite: {summary['annual_volatility']:.2%}")
    print(f"Maksimum Drawdown: {summary['max_drawdown']:.2%}")