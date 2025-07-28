import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
import base64
from utils import get_today_str, read_csv_with_index
from visualizer import *
from pdf_generator import PDFReportGenerator
from pipeline.config import ALL_BENCHMARKS

# 配置
DATA_DIR = Path('source_data')
PROCESSED_DIR = Path('processed_data')
MARKET_DIR = DATA_DIR
HOLDINGS_DIR = Path('holdings')
DEFAULT_BENCHMARKS = ['QQQ', 'SPY', 'DIA']
#ALL_BENCHMARKS = ["SPY", "QQQ", "DIA", "IWM", "SMH", "AIQ", "BOTZ", "^GSPC", "^DJI", "^IXIC"]

st.set_page_config(page_title="AGIX Fund Analyzer (New)", layout="wide")

with st.sidebar:
    st.header("Control Panel")
    page = st.radio(
        "Select Page",
        ["📊 Fund Performance Comparison", "🔍 Portfolio Analysis", "📰 Market Sentiment Analysis"],
        index=0
    )
    st.divider()
    # 删除benchmarks多选
    # benchmarks = st.multiselect(
    #     "Select ETF/Index for Comparison (multiple selection allowed)",
    #     DEFAULT_BENCHMARKS,
    #     default=DEFAULT_BENCHMARKS[:3]
    # )
    today = datetime.today().date()
    start_date = st.date_input("Start Date", datetime(today.year, 1, 1))
    end_date = st.date_input("End Date", today)
    risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.0) / 100
    st.divider()
    st.subheader("📄 PDF Export Settings")
    export_pages = st.multiselect(
        "Select Pages to Export",
        ["Fund Performance Comparison", "Portfolio Analysis", "Market Sentiment Analysis"],
        default=["Fund Performance Comparison"]
    )
    export_btn = st.button("📊 Export to PDF")

# 数据加载
returns_df = pd.read_csv(PROCESSED_DIR / 'returns.csv')
risk_metrics = pd.read_csv(PROCESSED_DIR / 'risk_metrics.csv')
volume_analysis = pd.read_csv(PROCESSED_DIR / 'volume_analysis.csv')
closes = read_csv_with_index(MARKET_DIR / 'market_data_closes.csv')
volumes = read_csv_with_index(MARKET_DIR / 'market_data_volumes.csv')

# 只保留AGIX和Comparison ETF数据，并去除Weight和Type列
filter_types = ['AGIX', 'Comparison ETF']
returns_df = returns_df[returns_df['Type'].isin(filter_types)].drop(columns=['Weight', 'Type','Industry'], errors='ignore')
risk_metrics = risk_metrics[risk_metrics['Type'].isin(filter_types)].drop(columns=['Weight', 'Type'], errors='ignore')
volume_analysis = volume_analysis[volume_analysis['Type'].isin(filter_types)].drop(columns=['Weight', 'Type'], errors='ignore')

# 主页面逻辑
def main():
    # 第一页
    if page == "📊 Fund Performance Comparison":
        st.title("AGIX Fund Performance Analysis (New)")
        # 新增：全局benchmarks多选
        benchmarks = st.multiselect(
            "选择对比基准（只影响所有对比图）",
            ALL_BENCHMARKS,
            default=DEFAULT_BENCHMARKS
        )
        st.subheader("Comprehensive Fund Monitoring Tool")
        st.caption(f"Data last updated: {get_today_str()}")
        st.header(f"1. Return Analysis")
        returns_display = returns_df.copy()
        returns_display.set_index('Ticker', inplace=True)
        returns_display = returns_display.apply(lambda x: x * 100 if x.name in ['DTD', 'WTD', 'MTD', 'YTD', 'Since Launch'] else x)
        desired_order = ['AGIX', 'QQQ', 'SPY', 'DIA']
        ordered_rows = [idx for idx in desired_order if idx in returns_display.index] + [idx for idx in returns_display.index if idx not in desired_order]
        returns_display = returns_display.loc[ordered_rows]
        percent_cols = ['DTD', 'WTD', 'MTD', 'YTD', 'Since Launch']
        format_dict = {col: "{:.2f}%" for col in percent_cols if col in returns_display.columns}
        # 处理 NaN 值，避免样式化警告
        returns_display_clean = returns_display.fillna(0)
        st.dataframe(
            returns_display_clean.style.format(format_dict).bar(axis=0, color='#b7e4c7'),
            use_container_width=True
        )
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("AGIX vs Benchmarks")
            fig1 = plot_returns_comparison(returns_display, benchmarks)
            st.pyplot(fig1)
        with col2:
            st.subheader("Return Distribution")
            fig2 = plot_returns_distribution(returns_display)
            st.pyplot(fig2)
        st.subheader("Cumulative Return Since Listing")
    
        fig3 = plot_cumulative_returns(closes, benchmarks)
        st.pyplot(fig3)
        st.header("2. Risk Metrics")
        risk_display = risk_metrics.copy()
        risk_display.set_index('Ticker', inplace=True)
        risk_display['Annualized Return'] = risk_display['Annualized Return'] * 100
        risk_display['Annualized Volatility'] = risk_display['Annualized Volatility'] * 100
        risk_display['Max Drawdown'] = risk_display['Max Drawdown'] * 100
        # 新增：risk metrics排序
        desired_order = ['AGIX', 'QQQ', 'SPY', 'DIA']
        ordered_risk_rows = [idx for idx in desired_order if idx in risk_display.index] + [idx for idx in risk_display.index if idx not in desired_order]
        risk_display = risk_display.loc[ordered_risk_rows]
        # 去除Industry列
        if 'Industry' in risk_display.columns:
            risk_display = risk_display.drop(columns=['Industry'])
        st.dataframe(risk_display.style.format({
            'Annualized Return': '{:.2f}%','Annualized Volatility': '{:.2f}%','Sharpe Ratio': '{:.2f}','Max Drawdown': '{:.2f}%'}))
        st.subheader("Risk Metrics Visualization")
        fig4 = plot_risk_metrics(risk_display, benchmarks)
        st.pyplot(fig4)
        st.header("3. Volume Analysis")
        volume_display = volume_analysis.copy()
        volume_display.set_index('Ticker', inplace=True)
        volume_display['Avg Daily Volume'] = volume_display['Avg Daily Volume'].apply(lambda x: f"{x:,.0f}")
        volume_display['Avg Daily Change (%)'] = volume_display['Avg Daily Change (%)'].round(2)
        # 去除Industry列
        if 'Industry' in volume_display.columns:
            volume_display = volume_display.drop(columns=['Industry'])
        st.dataframe(volume_display.style.format({'Avg Daily Change (%)': '{:.2f}%'}))
        st.subheader("AGIX Volume Trend")
        # 添加平滑窗口选择
        volume_window = st.slider("Volume Smoothing Window", 1, 20, 5, help="选择移动平均窗口大小来平滑交易量数据")
        fig5 = plot_volume_trend(volumes, window=volume_window)
        st.pyplot(fig5)
        with st.expander("View Raw Data"):
            st.subheader("Closing Prices")
            st.dataframe(closes.tail(10))
            st.subheader("Trading Volumes")
            st.dataframe(volumes.tail(10))
    # 第二页
    elif page == "🔍 Portfolio Analysis":
        st.title("AGIX Fund Portfolio Analysis (New)")
        st.subheader("Asset Allocation & Holdings Breakdown")
        # 读取数据
        sector_df = pd.read_csv(PROCESSED_DIR / 'holdings_sectorAnalysis.csv')
        country_df = pd.read_csv(PROCESSED_DIR / 'holdings_countryAnalysis.csv')

        col1, col2 = st.columns(2)
        with col1:
            # 行业权重分布饼图
            st.markdown("#### Industry Weight Distribution")
            sector_group = sector_df.groupby('Industry')['Weight'].sum().sort_values(ascending=False)
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(4, 4))
            sector_group.plot.pie(autopct='%1.1f%%', ylabel='', title='Industry Weight Distribution', ax=ax)
            st.pyplot(fig)

        with col2:
            # 国家权重分布饼图
            st.markdown("#### Country Weight Distribution")
            country_group = country_df.groupby('Country')['Weight'].sum().sort_values(ascending=False)
            fig2, ax2 = plt.subplots(figsize=(4, 4))
            country_group.plot.pie(autopct='%1.1f%%', ylabel='', title='Country Weight Distribution', ax=ax2)
            st.pyplot(fig2)

        tab1, tab2 = st.tabs(["Sector Analysis", "Country Analysis"])
        with tab1:
            st.markdown("#### Sector Holdings Breakdown")
            sector_df_sorted = sector_df.sort_values(['Industry', 'Ticker']) if 'Industry' in sector_df.columns else sector_df
            st.dataframe(sector_df_sorted, use_container_width=True)
            
            # 行业贡献度分析
            metrics = ['DTD', 'WTD', 'MTD', 'YTD', 'Since Launch']
            # 筛选出真正的持仓股（权重不为空的）
            holdings_df = sector_df.dropna(subset=['Weight', 'Industry'])

            for metric in metrics:
                st.markdown(f"##### Industry Contribution to AGIX {metric}")
                
                # 特别处理 'Since Launch' 的命名不一致问题
                if metric == 'Since Launch':
                    contrib_col = 'SinceLaunch_contribution'
                else:
                    contrib_col = f'{metric}_contribution'
                
                # 确保必需的列存在
                if contrib_col in holdings_df.columns:
                    # 按行业分组，并计算总权重和总贡献
                    industry_contribution = holdings_df.groupby('Industry').agg(
                        Weight=('Weight', 'sum'),
                        Contribution=(contrib_col, 'sum')
                    ).reset_index()

                    # 按贡献度降序排序
                    industry_contribution = industry_contribution.sort_values('Contribution', ascending=False)
                    
                    # 格式化输出
                    st.dataframe(
                        industry_contribution.style.format({
                            "Weight": "{:.2%}",
                            "Contribution": "{:.4%}"
                        }),
                        use_container_width=True
                    )

                # 个股涨幅Top5
                if metric in sector_df.columns:
                    top5_rise = sector_df.sort_values(metric, ascending=False).head(5)[['Ticker', metric]]
                    rise_str = ',  '.join([f"{row['Ticker']}({row[metric]*100:.2f}%)" for _, row in top5_rise.iterrows()])
                    st.markdown(f"###### Top 5 Stocks by {metric} Return:  {rise_str}")
                # 个股上涨贡献Top5
                contrib_col = f'{metric}_contribution'
                if contrib_col in sector_df.columns:
                    top5_contrib = sector_df.sort_values(contrib_col, ascending=False).head(5)[['Ticker', contrib_col]]
                    contrib_str = ',  '.join([f"{row['Ticker']}({row[contrib_col]*100:.2f}%)" for _, row in top5_contrib.iterrows()])
                    st.markdown(f"###### Top 5 Stocks by {metric} Contribution:  {contrib_str}")
        with tab2:
            st.markdown("#### Country Holdings Breakdown")
            country_df_sorted = country_df.sort_values(['Country', 'Ticker']) if 'Country' in country_df.columns else country_df
            st.dataframe(country_df_sorted, use_container_width=True)
    # 第三页
    elif page == "📰 Market Sentiment Analysis":
        st.title("Market Sentiment Analysis (New)")
        st.subheader("News Sentiment & Market Mood")
        st.info("市场情绪分析功能请根据新pipeline数据结构补充实现！如需新闻、情感分析等，请补充数据处理和前端展示逻辑。")
    if export_btn:
        report = PDFReportGenerator()
        report.add_title("AGIX Fund Analysis Report")
        report.add_text(f"Report generated on: {get_today_str()}")
        report.add_text(f"Analysis period: {start_date} to {end_date}")
        report.add_text(f"Pages included: {', '.join(export_pages)}")
        if "Fund Performance Comparison" in export_pages:
            report.add_section_title("1. Fund Performance Analysis")
            returns_display = returns_df.copy().apply(lambda x: x * 100).round(2)
            report.add_dataframe(returns_display, "Return Comparison")
            fig1 = plot_returns_comparison(returns_display, benchmarks)
            report.add_image(fig1, "AGIX vs Benchmarks Return Comparison")
            fig2 = plot_returns_distribution(returns_df)
            report.add_image(fig2, "Return Distribution")
            fig3 = plot_cumulative_returns(closes, benchmarks)
            report.add_image(fig3, "Cumulative Return Since Listing")
            report.add_section_title("Risk Metrics")
            risk_display = risk_metrics.copy()
            risk_display['Annualized Return'] = risk_display['Annualized Return'] * 100
            risk_display['Annualized Volatility'] = risk_display['Annualized Volatility'] * 100
            risk_display['Max Drawdown'] = risk_display['Max Drawdown'] * 100
            risk_display_table = risk_display.copy()
            risk_display_table.columns = ['Annualized Return (%)', 'Annualized Volatility (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
            report.add_dataframe(risk_display_table, "Risk Metrics Comparison")
            fig4 = plot_risk_metrics(risk_display, benchmarks)
            report.add_image(fig4, "Risk Metrics Comparison")
            report.add_section_title("Volume Analysis")
            volume_display = volume_analysis.copy()
            volume_display.columns = ['Avg Daily Volume', 'Avg Daily Change (%)']
            report.add_dataframe(volume_display, "Volume Analysis")
        filename = f"AGIX_Report_{get_today_str()}.pdf"
        report.generate(filename)
        with open(filename, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("PDF report generated successfully!")

if __name__ == "__main__":
    main() 