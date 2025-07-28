import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def plot_returns_comparison(returns_df, benchmarks):
    # 只选择实际存在的benchmarks，避免KeyError
    available = [b for b in ['AGIX'] + benchmarks if b in returns_df.index]
    if not available:
        raise ValueError('没有可用的AGIX或基准标的在数据中！')
    agix_comparison = returns_df.loc[available]
    fig, ax = plt.subplots(figsize=(10, 6))
    agix_comparison.T.plot(kind='bar', ax=ax)
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax.set_title("AGIX vs Benchmarks Return Comparison")
    ax.set_ylabel("Return (%)")
    ax.legend(title="Ticker", bbox_to_anchor=(1.05, 1), loc='upper left')
    return fig

def plot_returns_distribution(returns_df):
    returns_to_plot = returns_df[['DTD', 'WTD', 'MTD', 'YTD']].apply(lambda x: x * 100)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=returns_to_plot, ax=ax)
    ax.axhline(0, color='red', linestyle='--', alpha=0.7)
    ax.set_title("Return Distribution Comparison")
    ax.set_ylabel("Return (%)")
    return fig

def plot_cumulative_returns(closes, benchmarks, window=5):
    # 1. 找到AGIX有数据的第一天
    agix_valid = closes['AGIX'].first_valid_index()
    # 2. 截取所有数据从AGIX上市日开始
    closes = closes.loc[agix_valid:]
    normed_returns = closes / closes.iloc[0] - 1
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for ticker in ['AGIX'] + benchmarks:
        if ticker in normed_returns.columns:
            # 原始数据（细线，透明度较低）
            ax.plot(normed_returns.index, normed_returns[ticker] * 100, 
                    alpha=0.3, linewidth=1, color='gray')
            
            # 平滑处理后的数据（粗线，透明度较高）
            smoothed_data = normed_returns[ticker].rolling(window=window, min_periods=1).mean() * 100
            ax.plot(normed_returns.index, smoothed_data, 
                    label=ticker, linewidth=3 if ticker == 'AGIX' else 2, alpha=0.8)
    
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax.set_title(f"Cumulative Return Since Listing (Smoothed with {window}-day MA)")
    ax.set_ylabel("Cumulative Return (%)")
    ax.legend()
    ax.grid(True, alpha=0.2)
    return fig

def plot_risk_metrics(risk_metrics, benchmarks):
    risk_comparison = risk_metrics.loc[['AGIX'] + benchmarks]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    sns.barplot(x=risk_comparison.index, y='Annualized Return', data=risk_comparison, ax=axes[0, 0])
    axes[0, 0].set_title('Annualized Return (%)')
    sns.barplot(x=risk_comparison.index, y='Annualized Volatility', data=risk_comparison, ax=axes[0, 1])
    axes[0, 1].set_title('Annualized Volatility (%)')
    sns.barplot(x=risk_comparison.index, y='Sharpe Ratio', data=risk_comparison, ax=axes[1, 0])
    axes[1, 0].axhline(1.0, color='red', linestyle='--', alpha=0.7)
    axes[1, 0].set_title('Sharpe Ratio')
    sns.barplot(x=risk_comparison.index, y='Max Drawdown', data=risk_comparison, ax=axes[1, 1])
    axes[1, 1].set_title('Max Drawdown (%)')
    plt.tight_layout()
    return fig

def plot_volume_trend(volumes, window=5):
    fig, ax = plt.subplots(figsize=(12, 6))
    if 'AGIX' in volumes.columns:
        # 原始数据（细线，透明度较低）
        ax.plot(volumes.index, volumes['AGIX'], 
                alpha=0.3, linewidth=1, color='gray', label='Raw Volume')
        
        # 平滑处理后的数据（粗线，透明度较高）
        smoothed_volume = volumes['AGIX'].rolling(window=window, min_periods=1).mean()
        ax.plot(volumes.index, smoothed_volume, 
                linewidth=2, color='blue', alpha=0.8, label=f'Smoothed Volume ({window}-day MA)')
    
    ax.set_title(f"AGIX Daily Trading Volume (Smoothed with {window}-day MA)")
    ax.set_ylabel("Volume")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.3)
    return fig 