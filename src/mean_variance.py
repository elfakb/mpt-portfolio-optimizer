import pandas as pd 
from pypfopt import expected_returns, risk_models, EfficientFrontier
# expected returns : beklenen getiri % ile gelir 
# risk models : kovaryans matrisi  yani kointegre hisseleri bulmak için = birlikte yükselen ve alçalan değerler için 

from src.config import PROCESSED_PATH, CRYPTO_TICKERS, GOLD_TICKERS, MAX_CRYPTO_WEIGHT, MIN_GOLD_WEIGHT, RISK_FREE_RATE

def load_prices():
    return pd.read_csv(PROCESSED_PATH, index_col=0, parse_dates=True)


def efficient_frontier(prices):
    max_crypto = MAX_CRYPTO_WEIGHT
    min_gold = MIN_GOLD_WEIGHT
    # bunlar her portföyde en az % 10 kadar altın yatırımı yapıcağını belirlemek için
    # Her varlığın ortalama yıllık getirisini hesaplıyor.
    mu = expected_returns.mean_historical_return(prices)
    sigma = risk_models.sample_cov(prices) # her hissenin kovaryans matiriis
    ef = EfficientFrontier(mu,sigma)

    tickers = list(prices.columns)
    crypto_idx = [i for i, t in enumerate(tickers) if t in CRYPTO_TICKERS]
    gold_idx = [i for i, t in enumerate(tickers) if t in GOLD_TICKERS]
    # Sadece ilgili varlıklar portföyde varsa kısıtı ekle
    if crypto_idx:
        ef.add_constraint(lambda w: sum(w[i] for i in crypto_idx) <= max_crypto)
    if gold_idx:
        ef.add_constraint(lambda w: sum(w[i] for i in gold_idx) >= min_gold)

    return ef 


# Sharpe Oranı en yüksek portföyü buluyor: Sharpe oranı, birim risk başına ne kadar ek getiri elde edildiğini gösterir. Değer ne kadar yüksekse, risk-getiri dengesi o kadar iyidir.

def optimize_max_sharpe(prices ,max_crypto , min_gold):
    """   max_crypto = MAX_CRYPTO_WEIGHT
    min_gold = MIN_GOLD_WEIGHT"""

    ef = efficient_frontier(prices)
    ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)# Sharpe Oranı en yüksek portföyü buluyor.

    weights = ef.clean_weights()
    performance = ef.portfolio_performance(risk_free_rate=RISK_FREE_RATE)
    return weights, performance

def get_frontier_points(prices ,max_crypto , min_gold , n_points= 30):

    mu = expected_returns.mean_historical_return(prices)
    ef_min = efficient_frontier(prices)
    ef_min.min_volatility()
    min_ret, _, _ = ef_min.portfolio_performance() # minimum volatiliteye sahip portföy bulunur
    
    max_ret = mu.max() #en yüksek beklenen getiri

    # minimum ile maksimum getiri arasında hedef getiriler oluşturu
    target_returns = [min_ret + i * (max_ret - min_ret) / n_points for i in range(n_points)]

    risks, returns = [], []
    for target in target_returns:
        try:
            ef = efficient_frontier(prices)
            ef.efficient_return(target)
            ret, risk, _ = ef.portfolio_performance()
            risks.append(risk)
            returns.append(ret)
        except Exception:
            continue

    return risks, returns


if __name__ == "__main__":
    prices = load_prices()

    weights, (ret, vol, sharpe) = optimize_max_sharpe(prices)

    print("Optimal Ağırlıklar:")
    for asset, w in weights.items():
        if w > 0:
            print(f"  {asset}: {w:.2%}")

    print(f"\nGetiri: {ret:.2%} | Volatilite: {vol:.2%} | Sharpe: {sharpe:.2f}")

