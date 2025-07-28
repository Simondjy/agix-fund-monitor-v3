import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, HOLDINGS_DIR, ALL_BENCHMARKS, TICKER_TO_INDUSTRY

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def calculate_returns(df):
    results = pd.DataFrame(index=df.columns)
    today = df.index[-1]
    def get_prev_biz_day(date):
        while date not in df.index:
            date -= timedelta(days=1)
        return date
    results['DTD'] = df.pct_change().iloc[-1]
    week_start = today - timedelta(days=today.weekday())
    week_start = get_prev_biz_day(week_start)
    results['WTD'] = (df.iloc[-1] / df.loc[week_start]) - 1
    month_start = today.replace(day=1)
    month_start = get_prev_biz_day(month_start)
    results['MTD'] = (df.iloc[-1] / df.loc[month_start]) - 1
    year_start = today.replace(month=1, day=1)
    year_start = get_prev_biz_day(year_start)
    results['YTD'] = (df.iloc[-1] / df.loc[year_start]) - 1
    # --- 修改since launch逻辑 ---
    agix_first_date = df['AGIX'].first_valid_index() if 'AGIX' in df.columns else df.index[0]
    since_launch = []
    for col in df.columns:
        # 该ticker在AGIX首日有数据
        if agix_first_date in df.index and not pd.isna(df.loc[agix_first_date, col]):
            base_date = agix_first_date
        else:
            # 用该ticker自己的首日
            base_date = df[col].first_valid_index()
        since_launch.append((df[col].iloc[-1] / df.loc[base_date, col]) - 1)
    results['Since Launch'] = since_launch
    # --- 结束 ---
    return results

def calculate_risk_metrics(df, risk_free_rate=0.02):
    returns = df.pct_change().dropna()
    annualized_return = returns.mean() * 252
    annualized_volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    cumulative_returns = (1 + returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    return pd.DataFrame({
        'Annualized Return': annualized_return,
        'Annualized Volatility': annualized_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown
    })

def analyze_volume(volumes):
    volume_changes = volumes.pct_change().mean() * 100
    return pd.DataFrame({
        'Avg Daily Volume': volumes.mean(),
        'Avg Daily Change (%)': volume_changes
    })

# 增加类型标记函数

def add_type_column(df, holdings_tickers, comparison_etfs):
    def get_type(ticker):
        if ticker in holdings_tickers:
            return 'Holding'
        elif ticker in comparison_etfs:
            return 'Comparison ETF'
        elif ticker == 'AGIX':
            return 'AGIX'
        else:
            return 'Other'
    df_type = pd.DataFrame({'Ticker': df.columns})
    df_type['Type'] = df_type['Ticker'].apply(get_type)
    return df_type

# 增加Industry标记函数

def add_industry_column(df):
    df_industry = pd.DataFrame({'Ticker': df.columns})
    df_industry['Industry'] = df_industry['Ticker'].apply(lambda x: TICKER_TO_INDUSTRY.get(x))
    return df_industry

# 增加Country标记函数

def add_country_column(df):
    info_path = Path(__file__).parent.parent / 'source_data' / 'holdings_info.csv'
    if not info_path.exists():
        raise FileNotFoundError(f"{info_path} 不存在，请先生成 holdings_info.csv")
    info_df = pd.read_csv(info_path, dtype={'Ticker': str})
    country_map = dict(zip(info_df['Ticker'], info_df['Country']))
    df_country = pd.DataFrame({'Ticker': df.columns})
    df_country['Country'] = df_country['Ticker'].apply(lambda x: country_map.get(x, None))
    return df_country

# 国家分析函数

def country_analysis_for_holdings():
    returns_path = Path(__file__).parent.parent / 'processed_data' / 'returns.csv'
    df = pd.read_csv(returns_path)
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df, columns=df.columns if hasattr(df, 'columns') else None)
    # 只保留Type=Holding
    df = df[df['Type'] == 'Holding'].copy()
    # 加载Country信息
    info_path = Path(__file__).parent.parent / 'source_data' / 'holdings_info.csv'
    info_df = pd.read_csv(info_path, dtype={'Ticker': str})
    country_map = dict(zip(info_df['Ticker'], info_df['Country']))
    df['Country'] = df['Ticker'].apply(lambda x: country_map.get(x, None))
    # 只保留有Country的
    df = df[df['Country'].notna() & (df['Country'].astype(str).str.strip() != '')]
    # 需要的return类型
    return_types = ['DTD', 'WTD', 'MTD', 'YTD', 'Since Launch']
    # 计算每个return的contribution
    for rtype in return_types:
        col = rtype.replace(' ', '') + '_contribution' if ' ' in rtype else rtype + '_contribution'
        df[col] = df['Weight'] * df[rtype]
    # 计算每个国家的country_contribution
    for rtype in return_types:
        col = rtype.replace(' ', '') + '_contribution' if ' ' in rtype else rtype + '_contribution'
        country_col = 'country_' + col
        country_contrib = pd.DataFrame(df.groupby('Country', as_index=False)[col].sum())
        country_contrib = country_contrib.rename(columns={col: country_col})
        df = df.merge(country_contrib, on='Country', how='left')
    # 输出字段
    output_cols = ['Country', 'Ticker', 'Weight'] + return_types + [
        'DTD_contribution', 'WTD_contribution', 'MTD_contribution', 'YTD_contribution', 'SinceLaunch_contribution',
        'country_DTD_contribution', 'country_WTD_contribution', 'country_MTD_contribution', 'country_YTD_contribution', 'country_SinceLaunch_contribution'
    ]
    # 兼容列名
    df = df.rename(columns={'Since Launch_contribution': 'SinceLaunch_contribution', 'country_Since Launch_contribution': 'country_SinceLaunch_contribution'})
    df_out = df[output_cols]
    df_out.to_csv(Path(__file__).parent.parent / 'processed_data' / 'holdings_countryAnalysis.csv', index=False)
    print('国家贡献分析已保存为 holdings_countryAnalysis.csv')

def sector_analysis_for_holdings():
    import pandas as pd
    from pathlib import Path
    returns_path = Path(__file__).parent.parent / 'processed_data' / 'returns.csv'
    df = pd.read_csv(returns_path)
    df = pd.DataFrame(df)
    # 只保留Type=Holding
    df = df[df['Type'] == 'Holding'].copy()
    # 只保留有Industry的
    df = df[df['Industry'].notna() & (df['Industry'].astype(str).str.strip() != '')]
    # 需要的return类型
    return_types = ['DTD', 'WTD', 'MTD', 'YTD', 'Since Launch']
    # 计算每个return的contribution
    for rtype in return_types:
        col = rtype.replace(' ', '') + '_contribution' if ' ' in rtype else rtype + '_contribution'
        df[col] = df['Weight'] * df[rtype]
    # 计算每个行业的sector_contribution
    for rtype in return_types:
        col = rtype.replace(' ', '') + '_contribution' if ' ' in rtype else rtype + '_contribution'
        sector_col = 'sector_' + col
        sector_contrib = pd.DataFrame(df.groupby('Industry', as_index=False)[col].sum())
        sector_contrib = sector_contrib.rename(columns={col: sector_col})
        df = pd.DataFrame(df).merge(sector_contrib, on='Industry', how='left')
    # 输出字段
    output_cols = ['Industry', 'Ticker', 'Weight'] + return_types + [
        'DTD_contribution', 'WTD_contribution', 'MTD_contribution', 'YTD_contribution', 'SinceLaunch_contribution',
        'sector_DTD_contribution', 'sector_WTD_contribution', 'sector_MTD_contribution', 'sector_YTD_contribution', 'sector_SinceLaunch_contribution'
    ]
    # 兼容列名
    df = df.rename(columns={'Since Launch_contribution': 'SinceLaunch_contribution', 'sector_Since Launch_contribution': 'sector_SinceLaunch_contribution'})
    df_out = df[output_cols]
    df_out.to_csv(Path(__file__).parent.parent / 'processed_data' / 'holdings_sectorAnalysis.csv', index=False)
    print('行业贡献分析已保存为 holdings_sectorAnalysis.csv')

def main():
    closes = pd.read_csv(RAW_DATA_DIR / 'market_data_closes.csv', index_col=0, parse_dates=True)
    volumes = pd.read_csv(RAW_DATA_DIR / 'market_data_volumes.csv', index_col=0, parse_dates=True)
    returns_df = calculate_returns(closes)
    risk_metrics = calculate_risk_metrics(closes)
    volume_analysis = analyze_volume(volumes)

    # 读取持仓股票列表
    holdings_tickers = pd.read_csv(RAW_DATA_DIR / 'holdings_tickers.csv')['Ticker'].astype(str).tolist()

    # 加类型信息
    type_df = add_type_column(closes, holdings_tickers, ALL_BENCHMARKS)
    # 加Industry信息
    industry_df = add_industry_column(closes)
    # 合并类型和行业
    type_df = type_df.merge(industry_df, on='Ticker', how='left')

    # 计算权重（仅对持仓股票）
    # 读取最新持仓csv
    import re
    import glob
    import os
    # 找到最新的持仓csv文件
    holdings_files = sorted(glob.glob(str(HOLDINGS_DIR / '*_agix_holdings.csv')), reverse=True)
    if holdings_files:
        latest_holdings = pd.read_csv(holdings_files[0], skiprows=1)
        # 兼容Ticker列名
        if 'Ticker' in latest_holdings.columns and 'Market Value($)' in latest_holdings.columns:
            latest_holdings = latest_holdings.dropna(subset=['Ticker', 'Market Value($)'])
            latest_holdings['Ticker'] = latest_holdings['Ticker'].astype(str)
            #latest_holdings = latest_holdings[latest_holdings['Ticker'].apply(lambda t: bool(re.match(r'^[A-Z]{1,5}$', t)))]
            latest_holdings['Market Value($)'] = latest_holdings['Market Value($)'].astype(str).str.replace(',', '', regex=True).astype(float)
            total_value = latest_holdings['Market Value($)'].sum()
            latest_holdings['Weight'] = latest_holdings['Market Value($)'] / total_value
            weight_map = dict(zip(latest_holdings['Ticker'], latest_holdings['Weight']))
        else:
            weight_map = {}
    else:
        weight_map = {}
    # 生成weight列
    type_df['Weight'] = type_df['Ticker'].apply(lambda x: weight_map.get(x, 0))

    # 合并类型、权重和行业到分析结果
    returns_df = returns_df.merge(type_df, left_index=True, right_on='Ticker')
    risk_metrics = risk_metrics.merge(type_df, left_index=True, right_on='Ticker')
    volume_analysis = volume_analysis.merge(type_df, left_index=True, right_on='Ticker')

    returns_df.to_csv(PROCESSED_DATA_DIR / 'returns.csv', index=False)
    risk_metrics.to_csv(PROCESSED_DATA_DIR / 'risk_metrics.csv', index=False)
    volume_analysis.to_csv(PROCESSED_DATA_DIR / 'volume_analysis.csv', index=False)
    print('所有指标已保存')

if __name__ == '__main__':
    main()
    sector_analysis_for_holdings()
    country_analysis_for_holdings() 