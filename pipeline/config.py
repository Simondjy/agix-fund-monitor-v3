import os
from pathlib import Path
from datetime import datetime, timedelta

# v2本地数据保存路径
BASE_DIR = Path(__file__).resolve().parent.parent  # v2目录
RAW_DATA_DIR = BASE_DIR / 'source_data'
PROCESSED_DATA_DIR = BASE_DIR / 'processed_data'
HOLDINGS_DIR = BASE_DIR / 'holdings'

# 常用ETF列表
ALL_BENCHMARKS = [
    "QQQ",
    "^SPX",
    "DIA",
    "^DJI",
    "SPY",
    "SMH",
    "IGV",
    "CHAT",
    "LRNZ",
    "AIS",
    "AIQ",
    "LOUP",
    "THNQ",
    "FDTX",
    "WTAI",
    "RBOT",
    "IGPT",
    "ARTY",
    "RBOT",
    "XAIX.F",#
    "XAIX",
    "BOTZ",
    "AIAI.L",
    "RBTZ.AX",
    "WTAI",
    "WISE",
    "XB0T.DE"
]

# yfinance下载参数
YF_PERIOD = 'max'
YF_INTERVAL = '1d'
# yfinance数据下载起始日期
YF_START_DATE = '2023-01-01'
YF_END_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# 其他配置
CACHE_DIR = BASE_DIR / 'cache' 


# 股票代码对应的Industry
TICKER_TO_INDUSTRY = {
    "META": "Application",
    "CRM": "Application",
    "NOW": "Application",
    "DUOL": "Application",
    "SAP": "Application",
    "TEM": "Application",
    "ADBE": "Application",
    "IOT": "Application",
    "WDAY": "Application",
    "RBLX": "Application",
    "APP": "Application",
    "SHOP": "Application",
    "TEAM": "Application",
    
    "MSFT": "Infrastructure",
    "AMZN": "Infrastructure",
    "GOOGL": "Infrastructure",
    "TSLA": "Infrastructure",
    "PLTR": "Infrastructure",
    "ORCL": "Infrastructure",
    "NBIS": "Infrastructure",
    "ESTC": "Infrastructure",
    "SNOW": "Infrastructure",
    "DDOG": "Infrastructure",
    "NET": "Infrastructure",
    "GTLB": "Infrastructure",
    "PANW": "Infrastructure",
    "MDB": "Infrastructure",
    "PSTG": "Infrastructure",
    "ZS": "Infrastructure",
    "CFLT": "Infrastructure",
    
    "NVDA": "Semi",
    "AAPL": "Semi",
    "AVGO": "Semi",
    #"2330": "Semi",
    #"A000660": "Semi",
    "ASML": "Semi",
    "MRVL": "Semi",
    "VRT": "Semi",
    "ANET": "Semi",
    #"2454": "Semi",
    "MU": "Semi",
    "QCOM": "Semi",
    "SNPS": "Semi",
    "ARM": "Semi",
    
    "000660.KS": "Semi",#
    "2330.TW": "Semi",#
    "XAAI.PVT": "Infrastructure",
    "2454.TW": "Semi",#
    "ANTH.PVT": "Infrastructure",

}

COMPANY_TO_TICKER_ADD = {
    "XAI HOLDINGS CORP": "XAAI.PVT",
    "ANTHROPIC, PBC": "ANTH.PVT",
    "TSMC": "2330.TW",
    "SK HYNIX INC": "000660.KS",
    "ARISTA NETWORKS INC": "ANET",
    "MEDIATEK INC": "2454.TW",
    # 可继续补充
}