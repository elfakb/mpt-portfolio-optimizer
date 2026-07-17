"""
1-verileri yfinance üzerinden çekiyoruz 
2-Türk hisse senetlerinin verilerini o anlık dolar kuru üzerinden dolara çeviriyoruz karışıklık olmasın diye 

"""
import sys, os
import pandas as pd
import yfinance as yf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.config import ALL_TICKERS, BIST_TICKERS, FX_TICKER, START_DATE, END_DATE, RAW_PATH, PROCESSED_PATH
# bu config dosyasında istediğiniz hisseleri fonalrı ekleyebilrisiniz öenmli olan bu dosyayı çalıştırmadan önce eklenmesi 

def download_close_prices(tickers, start, end):
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    return data["Close"] # tüm kapanış fiyatlarını indiririz


def main():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # kapanış fiyatlarını indirip raw klasörünün altına csv olarak kaydederiz
    prices = download_close_prices(ALL_TICKERS, START_DATE, END_DATE)
    prices.to_csv(RAW_PATH)

    # USDTRY kurunu indiriyoruz o anki 
    fx = download_close_prices([FX_TICKER], START_DATE, END_DATE)
    if isinstance(fx, pd.DataFrame):
        fx = fx[FX_TICKER]  

    # tüm bist 30 hisselerini o anki kur ile dolara çeviriyoruz
    for ticker in BIST_TICKERS:
        prices[ticker] = prices[ticker] / fx

    # eksik verielri frontfill ve beforefill ile doldururuz
    prices = prices.ffill().bfill()

    # verileri yeni csv dosyanına kaydederiz
    prices.to_csv(PROCESSED_PATH)
    print(f"Bitti: {prices.shape[0]} gün, {prices.shape[1]} varlık -> {PROCESSED_PATH}")


if __name__ == "__main__":
    main()