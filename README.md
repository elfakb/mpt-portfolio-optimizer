

# MPT Portföy Optimizatörü

BIST hisseleri, ABD'nin büyük şirketleri, uluslararası ETF'ler, kripto paralar ve
altın/emtia dahil 66 varlık üzerinde, Modern Portföy Teorisi (Markowitz) ve Risk Parity
temelli interaktif bir portföy optimizasyon aracı.

Uygulama iki modda çalışır:

**1. Önerilen Portföy** — 66 varlıklık tam evreni kullanır. Kullanıcı iki kısıtı (maks.
kripto ağırlığı, min. altın ağırlığı) slider'larla belirler; uygulama Max Sharpe ve Risk
Parity portföylerini hesaplar, Efficient Frontier'ı çizer, risk metriklerini hesaplar ve
S&P 500'e karşı 5 yıllık bir backtest çalıştırır.

**2. Kendi Portföyünü Oluştur** — kullanıcı hangi varlıkların dahil edileceğini seçer
(BIST hisseleri, ABD hisseleri, ETF'ler, kripto, altından herhangi bir alt küme), kendi
kısıtlarını belirler; uygulama aynı tam süreci — optimizasyon, Efficient Frontier, backtest —
yalnızca bu özel seçim üzerinde çalıştırır.

## Demo


https://github.com/user-attachments/assets/334abdef-1796-4749-aa26-1f65a9dfb8dc



https://github.com/user-attachments/assets/509ab25b-f4d2-4052-af69-6e5518c61f0e


## Proje İçeriği

- Efficient Frontier'ı hesaplar, Sharpe oranını maksimize eden portföyü bulur
- Aynı varlık evreninde Risk Parity stratejisini uygular ve Markowitz ile karşılaştırır
- Gerçekçi kısıtlar uygular (maks. kripto ağırlığı, min. altın ağırlığı gibi)
- Aylık rebalancing ile 5 yıllık backtest çalıştırır, S&P 500 ile kıyaslar
- VaR / CVaR risk metriklerini hesaplar

---

## Projenin Matematiksel Yönü

**Markowitz Ortalama-Varyans Optimizasyonu.** Portföy getirisi, varlık getirilerinin
ağırlıklı ortalamasıdır; portföy riski ise sadece bireysel volatiliteye değil, varlıkların
birlikte hareket etme biçimine bağlıdır:

```
E(Rp) = Σ wi · E(Ri)
σp²   = Σ Σ wi · wj · σij
```

Çeşitlendirmenin matematiksel temeli budur; optimizasyon PyPortfolioOpt / `cvxpy` ile
çözülen bir quadratic programming problemidir.

**Sharpe Oranı Maksimizasyonu.**

```
Sharpe = (E(Rp) - Rf) / σp
```

Sharpe'ı maksimize eden portföy, risksiz getiri ile Efficient Frontier arasındaki teğet
noktadır; bu projede ek kısıtlar altında çözülür.

**Risk Parity.** Getiriyi optimize etmek yerine, her varlığın portföy riskine marjinal
katkısı eşitlenir:

```
RCi = wi · (Σw)i / σp
```

`scipy.optimize.minimize` (SLSQP) ile çözülür.

**VaR & CVaR.** VaR, tarihsel getiri dağılımına dayanarak %95 güven aralığında beklenen
maksimum kaybı gösterir. CVaR (Expected Shortfall), VaR'ı aşan senaryolardaki ortalama kaybı yakalar.

---

## Proje Yapısı

```
mpt-portfolio-optimizer/
├── app.py                  # Streamlit arayüzü (önerilen + özel portföy)
├── data/
│   ├── fetch_data.py       # yfinance'ten veri çeker, USD'ye normalize eder
│   ├── raw/
│   └── processed/
├── src/
│   ├── config.py            # Varlık evreni, kısıtlar, tarih aralığı
│   ├── data_loader.py
│   ├── mean_variance.py     # Markowitz optimizasyonu
│   ├── risk_parity.py       # Risk Parity optimizasyonu
│   ├── risk_metrics.py      # VaR, CVaR
│   ├── backtest.py          # Backtest ve rebalancing
│   └── visualization.py     # Plotly grafikleri
└── requirements.txt
```

---

## Kurulum

```bash
git clone https://github.com/elfakb/mpt-portfolio-optimizer.git
cd mpt-portfolio-optimizer

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

python data/fetch_data.py
streamlit run app.py
```

---

## Örnek Backtest Sonuçları (5 Yıl)

| Strateji | Toplam Getiri | Yıllık Getiri | Yıllık Volatilite | Sharpe | Maks. Drawdown |
|---|---|---|---|---|---|
| Max Sharpe | 408.14% | 26.09% | 24.46% | 1.07 | -27.80% |
| Risk Parity | 101.14% | 10.48% | 11.31% | 0.72 | -19.65% |
| SPY (Benchmark) | 84.06% | 8.79% | 14.24% | – | -24.50% |

---

## Kullanılan Teknolojiler

Python · PyPortfolioOpt · cvxpy · scipy · pandas · NumPy · yfinance · Plotly · Streamlit


---

# MPT Portfolio Optimizer

An interactive portfolio optimization tool based on Modern Portfolio Theory (Markowitz)
and Risk Parity, covering 66 assets across BIST stocks, major US companies, international
ETFs, cryptocurrencies, and gold/commodities.

The app runs in two modes:

**1. Suggested Portfolio** — uses the full 66-asset universe. The user sets two constraints
(max crypto weight, min gold weight) via sliders; the app computes the Max Sharpe and Risk
Parity portfolios, plots the Efficient Frontier, calculates risk metrics, and runs a 5-year
backtest against the S&P 500.

**2. Build Your Own Portfolio** — the user selects which assets to include (any subset of
BIST stocks, US stocks, ETFs, crypto, gold), sets their own constraints, and the app runs
the same full pipeline — optimization, Efficient Frontier, backtest — on that custom
selection only.


---

## Overview

- Computes the Efficient Frontier and finds the Sharpe-maximizing portfolio
- Implements Risk Parity on the same asset universe and compares it to Markowitz
- Applies realistic constraints (e.g. max crypto weight, min gold weight)
- Runs a 5-year backtest with monthly rebalancing, benchmarked against the S&P 500
- Computes VaR / CVaR risk metrics

---

## Mathematical Background

**Markowitz Mean-Variance Optimization.** Portfolio return is a weighted average of asset
returns; portfolio risk depends on how assets co-move, not just their individual volatility:

```
E(Rp) = Σ wi · E(Ri)
σp²   = Σ Σ wi · wj · σij
```

This is the basis for diversification and is solved as a quadratic programming problem
via PyPortfolioOpt / `cvxpy`.

**Sharpe Ratio Maximization.**

```
Sharpe = (E(Rp) - Rf) / σp
```

The Sharpe-maximizing portfolio is the tangency point between the risk-free rate and the
Efficient Frontier, solved here under additional constraints.

**Risk Parity.** Instead of optimizing for return, each asset's marginal contribution to
portfolio risk is equalized:

```
RCi = wi · (Σw)i / σp
```

Solved via `scipy.optimize.minimize` (SLSQP).

**VaR & CVaR.** VaR estimates the maximum expected loss at a 95% confidence level from the
historical return distribution. CVaR (Expected Shortfall) captures the average loss in the
scenarios that exceed VaR.

---

## Project Structure

```
mpt-portfolio-optimizer/
├── app.py                  # Streamlit UI (suggested + custom portfolio)
├── data/
│   ├── fetch_data.py       # Downloads and USD-normalizes data via yfinance
│   ├── raw/
│   └── processed/
├── src/
│   ├── config.py            # Asset universe, constraints, date range
│   ├── data_loader.py
│   ├── mean_variance.py     # Markowitz optimization
│   ├── risk_parity.py       # Risk Parity optimization
│   ├── risk_metrics.py      # VaR, CVaR
│   ├── backtest.py          # Backtest and rebalancing
│   └── visualization.py     # Plotly charts
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/elfakb/mpt-portfolio-optimizer.git
cd mpt-portfolio-optimizer

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

python data/fetch_data.py
streamlit run app.py
```

---

## Sample Backtest Results (5-Year)

| Strategy | Total Return | Annual Return | Annual Volatility | Sharpe | Max Drawdown |
|---|---|---|---|---|---|
| Max Sharpe | 408.14% | 26.09% | 24.46% | 1.07 | -27.80% |
| Risk Parity | 101.14% | 10.48% | 11.31% | 0.72 | -19.65% |
| SPY (Benchmark) | 84.06% | 8.79% | 14.24% | – | -24.50% |

---

## Tech Stack

Python · PyPortfolioOpt · cvxpy · scipy · pandas · NumPy · yfinance · Plotly · Streamlit
