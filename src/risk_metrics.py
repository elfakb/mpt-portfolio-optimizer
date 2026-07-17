#  VaR, CVaR ve Monte Carlo simülasyonu
# VaR : Value at Risk En kötü durumda ne kadar kayıp olacağını hesaplar 
# CVaR : Conditional Value at Risk VaR'ın da ötesindeki kötü senaryolarda ortalama ne kadar kayıp olacağını hesaplar 
# monte Carlo Simulation : Gelecekte binlerce farklı senaryo oluşursa portföy nasıl davranır
import numpy as np
import pandas as pd
from src.config import PROCESSED_PATH


def load_prices():
    return pd.read_csv(PROCESSED_PATH, index_col=0, parse_dates=True)


# portföy ağırlılarıyla portföyün günlük getirisini hesaplama 
def portfolio_returns(prices, weights):
    returns = prices.pct_change().dropna()
    
    weights = np.array([weights[t] for t in prices.columns])

    total = returns @ weights

    return total

# Belirli bir güven seviyesinde beklenen maksimum kayıp. confiance : %95
def historical_var(port_returns, confidence=0.95):

    return -np.percentile(port_returns, (1 - confidence) * 100)

# CVaR (Expected Shortfall): VaR'ın ötesindeki kayıpların ortalaması
def historical_cvar(port_returns, confidence=0.95):
    var = historical_var(port_returns, confidence)
    tail_losses = port_returns[port_returns <= -var]
    return -tail_losses.mean()

#  Portföyün geçmiş getiri dağılımına dayanarak gelecekteki olası değer yollarını simüle eder.
def monte_carlo_simulation(port_returns, n_simulations=10000, n_days=252, initial_value=100000):

    mu = port_returns.mean()
    sigma = port_returns.std()

    simulated_paths = np.zeros((n_simulations, n_days))

    for i in range(n_simulations):
        daily_returns = np.random.normal(mu, sigma, n_days)
        price_path = initial_value * np.cumprod(1 + daily_returns)
        simulated_paths[i] = price_path

    return simulated_paths

# toplam 10.000 portföy değeri hesaplanıyor ve en başarılı olan ı seçeriz bu senaryolardan 1 yıllık Monte Carlo VaR ve CVaR hesaplanıyor.
def monte_carlo_var_cvar(simulated_paths, confidence=0.95, initial_value=100000):

    final_values = simulated_paths[:, -1]
    losses = (initial_value - final_values) / initial_value

    var = np.percentile(losses, confidence * 100)
    cvar = losses[losses >= var].mean()

    return var, cvar


if __name__ == "__main__":
    from src.mean_variance import optimize_max_sharpe

    prices = load_prices()
    weights, _ = optimize_max_sharpe(prices)

    port_returns = portfolio_returns(prices, weights)

    var_95 = historical_var(port_returns, 0.95)
    cvar_95 = historical_cvar(port_returns, 0.95)
    print(f"Tarihsel VaR (%95): {var_95:.2%}")
    print(f"Tarihsel CVaR (%95): {cvar_95:.2%}")

    paths = monte_carlo_simulation(port_returns)
    mc_var, mc_cvar = monte_carlo_var_cvar(paths)
    print(f"\nMonte Carlo VaR (%95, 1 yıl): {mc_var:.2%}")
    print(f"Monte Carlo CVaR (%95, 1 yıl): {mc_cvar:.2%}")