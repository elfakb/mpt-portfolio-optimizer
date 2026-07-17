# 🧮 MPT Portfolio Optimizer

30 varlıktan oluşan bir portföyü (BIST hisseleri, uluslararası ETF'ler, kripto paralar,
altın/emtia) Modern Portföy Teorisi (Markowitz) ve Risk Parity yaklaşımlarıyla optimize
eden, sonuçları 5 yıllık backtest ile test eden interaktif bir araç.

**[Canlı Demo](#)** ← deploy linkini buraya ekleyeceğiz

![Efficient Frontier](docs/screenshot.png) ← ekran görüntüsü eklenebilir

---

## 🎯 Bu Proje Ne Yapıyor?

- 30 varlığın **Efficient Frontier**'ını (etkin sınır) hesaplar ve görselleştirir
- **Sharpe oranını maksimize** eden optimal portföy ağırlıklarını bulur
- Aynı varlıklarla **Risk Parity** stratejisini uygular ve karşılaştırır
- Gerçekçi kısıtlar uygular: maksimum %30 kripto, minimum %10 altın
- **5 yıllık backtest** ile "bu strateji gerçekte ne kazandırırdı" sorusuna cevap verir
- Sonuçları **S&P 500 (SPY) benchmark'ı** ile kıyaslar
- **VaR / CVaR** risk metriklerini hesaplar
- Kullanıcının **kendi varlık seçimiyle** özel portföy oluşturmasına izin verir

---

## 📊 Matematiksel Arka Plan

### 1. Markowitz Mean-Variance Optimizasyonu

Modern Portföy Teorisi'nin temel fikri: bir portföyün beklenen getirisi, içindeki
varlıkların ağırlıklı ortalamasıdır:

```
E(Rp) = Σ wi · E(Ri)
```

Ama portföyün riski (varyansı) sadece varlıkların ayrı ayrı riskine değil,
**birbirleriyle olan korelasyonlarına** da bağlıdır:

```
σp² = Σ Σ wi · wj · σij
```

Burada `σij` varlık i ve j arasındaki kovaryanstır. Bu formül şunu gösterir:
düşük veya negatif korelasyonlu varlıkları bir araya getirmek, bireysel risklerin
toplamından **daha düşük** bir portföy riski üretebilir — çeşitlendirmenin
matematiksel temeli budur.

**Optimizasyon problemi**: Belirli bir risk seviyesinde getiriyi maksimize etmek
(ya da tersi), bir quadratic programming (QP) problemidir:

```
maksimize:  w^T μ - (λ/2) w^T Σ w
kısıt:      Σ wi = 1,  wi ≥ 0 (long-only)
```

Burada `λ` risk toleransını temsil eder. Bu projede PyPortfolioOpt kütüphanesi
bu QP problemini `cvxpy` altyapısıyla çözüyor.

### 2. Sharpe Oranı Maksimizasyonu

Sharpe oranı, alınan her birim riske karşılık elde edilen "fazla" getiriyi ölçer:

```
Sharpe = (E(Rp) - Rf) / σp
```

Sharpe'ı maksimize eden portföy, Efficient Frontier üzerinde risksiz getiri
noktasından çizilen teğet doğrunun değdiği noktadır (Tangency Portfolio).
Bu proje `MAX_CRYPTO_WEIGHT` ve `MIN_GOLD_WEIGHT` gibi ek doğrusal kısıtlarla
bu optimizasyonu gerçekçi sınırlar içinde çalıştırır.

### 3. Risk Parity

Markowitz optimizasyonu getiriyi merkeze koyar, bu da genelde az sayıda varlığa
yoğunlaşan (konsantre) portföyler üretir. Risk Parity farklı bir felsefe önerir:
**her varlığın portföy riskine katkısı eşit olsun.**

Varlık `i`'nin marjinal risk katkısı:

```
RCi = wi · (Σw)i / σp
```

Risk Parity, tüm `RCi` değerlerini birbirine eşitlemeye çalışan bir optimizasyon
problemidir. Bu projede `scipy.optimize.minimize` (SLSQP metodu) ile çözülüyor,
çünkü PyPortfolioOpt'un hazır bir risk parity modülü yok.

### 4. VaR ve CVaR

**VaR (Value at Risk)**: belirli bir güven aralığında (%95) beklenen maksimum kayıp.
Tarihsel yöntemde, günlük getiri dağılımının ilgili yüzdelik dilimine bakılır.

**CVaR (Conditional VaR / Expected Shortfall)**: VaR'ı aşan senaryolarda
ortalama kaybı gösterir — VaR'ın "kuyruk riskini" görmezden gelme sorununu çözer.

Bu projede hem tarihsel hem de Monte Carlo simülasyonuna dayalı VaR/CVaR hesaplanıyor.

---

## 🗂️ Proje Yapısı

```
mpt-portfolio-optimizer/
├── app.py                  # Streamlit arayüzü (iki sekme: önerilen + özel portföy)
├── data/
│   ├── fetch_data.py       # yfinance'ten veri çeker, USD'ye normalize eder
│   ├── raw/                # Ham fiyat verisi
│   └── processed/          # Temizlenmiş, USD normalize veri
├── src/
│   ├── config.py           # Varlık listesi, kısıtlar, tarih aralığı
│   ├── data_loader.py       # Veri yükleme yardımcı fonksiyonları
│   ├── mean_variance.py     # Markowitz optimizasyonu
│   ├── risk_parity.py       # Risk Parity optimizasyonu
│   ├── risk_metrics.py      # VaR, CVaR, Monte Carlo
│   ├── backtest.py          # 5 yıllık backtest + rebalancing
│   └── visualization.py     # Plotly grafik fonksiyonları
└── requirements.txt
```

---

## 🚀 Kurulum ve Çalıştırma

```bash
git clone <repo-url>
cd mpt-portfolio-optimizer

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

python data/fetch_data.py     # Veriyi indir (30 varlık, ~5 yıl)

streamlit run app.py
```

---

## 📈 Örnek Sonuçlar (Son 5 Yıl Backtest)

| Strateji | Toplam Getiri | Yıllık Getiri | Yıllık Volatilite | Sharpe | Maks. Drawdown |
|---|---|---|---|---|---|
| Max Sharpe | 408.14% | 26.09% | 24.46% | ~1.07 | -27.80% |
| Risk Parity | 101.14% | 10.48% | 11.31% | ~0.72 | -19.65% |
| SPY (Benchmark) | 84.06% | 8.79% | 14.24% | - | -24.50% |

**Not:** Bu sonuçlar geçmiş veriye (backtest) dayanır ve gelecekteki performansı
garanti etmez. 2021-2026 dönemi özellikle teknoloji ve kripto varlıklar için
güçlü bir yükseliş dönemiydi; farklı bir dönemde sonuçlar önemli ölçüde
değişebilir.

---

## ⚠️ Sınırlamalar

- Beklenen getiriler **geçmiş ortalamalara** dayanıyor (`mean_historical_return`) —
  bu, gelecekteki getirilerin geçmişe benzeyeceği varsayımını taşır ve genellikle
  Markowitz optimizasyonunun en tartışmalı noktasıdır (Black-Litterman modeli bu
  sorunu piyasa dengesi + öznel görüşlerle hafifletmeyi amaçlar — bu projenin
  ikinci fazında ele alınacaktır)
- İşlem maliyeti (transaction cost) ve vergi etkisi backtest'e dahil edilmemiştir
- Kripto varlıklar 7/24 işlem görürken BIST/ABD borsaları belirli saatlerde
  işlem görüyor; bu farkı hizalamak için forward-fill kullanıldı, bu basit bir
  yaklaşımdır

---

## 🛠️ Kullanılan Teknolojiler

`Python` · `PyPortfolioOpt` · `cvxpy` · `scipy` · `pandas` · `NumPy` · `yfinance` ·
`Plotly` · `Streamlit`
```

---

Bu README'de birkaç yer bilinçli olarak "boşluk" bıraktım:
- `[Canlı Demo](#)` — deploy linkini yapıştıracağız
- `docs/screenshot.png` — istersen en güzel ekran görüntünü (backtest grafiği gibi) `docs/` klasörüne koyup buraya bağlayabiliriz

Deploy'a geçelim mi, yoksa README'de değiştirmek/eklemek istediğin bir şey var mı?