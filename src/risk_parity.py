import numpy as np 
import pandas as pd 
from scipy.optimize import minimize # riske göre en yii ağırlıları bulmak için 

from src.config import PROCESSED_PATH

def load_prices():
    return pd.read_csv(PROCESSED_PATH , index_col = 0, parse_dates = True)


# kovaryans matrisi hesaplar cointegre = irbiryle benzer hareket eden hissseler için 
def get_covariance(prices): 
    returns = prices.pct_change().dropna() # günlük getirileri heseplar
    return returns.cov() * 252  # 1 yıllık toplam cov hesaplanır 


# her varlığın portföyün toplam riskine katkısını ölçer
def risk_contribution(weights, sigma): 

    weights = np.array(weights)  # portföy voltalitesi 
    portfolio_vol = np.sqrt(weights @ sigma @ weights) # portföyün toplam volatilitesini hesaplarız : ağırlık * kovaryans matrisi * portföy voltalitesi 

    marginal_contribution = sigma @ weights  #  portföydeki ağırlıkları ile kovaryans matrisi çarpılarak her hissenin portföye özel katkısı hesaplanıyor RİSKE

    contribution = weights * marginal_contribution / portfolio_vol # her varlığın portföy riskine katkısı

    return contribution


def risk_parity_objective(weights, sigma): #  her varlığın portföy riskine katkısını eşitlemeye çalışır
    contribution = risk_contribution(weights, sigma)
    target = contribution.mean()
    return np.sum((contribution - target) ** 2) # farkların kareleri toplamı 


def optimize_risk_parity(prices): # risk parity optimizasyonu: ağırlıkları optimize eder
    sigma = get_covariance(prices)

    n = sigma.shape[0]

    init_weights = np.ones(n) / n 
    
    bounds = [(0, 1) for _ in range(n)] 
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

    result = minimize(
        risk_parity_objective,
        init_weights,
        args=(sigma,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    weights = dict(zip(prices.columns, result.x))
    return weights


if __name__ == "__main__":

    prices = load_prices()
    weights = optimize_risk_parity(prices)

    print("Risk Parity Ağırlıkları:")
    for asset, w in sorted(weights.items(), key=lambda x: -x[1]):
        if w > 0.001:
            print(f"  {asset}: {w:.2%}")
