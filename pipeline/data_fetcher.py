import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import RAW_DATA_DIR, HOLDINGS_DIR, ALL_BENCHMARKS, YF_PERIOD, YF_INTERVAL, YF_START_DATE, YF_END_DATE, COMPANY_TO_TICKER_ADD
import requests
import time

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
HOLDINGS_DIR.mkdir(parents=True, exist_ok=True)

# 尝试从kraneshares官网按指定文件名下载持仓csv文件，下载成功返回True，否则返回False
def try_download(csv_name, save_path):
    url = f'https://kraneshares.com/csv/{csv_name}'
    print(f'[INFO] 尝试下载URL: {url}')
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f'[INFO] 下载成功: {save_path}')
        return True
    except Exception as e:
        print(f'[WARN] 下载失败: {url}, 错误: {e}')
        return False

# 下载AGIX持仓文件，优先下载今日，其次昨日，最后本地最新，找不到则返回None
def download_agix_holdings():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    today_csv = today.strftime('%m_%d_%Y') + '_agix_holdings.csv'
    yesterday_csv = yesterday.strftime('%m_%d_%Y') + '_agix_holdings.csv'
    today_path = HOLDINGS_DIR / today_csv
    yesterday_path = HOLDINGS_DIR / yesterday_csv

    # 1. 优先下载今日
    if not today_path.exists():
        if try_download(today_csv, today_path):
            return today_path
    if today_path.exists():
        print(f'[INFO] 使用本地今日持仓: {today_path}')
        return today_path

    # 2. 下载昨日
    if not yesterday_path.exists():
        if try_download(yesterday_csv, yesterday_path):
            return yesterday_path
    if yesterday_path.exists():
        print(f'[INFO] 使用本地昨日持仓: {yesterday_path}')
        return yesterday_path

    # 3. 用本地最新
    all_csvs = sorted(HOLDINGS_DIR.glob('*_agix_holdings.csv'), reverse=True)
    if all_csvs:
        print(f'[INFO] 使用本地最新持仓: {all_csvs[0]}')
        return all_csvs[0]
    print('[FATAL] 无法下载或找到任何AGIX持仓文件，请检查网络或手动上传。')
    return None


# 读取持仓csv文件，提取有效的股票ticker列表
# 新增：根据公司名替换ticker，并覆盖保存到原文件
def replace_tickers_in_holdings_file(holdings_csv):
    df = pd.read_csv(holdings_csv, skiprows=1)
    for company, ticker in COMPANY_TO_TICKER_ADD.items():
        df.loc[df['Company Name'] == company, 'Ticker'] = ticker
    # 重新保存，保留原有的表头格式
    with open(holdings_csv, 'r', encoding='utf-8') as f:
        header = f.readline()
    df.to_csv(holdings_csv, index=False, mode='w', encoding='utf-8')
    # 保留原始的第一行表头
    with open(holdings_csv, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(header + content)

# 读取持仓csv文件，提取有效的股票ticker列表
def get_holdings_tickers(holdings_csv):
    print(f'[INFO] 读取持仓csv: {holdings_csv}')
    df = pd.read_csv(holdings_csv, skiprows=1)
    # 只修改需要替换的Ticker
    #for company, ticker in COMPANY_TO_TICKER_ADD.items():
        #df.loc[df['Company Name'] == company, 'Ticker'] = ticker
    tickers = df["Ticker"].dropna().astype(str).unique().tolist()

    #import re
    #total_count = len(tickers)
    #valid_tickers = [t for t in tickers if re.match(r'^[A-Z]{1,5}$', t)]
    #valid_count = len(valid_tickers)
    #invalid_count = total_count - valid_count
    #invalid_tickers = [t for t in tickers if not re.match(r'^[A-Z]{1,5}$', t)]
    #print(f'[INFO] 总ticker数量: {total_count}，有效ticker数量: {valid_count}，无效tickers: {invalid_tickers}')
    #tickers = [t for t in tickers if re.match(r'^[A-Z]{1,5}$', t)]
    #print(f'[INFO] 持仓ticker数量: {len(tickers)}，示例: {tickers[:10]}')

    return tickers

# 批量下载指定ticker的行情数据（收盘价和成交量），并保存为csv文件
# 默认从YF_START_DATE开始，按50只股票一批下载，支持多线程
def download_market_data(tickers, start_date=YF_START_DATE, end_date=YF_END_DATE):
    batch_size = 100
    max_retries = 5
    remaining_tickers = tickers.copy()
    closes_list, volumes_list = [], []
    retry_count = 0
    while remaining_tickers and retry_count < max_retries:
        time.sleep(1)
        failed_tickers = []
        print(f'\n[RETRY] 第{retry_count+1}轮尝试，待下载ticker数量: {len(remaining_tickers)}')
        for i in range(0, len(remaining_tickers), batch_size):
            batch = remaining_tickers[i:i+batch_size]
            print(f'[INFO] 下载行情 batch {i//batch_size+1} (重试{retry_count+1}): {batch}')
            try:
                data = yf.download(batch, start=start_date, end=end_date, period=YF_PERIOD, interval=YF_INTERVAL, group_by='ticker', auto_adjust=True, threads=True)
                if data is None or (hasattr(data, 'empty') and data.empty):
                    print(f'[WARN] batch {i//batch_size+1} 无数据: {batch}')
                    failed_tickers.extend(batch)
                    continue
                # 检查每个ticker在最新交易日是否有收盘价，否则加入失败列表
                latest_date = None
                if hasattr(data, 'empty') and (not data.empty):
                    latest_date = data.index.max()
                batch_failed = []
                for t in batch:
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            close_val = data[(t, 'Close')].loc[latest_date] if latest_date is not None and (t, 'Close') in data.columns else None
                        else:
                            close_val = data['Close'].loc[latest_date] if latest_date is not None and 'Close' in data.columns else None
                        if isinstance(close_val, pd.Series):
                            # 如果是Series，检查是否全是NaN
                            if close_val.isna().all():
                                batch_failed.append(t)
                        elif pd.isna(close_val):
                            batch_failed.append(t)
                    except Exception:
                        batch_failed.append(t)
                if batch_failed:
                    print(f'[WARN] batch {i//batch_size+1} 最新交易日无收盘价ticker: {batch_failed}')
                    failed_tickers.extend(batch_failed)
                else:
                    print(f'[INFO] batch {i//batch_size+1} 全部ticker最新交易日有收盘价')
                if isinstance(data.columns, pd.MultiIndex):
                    closes = data.loc[:, (slice(None), 'Close')]
                    closes.columns = closes.columns.droplevel(1)
                    volumes = data.loc[:, (slice(None), 'Volume')]
                    volumes.columns = volumes.columns.droplevel(1)
                else:
                    closes = data[['Close']]
                    volumes = data[['Volume']]
                closes_list.append(closes)
                volumes_list.append(volumes)
            except Exception as e:
                print(f'[ERROR] batch {i//batch_size+1} 下载异常: {e}')
                failed_tickers.extend(batch)
        if failed_tickers:
            print(f'[RETRY] 第{retry_count+1}轮失败ticker: {failed_tickers}')
        else:
            print(f'[RETRY] 第{retry_count+1}轮全部ticker下载成功！')
        remaining_tickers = list(set(failed_tickers))
        retry_count += 1
        if remaining_tickers:
            print(f'[RETRY] 轮次{retry_count}后，仍需重试ticker: {remaining_tickers}')
    if remaining_tickers:
        print(f'[ERROR] 达到最大重试次数，以下ticker仍未成功下载: {remaining_tickers}')
    if closes_list:
        closes_all = pd.concat(closes_list, axis=1)
        closes_all = closes_all.loc[:,~closes_all.columns.duplicated()]
        closes_all.to_csv(RAW_DATA_DIR / 'market_data_closes.csv')
        print(f'[INFO] 收盘价已保存: {RAW_DATA_DIR / "market_data_closes.csv"}')
        # 检查每个ticker在最新交易日是否有收盘价数据
        latest_date = closes_all.index.max()
        missing_tickers = [col for col in closes_all.columns if pd.isna(closes_all.loc[latest_date, col])]
        if missing_tickers:
            print(f'[WARN] 以下ticker在最新交易日({latest_date})无收盘价数据: {missing_tickers}')
    else:
        print('[ERROR] 没有收盘价数据可保存')
    if volumes_list:
        volumes_all = pd.concat(volumes_list, axis=1)
        volumes_all = volumes_all.loc[:,~volumes_all.columns.duplicated()]
        volumes_all.to_csv(RAW_DATA_DIR / 'market_data_volumes.csv')
        print(f'[INFO] 交易量已保存: {RAW_DATA_DIR / "market_data_volumes.csv"}')
    else:
        print('[ERROR] 没有交易量数据可保存')


def fetch_holdings_info():
    import pandas as pd
    import yfinance as yf
    from pathlib import Path
    from tqdm import tqdm
    tickers_path = Path(__file__).parent.parent / 'source_data' / 'holdings_tickers.csv'
    out_path = Path(__file__).parent.parent / 'source_data'  / 'holdings_info.csv'
    tickers = pd.read_csv(tickers_path)['Ticker'].astype(str).tolist()
    info_list = []
    for t in tqdm(tickers, desc='获取公司信息'):
        try:
            yf_t = yf.Ticker(t)
            info = yf_t.info
            info_list.append({
                'Ticker': t,
                'Company Name': info.get('longName', ''),
                'Website': info.get('website', ''),
                'Country': info.get('country', ''),
                'AverageAnalystRating': info.get('averageAnalystRating', '')
            })
        except Exception as e:
            info_list.append({
                'Ticker': t,
                'Company Name': '',
                'Website': '',
                'Country': '',
                'AverageAnalystRating': '',
                'Error': str(e)
            })
    df_info = pd.DataFrame(info_list)
    df_info.to_csv(out_path, index=False)
    print(f'[INFO] 持仓公司信息已保存: {out_path}')


def main():
    print("\n" + "="*40 + " PIPELINE START " + "="*40)
    # 下载持仓
    print("\n" + "="*20 + " 下载持仓情况 " + "="*20)
    holdings_csv = download_agix_holdings()
    if holdings_csv is None:
        print('[FATAL] 持仓数据下载失败，终止')
        return

    # 新增：下载后直接替换ticker
    replace_tickers_in_holdings_file(holdings_csv)

    holdings_tickers = get_holdings_tickers(holdings_csv)
    # 保存holdings_tickers到csv，供data_processor使用
    pd.Series(holdings_tickers, name='Ticker').to_csv(RAW_DATA_DIR / 'holdings_tickers.csv', index=False)
    # 合并AGIX、基准指数和持仓股票ticker，去重
    all_tickers = ['AGIX'] + ALL_BENCHMARKS + holdings_tickers
    all_tickers = list(dict.fromkeys([t for t in all_tickers if t and t != 'nan']))
    # 下载市场数据
    print("\n" + "="*20 + " 下载市场数据 " + "="*20)
    print(f'[INFO] 总共需要下载行情的ticker数量: {len(all_tickers)}')
    download_market_data(all_tickers)  # start_date默认已为YF_START_DATE
    # 下载持仓公司信息
    print("\n" + "="*20 + " 下载持仓股票公司信息 " + "="*20)
    fetch_holdings_info()
    print("\n" + "="*40 + " PIPELINE END " + "="*40)

if __name__ == '__main__':
    # 直接运行本文件时，执行主流程
    main() 