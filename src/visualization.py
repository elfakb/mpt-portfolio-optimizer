# visualization.py - Grafik üreten fonksiyonlar (plotly)

import plotly.graph_objects as go


def plot_efficient_frontier(frontier_risk, frontier_return, optimal_risk=None, optimal_return=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frontier_risk, y=frontier_return, mode="lines", name="Efficient Frontier"))

    if optimal_risk is not None:
        fig.add_trace(go.Scatter(x=[optimal_risk], y=[optimal_return], mode="markers",
                                  marker=dict(size=12, color="red"), name="Max Sharpe Portföyü"))

    fig.update_layout(xaxis_title="Risk (Volatilite)", yaxis_title="Beklenen Getiri", title="Efficient Frontier")
    return fig


def plot_backtest(history):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history.index, y=history["portfolio_value"], mode="lines", name="Portföy Değeri"))
    fig.update_layout(xaxis_title="Tarih", yaxis_title="Portföy Değeri (USD)", title="Backtest Sonucu")
    return fig


def plot_weights(weights, title="Portföy Ağırlıkları"):
    filtered = {k: v for k, v in weights.items() if v > 0.001}
    fig = go.Figure(data=[go.Pie(labels=list(filtered.keys()), values=list(filtered.values()))])
    fig.update_layout(title=title)
    return fig

def plot_backtest_comparison(histories: dict):
    """
    histories: {"Max Sharpe": df, "Risk Parity": df, "SPY (Benchmark)": df}
    Her df'in 'portfolio_value' sütunu ve tarih index'i olmalı.
    """
    fig = go.Figure()
    colors = {"Max Sharpe": "#4C9AFF", "Risk Parity": "#00C48C", "SPY (Benchmark)": "#FF6B6B"}

    for name, df in histories.items():
        fig.add_trace(go.Scatter(
            x=df.index, y=df["portfolio_value"],
            mode="lines", name=name,
            line=dict(color=colors.get(name))
        ))

    fig.update_layout(xaxis_title="Tarih", yaxis_title="Portföy Değeri (USD)",
                       title="Strateji Karşılaştırması: Max Sharpe vs Risk Parity vs SPY")
    return fig




from src.config import BIST_TICKERS, ETF_TICKERS, US_STOCK_TICKERS, CRYPTO_TICKERS, GOLD_TICKERS

def plot_category_weights(weights, title="Kategori Bazlı Dağılım"):
    categories = {
        "BIST Hisseleri": sum(w for t, w in weights.items() if t in BIST_TICKERS),
        "Uluslararası ETF": sum(w for t, w in weights.items() if t in ETF_TICKERS),
        "ABD Hisseleri": sum(w for t, w in weights.items() if t in US_STOCK_TICKERS),
        "Kripto": sum(w for t, w in weights.items() if t in CRYPTO_TICKERS),
        "Altın/Kıymetli Maden": sum(w for t, w in weights.items() if t in GOLD_TICKERS),
    }
    fig = go.Figure(data=[go.Pie(labels=list(categories.keys()), values=list(categories.values()))])
    fig.update_layout(title=title)
    return fig