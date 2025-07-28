from datetime import datetime
import pandas as pd

def get_today_str():
    return datetime.today().strftime('%Y-%m-%d')

def read_csv_with_index(path):
    return pd.read_csv(path, index_col=0, parse_dates=True) 