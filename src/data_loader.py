# data_loader.py - İşlenmiş fiyat verisini yükler

import pandas as pd
from src.config import PROCESSED_PATH


def load_prices():
    """USD normalize edilmiş, temizlenmiş fiyat verisini yükler."""
    return pd.read_csv(PROCESSED_PATH, index_col=0, parse_dates=True)


def get_returns(prices):
    """Günlük yüzde getiri serisini hesaplar."""
    return prices.pct_change().dropna()