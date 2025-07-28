import yfinance as yf

tickers = [
    "ANTH.PVT"
]

unavailable = []

for ticker in tickers:
    try:
        data = yf.Ticker(ticker)
        info = data.info
        # yfinance 返回的 info 为空字典时，说明无法获取
        if not info or info is None or info == {}:
            unavailable.append(ticker)
        print(info)
    except Exception as e:
        unavailable.append(ticker)

print('无法获取的代码:')
for t in unavailable:
    print(t)
