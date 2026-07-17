# app.py - Portföy Optimizatörü

import streamlit as st
import pandas as pd

from src import config
from src.mean_variance import optimize_max_sharpe, get_frontier_points
from src.risk_parity import optimize_risk_parity
from src.risk_metrics import portfolio_returns, historical_var, historical_cvar
from src.backtest import run_backtest, backtest_performance_summary, get_benchmark_returns
from src.visualization import (
    plot_efficient_frontier, plot_backtest_comparison,
    plot_weights, plot_category_weights,
)
from src.data_loader import load_prices


st.set_page_config(page_title="MPT Portfolio Optimizer", layout="wide", page_icon="📊")

st.title("Portföy Optimizatörü")
st.markdown(f"""
{len(config.ALL_TICKERS)} varlıktan oluşan çok varlıklı bir evrende (BIST hisseleri,
ABD'nin önde gelen şirketleri, uluslararası ETF'ler, kripto paralar, altın/emtia)
Modern Portföy Teorisi çerçevesinde optimal ağırlıkları hesaplar. Markowitz ortalama-varyans
optimizasyonunu Risk Parity yaklaşımıyla karşılaştırır, sonuçları S&P 500 benchmark'ı ve
5 yıllık backtest ile değerlendirir.
""")
st.divider()

tab1, tab2 = st.tabs(["Önerilen Portföy", "Kendi Portföyünü Oluştur"])

# =================================================================
# SEKME 1: ÖNERİLEN PORTFÖY
# =================================================================
with tab1:
    st.sidebar.header("Kısıtlamalar")
    max_crypto = st.sidebar.slider("Maksimum Kripto Ağırlığı (%)", 0, 50, int(config.MAX_CRYPTO_WEIGHT * 100), key="mc1") / 100
    min_gold = st.sidebar.slider("Minimum Altın Ağırlığı (%)", 0, 30, int(config.MIN_GOLD_WEIGHT * 100), key="mg1") / 100

    st.sidebar.caption(
        "Bu kısıtlamalar yalnızca Max Sharpe portföyünü etkiler; "
        "Risk Parity kendi matematiği gereği bunlardan bağımsız çalışır."
    )

    prices = load_prices()
    st.caption(f"Veri aralığı: {prices.index.min().date()} — {prices.index.max().date()}  ·  {len(config.ALL_TICKERS)} varlık")

    with st.spinner("Optimal portföy hesaplanıyor..."):
        weights, (ret, vol, sharpe) = optimize_max_sharpe(prices, max_crypto, min_gold)
        rp_weights = optimize_risk_parity(prices)

    # -----------------------------------------------------------
    # 1. İKİ STRATEJİ
    # -----------------------------------------------------------
    st.header("1. İki Yatırım Yaklaşımı")

    col_desc1, col_desc2 = st.columns(2)
    with col_desc1:
        st.markdown("**Max Sharpe (Markowitz)**")
        st.caption(
            "Alınan her birim riske karşılık en yüksek getiriyi hedefler. "
            "Genellikle az sayıda varlığa yoğunlaşır; getiri potansiyeli yüksek, "
            "volatilite de buna paralel yüksektir."
        )
    with col_desc2:
        st.markdown("**Risk Parity**")
        st.caption(
            "Getiriyi hesaba katmaz; her varlığın portföy riskine katkısını eşitler. "
            "Sermayeyi geniş bir tabana dağıtır; volatilite düşük, getiri potansiyeli sınırlıdır."
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Max Sharpe Portföyü")
        m1, m2, m3 = st.columns(3)
        m1.metric("Getiri", f"{ret:.2%}")
        m2.metric("Volatilite", f"{vol:.2%}")
        m3.metric("Sharpe", f"{sharpe:.2f}")
        st.plotly_chart(plot_weights(weights, "Max Sharpe Ağırlıkları"), use_container_width=True)

    with col2:
        st.subheader("Risk Parity Portföyü")
        rp_returns = portfolio_returns(prices, rp_weights)
        rp_annual_return = rp_returns.mean() * 252
        rp_annual_vol = rp_returns.std() * (252 ** 0.5)
        rp_sharpe = (rp_annual_return - config.RISK_FREE_RATE) / rp_annual_vol
        m4, m5, m6 = st.columns(3)
        m4.metric("Getiri", f"{rp_annual_return:.2%}")
        m5.metric("Volatilite", f"{rp_annual_vol:.2%}")
        m6.metric("Sharpe", f"{rp_sharpe:.2f}")
        st.plotly_chart(plot_weights(rp_weights, "Risk Parity Ağırlıkları"), use_container_width=True)

    if sharpe > rp_sharpe:
        st.info(f"Bu senaryoda Max Sharpe, risk-ayarlı olarak daha verimli (Sharpe {sharpe:.2f} vs {rp_sharpe:.2f}), ancak daha yüksek volatilite (%{vol*100:.1f}) ile geliyor.")
    else:
        st.info(f"Bu senaryoda Risk Parity, risk-ayarlı olarak daha verimli (Sharpe {rp_sharpe:.2f} vs {sharpe:.2f}), daha düşük volatiliteyle.")

    st.subheader("Kategori Bazlı Dağılım")
    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        st.plotly_chart(plot_category_weights(weights, "Max Sharpe"), use_container_width=True)
    with col_cat2:
        st.plotly_chart(plot_category_weights(rp_weights, "Risk Parity"), use_container_width=True)

    st.divider()

    # -----------------------------------------------------------
    # 2. EFFICIENT FRONTIER
    # -----------------------------------------------------------
    st.header("2. Efficient Frontier")
    st.markdown("""
Eğri üzerindeki her nokta, belirli bir risk seviyesinde ulaşılabilecek en yüksek getiriyi
temsil eder. Eğrinin altında kalan hiçbir portföy verimli değildir. Kırmızı nokta, Sharpe
oranını maksimize eden portföyü — yani Max Sharpe Portföyünü — gösterir.
""")

    frontier_risk, frontier_return = get_frontier_points(prices, max_crypto=max_crypto, min_gold=min_gold)
    st.plotly_chart(plot_efficient_frontier(frontier_risk, frontier_return, vol, ret), use_container_width=True)

    st.divider()

    # -----------------------------------------------------------
    # 3. RİSK METRİKLERİ
    # -----------------------------------------------------------
    st.header("3. Risk Metrikleri")
    st.caption("Max Sharpe Portföyü için hesaplanmıştır.")

    port_returns = portfolio_returns(prices, weights)
    var_95 = historical_var(port_returns, 0.95)
    cvar_95 = historical_cvar(port_returns, 0.95)

    col3, col4 = st.columns(2)
    with col3:
        st.metric("Tarihsel VaR (%95, günlük)", f"{var_95:.2%}")
        st.caption(f"100 günün 95'inde günlük kaybın %{var_95*100:.2f}'yi geçmeyeceği beklenir.")
    with col4:
        st.metric("Tarihsel CVaR (%95, günlük)", f"{cvar_95:.2%}")
        st.caption(f"En kötü %5'lik günlerde ortalama kayıp %{cvar_95*100:.2f}'dir.")

    st.divider()

    # -----------------------------------------------------------
    # 4. BACKTEST
    # -----------------------------------------------------------
    st.header("4. 5 Yıllık Backtest")
    st.markdown("""
Portföy her ay yeniden dengelenir (rebalancing). SPY (Benchmark) çizgisi, sadece
S&P 500 endeksine yatırım yapılsaydı elde edilecek sonucu gösterir. Maksimum Drawdown,
portföyün tepe noktasından en fazla ne kadar düştüğünü belirtir.
""")

    if st.button("Backtest Çalıştır", key="backtest1", type="primary"):
        with st.spinner("Backtest yürütülüyor..."):
            history_sharpe = run_backtest(prices, strategy="max_sharpe", max_crypto=max_crypto, min_gold=min_gold)
            history_rp = run_backtest(prices, strategy="risk_parity")
            history_benchmark = get_benchmark_returns(prices, benchmark="SPY")

        fig = plot_backtest_comparison({
            "Max Sharpe": history_sharpe,
            "Risk Parity": history_rp,
            "SPY (Benchmark)": history_benchmark,
        })
        st.plotly_chart(fig, use_container_width=True)

        summary_sharpe = backtest_performance_summary(history_sharpe)
        summary_rp = backtest_performance_summary(history_rp)
        summary_bench = backtest_performance_summary(history_benchmark)

        comparison_df = pd.DataFrame({
            "Max Sharpe": summary_sharpe,
            "Risk Parity": summary_rp,
            "SPY (Benchmark)": summary_bench,
        }).T
        comparison_df.columns = ["Toplam Getiri", "Yıllık Getiri", "Yıllık Volatilite", "Sharpe Oranı", "Maks. Drawdown"]
        for col in comparison_df.columns:
            comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.2%}" if "Oranı" not in col else f"{x:.2f}")

        st.dataframe(comparison_df, use_container_width=True)

        sharpe_beat_spy = summary_sharpe["total_return"] > summary_bench["total_return"]
        rp_beat_spy = summary_rp["total_return"] > summary_bench["total_return"]

        if sharpe_beat_spy or rp_beat_spy:
            winners = [w for w, beat in [("Max Sharpe", sharpe_beat_spy), ("Risk Parity", rp_beat_spy)] if beat]
            st.success(f"{' ve '.join(winners)} stratejisi, SPY'a yatırım yapmaktan daha fazla getiri sağladı.")
        else:
            st.warning("Bu dönemde hiçbir strateji SPY'ı geçemedi.")

        sharpe_scores = {
            "Max Sharpe": summary_sharpe["sharpe_ratio"],
            "Risk Parity": summary_rp["sharpe_ratio"],
            "SPY (Benchmark)": summary_bench["sharpe_ratio"],
        }
        best_strategy = max(sharpe_scores, key=sharpe_scores.get)

        st.info(
            f"Risk-ayarlı olarak en iyi performans: **{best_strategy}** "
            f"(Sharpe oranı: {sharpe_scores[best_strategy]:.2f}). "
            f"Sharpe oranı, elde edilen getirinin alınan riske göre ne kadar verimli olduğunu gösterir."
        )

# =================================================================
# SEKME 2: KENDİ PORTFÖYÜNÜ OLUŞTUR
# =================================================================
with tab2:
    st.header("Kendi Portföyünü Oluştur")
    st.markdown("Yatırım yapmak istediğin varlıkları seç; model yalnızca bu varlıklarla en iyi portföyü hesaplar.")

    st.subheader("1. Varlıklarını Seç")

    ctab1, ctab2, ctab3, ctab4, ctab5 = st.tabs(["BIST Hisseleri", "ETF'ler", "ABD Hisseleri", "Kripto", "Altın/Emtia"])

    with ctab1:
        selected_bist = st.multiselect("BIST Hisseleri", config.BIST_TICKERS, default=config.BIST_TICKERS, key="bist2")
    with ctab2:
        selected_etf = st.multiselect("Uluslararası ETF'ler", config.ETF_TICKERS, default=config.ETF_TICKERS, key="etf2")
    with ctab3:
        selected_us = st.multiselect("ABD Hisseleri", config.US_STOCK_TICKERS, default=config.US_STOCK_TICKERS, key="us2")
    with ctab4:
        selected_crypto = st.multiselect("Kripto Paralar", config.CRYPTO_TICKERS, default=[], key="crypto2")
    with ctab5:
        selected_gold = st.multiselect("Altın/Emtia", config.GOLD_TICKERS, default=config.GOLD_TICKERS, key="gold2")

    selected_assets = selected_bist + selected_etf + selected_us + selected_crypto + selected_gold

    st.metric("Seçilen Varlık Sayısı", len(selected_assets))

    if len(selected_assets) < 5:
        st.warning("Anlamlı bir optimizasyon için en az 5 varlık seçin.")
    else:
        st.subheader("2. Kısıtlarını Belirle (opsiyonel)")

        max_crypto2 = 0.0
        min_gold2 = 0.0

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            if len(selected_crypto) > 0:
                max_crypto2 = st.slider("Maksimum Kripto Ağırlığı (%)", 0, 100, 30, key="mc2") / 100
        with col_k2:
            if len(selected_gold) > 0:
                min_gold2 = st.slider("Minimum Altın Ağırlığı (%)", 0, 50, 0, key="mg2") / 100

        prices2 = load_prices()[selected_assets]

        with st.spinner("Portföy hesaplanıyor..."):
            weights2, (ret2, vol2, sharpe2) = optimize_max_sharpe(prices2, max_crypto2, min_gold2)
            rp_weights2 = optimize_risk_parity(prices2)

        st.subheader("3. Sonuçlar")

        col1b, col2b = st.columns(2)

        with col1b:
            st.markdown("**Max Sharpe Portföyü**")
            mb1, mb2, mb3 = st.columns(3)
            mb1.metric("Getiri", f"{ret2:.2%}")
            mb2.metric("Volatilite", f"{vol2:.2%}")
            mb3.metric("Sharpe", f"{sharpe2:.2f}")
            st.plotly_chart(plot_weights(weights2, "Max Sharpe Portföyün"), use_container_width=True)

        with col2b:
            st.markdown("**Risk Parity Portföyü**")
            rp_returns2 = portfolio_returns(prices2, rp_weights2)
            rp_annual_return2 = rp_returns2.mean() * 252
            rp_annual_vol2 = rp_returns2.std() * (252 ** 0.5)
            rp_sharpe2 = (rp_annual_return2 - config.RISK_FREE_RATE) / rp_annual_vol2
            mb4, mb5, mb6 = st.columns(3)
            mb4.metric("Getiri", f"{rp_annual_return2:.2%}")
            mb5.metric("Volatilite", f"{rp_annual_vol2:.2%}")
            mb6.metric("Sharpe", f"{rp_sharpe2:.2f}")
            st.plotly_chart(plot_weights(rp_weights2, "Risk Parity Portföyün"), use_container_width=True)

        st.subheader("4. Efficient Frontier")
        frontier_risk2, frontier_return2 = get_frontier_points(prices2, max_crypto=max_crypto2, min_gold=min_gold2)
        st.plotly_chart(plot_efficient_frontier(frontier_risk2, frontier_return2, vol2, ret2), use_container_width=True)

        st.subheader("5. Backtest: SPY'a Karşı")

        if st.button("Backtest Çalıştır", key="backtest2", type="primary"):
            with st.spinner("Backtest yürütülüyor..."):
                history_sharpe2 = run_backtest(prices2, strategy="max_sharpe", max_crypto=max_crypto2, min_gold=min_gold2)
                history_rp2 = run_backtest(prices2, strategy="risk_parity")
                history_benchmark2 = get_benchmark_returns(prices2, benchmark="SPY")

            fig2 = plot_backtest_comparison({
                "Max Sharpe": history_sharpe2,
                "Risk Parity": history_rp2,
                "SPY (Benchmark)": history_benchmark2,
            })
            st.plotly_chart(fig2, use_container_width=True)

            summary_sharpe2 = backtest_performance_summary(history_sharpe2)
            summary_rp2 = backtest_performance_summary(history_rp2)
            summary_bench2 = backtest_performance_summary(history_benchmark2)

            comparison_df2 = pd.DataFrame({
                "Max Sharpe": summary_sharpe2,
                "Risk Parity": summary_rp2,
                "SPY (Benchmark)": summary_bench2,
            }).T
            comparison_df2.columns = ["Toplam Getiri", "Yıllık Getiri", "Yıllık Volatilite", "Sharpe Oranı", "Maks. Drawdown"]
            for col in comparison_df2.columns:
                comparison_df2[col] = comparison_df2[col].apply(lambda x: f"{x:.2%}" if "Oranı" not in col else f"{x:.2f}")

            st.dataframe(comparison_df2, use_container_width=True)

            sharpe_beat_spy2 = summary_sharpe2["total_return"] > summary_bench2["total_return"]
            rp_beat_spy2 = summary_rp2["total_return"] > summary_bench2["total_return"]

            if sharpe_beat_spy2 or rp_beat_spy2:
                winners2 = [w for w, beat in [("Max Sharpe", sharpe_beat_spy2), ("Risk Parity", rp_beat_spy2)] if beat]
                st.success(f"{' ve '.join(winners2)} portföyün, SPY'a yatırım yapmaktan daha fazla getiri sağladı.")
            else:
                st.warning("Bu seçimle hiçbir strateji SPY'ı geçemedi.")