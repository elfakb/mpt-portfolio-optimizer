from datetime import datetime, timedelta


BIST_TICKERS = [
    "GARAN.IS", "AKBNK.IS", "YKBNK.IS", "ISCTR.IS", "HALKB.IS", "VAKBN.IS",   # Bankacılık
    "KCHOL.IS", "SAHOL.IS", "DOAS.IS",                                        # Holding
    "TUPRS.IS", "PETKM.IS",                                                   # Enerji/Petrol
    "SASA.IS", "EREGL.IS", "SISE.IS", "GUBRF.IS",                             # Sanayi/Kimya
    "ASELS.IS", "LOGO.IS",                                                    # Savunma/Teknoloji
    "THYAO.IS", "PGSUS.IS",                                                   # Havacılık/Ulaştırma
    "FROTO.IS", "TOASO.IS",                                                   # Otomotiv
    "BIMAS.IS", "MGROS.IS",                                                   # Perakende/Tüketim
    "TCELL.IS",                                                               # Telekom
    "ARCLK.IS",                                                               # Beyaz Eşya
    "ENKAI.IS",                                                               # İnşaat                                                              # Madencilik
    "ENJSA.IS",                                                               # Elektrik/Enerji
    "TAVHL.IS",                                                               # Havalimanı Hizmetleri
]

ETF_TICKERS = ["SPY", "QQQ", "EFA", "EEM", "AGG", "TLT", "VNQ", "XLE", "XLK"]

US_STOCK_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "NVDA",     # Teknoloji
    "AMZN", "WMT",                       # E-ticaret/Tüketim
    "JPM", "V", "MA",                    # Finans
    "JNJ", "UNH", "LLY",                 # Sağlık
    "XOM", "CVX",                        # Enerji
    "CAT", "BA",                         # Sanayi
    "KO", "PG",                          # Tüketim Malları
    "META", "DIS",                       # Medya/İletişim
]

CRYPTO_TICKERS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]

GOLD_TICKERS = ["GC=F", "GLD", "SLV", "PDBC"]

ALL_TICKERS = BIST_TICKERS + ETF_TICKERS + US_STOCK_TICKERS + CRYPTO_TICKERS + GOLD_TICKERS


FX_TICKER = "USDTRY=X"



END_DATE = datetime.today().strftime("%Y-%m-%d")
START_DATE = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")

# KISITLAR

MAX_CRYPTO_WEIGHT = 0.30
MIN_GOLD_WEIGHT = 0.10
RISK_FREE_RATE = 0.04



REBALANCE_FREQUENCY = "ME"  # Aylık


RAW_PATH = "data/raw/prices_raw.csv"
PROCESSED_PATH = "data/processed/prices_usd.csv"