import pandas as pd
from pathlib import Path

# 读取收盘价数据
closes_path = Path(__file__).parent.parent / 'source_data' / 'market_data_closes.csv'
if not closes_path.exists():
    closes_path = Path(__file__).parent.parent / 'source_data' / 'market_data_closes.csv'
closes = pd.read_csv(closes_path, index_col=0, parse_dates=True)

problem_tickers = {}

for ticker in closes.columns:
    series = closes[ticker]
    # 找到第一个非空的日期（上市首日）
    first_valid = series.first_valid_index()
    if first_valid is None:
        continue  # 全部为空，跳过
    # 上市首日及之后的所有数据
    after_list = series.loc[first_valid:]
    # 检查是否有空值
    if after_list.isna().any():
        na_dates = after_list[after_list.isna()].index.strftime('%Y-%m-%d').tolist()
        problem_tickers[ticker] = na_dates

#if problem_tickers:
    #print('以下标的在上市后仍有空白数据：')
    #for ticker, dates in problem_tickers.items():
        #print(f'{ticker}: {dates}')
#else:
    #print('所有标的上市后数据均完整。')

# 检查是否有连续多天空白的标的
from datetime import datetime, timedelta

print("\n==== 连续多天空白检测 ====")
found = False
for ticker, dates in problem_tickers.items():
    # 转为日期对象并排序
    date_objs = sorted([datetime.strptime(d, '%Y-%m-%d') for d in dates])
    if not date_objs:
        continue
    streak = 1
    max_streak = 1
    streak_start = date_objs[0]
    max_streak_start = streak_start
    max_streak_end = streak_start
    for i in range(1, len(date_objs)):
        if (date_objs[i] - date_objs[i-1]).days == 1:
            streak += 1
            if streak > max_streak:
                max_streak = streak
                max_streak_start = date_objs[i-streak+1]
                max_streak_end = date_objs[i]
        else:
            streak = 1
    if max_streak > 1:
        found = True
        print(f"{ticker} 存在连续 {max_streak} 天空白，起始日期：{max_streak_start.strftime('%Y-%m-%d')}，结束日期：{max_streak_end.strftime('%Y-%m-%d')}")
if not found:
    print("未发现任何标的有连续多天空白的情况，仅为单天分布。")

def validate_industry_mapping():
    # 读取returns.csv，假设Type和Industry都在里面
    df = pd.read_csv(Path(__file__).parent.parent / 'processed_data' / 'returns.csv')
    problems = []
    for _, row in df.iterrows():
        ticker = row['Ticker']
        ttype = row['Type']
        industry = row['Industry'] if 'Industry' in row else None
        industry_str = str(industry).strip().lower()
        if ttype == 'Holding':
            if industry_str == '' or industry_str == 'nan':
                problems.append((ticker, ttype, 'Holding无行业'))
        elif ttype == 'Comparison ETF':
            if not (industry_str == '' or industry_str == 'nan'):
                problems.append((ticker, ttype, 'ETF有行业'))
    if not problems:
        print('行业mapping正确')
    else:
        print('行业mapping有问题的tickers:')
        for t in problems:
            print(f'Ticker: {t[0]}, Type: {t[1]}, 问题: {t[2]}')

if __name__ == '__main__':
    print("\n==== 行业映射验证 ====")
    validate_industry_mapping() 