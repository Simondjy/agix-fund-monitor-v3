# AGIX Fund Monitor v3

一个基于Streamlit的AGIX基金监控和分析平台，提供实时性能分析、风险评估和投资组合分析功能。

## 项目概述

本项目是一个完整的基金监控系统，包含：
- **数据采集管道**：自动下载AGIX持仓数据和市场行情数据
- **数据处理引擎**：计算各种金融指标和风险指标
- **可视化界面**：基于Streamlit的交互式Web应用
- **报告生成**：支持PDF报告导出功能

## 目录结构

```
v3/
├── app.py                    # Streamlit主应用
├── pipeline/                 # 数据处理管道
│   ├── config.py            # 配置文件
│   ├── data_fetcher.py      # 数据采集脚本
│   ├── data_processor.py    # 数据处理脚本
│   └── data_validate.py     # 数据验证脚本
├── source_data/             # 原始数据存储
│   ├── market_data_closes.csv    # 收盘价数据
│   ├── market_data_volumes.csv   # 成交量数据
│   ├── holdings_tickers.csv      # 持仓股票列表
│   └── holdings_info.csv         # 公司信息数据
├── processed_data/          # 处理后数据
│   ├── returns.csv              # 收益率数据
│   ├── risk_metrics.csv         # 风险指标
│   ├── volume_analysis.csv      # 成交量分析
│   ├── holdings_sectorAnalysis.csv  # 行业分析
│   └── holdings_countryAnalysis.csv # 国家分析
├── holdings/                # AGIX持仓文件
│   └── *_agix_holdings.csv  # 每日持仓数据
├── visualizer.py            # 可视化工具
├── pdf_generator.py         # PDF报告生成器
├── utils.py                 # 工具函数
└── README.md               # 项目说明
```

## 功能特性

### 1. 基金表现对比分析
- 多时间维度收益率分析（日、周、月、年、成立以来）
- 与主流ETF和指数的对比
- 收益率分布可视化
- 累计收益曲线展示

### 2. 风险评估
- 年化收益率和波动率
- 夏普比率计算
- 最大回撤分析
- 风险指标可视化

### 3. 投资组合分析
- 行业权重分布
- 国家权重分布
- 个股贡献度分析
- 行业/国家贡献度分析

### 4. 成交量分析
- 日均成交量统计
- 成交量趋势可视化
- 成交量变化率分析

### 5. 报告导出
- 支持PDF格式报告导出
- 可选择导出页面内容
- 包含图表和数据表格

## 安装和运行

### 环境要求
- Python 3.8+
- Streamlit
- pandas, numpy, matplotlib, seaborn
- yfinance
- reportlab

### 安装依赖
```bash
pip install streamlit pandas numpy matplotlib seaborn yfinance reportlab
```

### 数据准备
1. 运行数据采集管道：
```bash
cd pipeline
python data_fetcher.py
python data_processor.py
```

2. 启动应用：
```bash
streamlit run app.py
```

## 部署说明

### 本地部署
项目设计为本地数据存储模式，所有数据文件存储在本地目录中。

### 云端部署
由于项目依赖本地数据文件，云端部署需要：
1. 将数据文件上传到云端服务器
2. 配置定期数据更新机制
3. 使用Streamlit Cloud或其他云平台部署

## 数据更新

项目支持自动数据更新：
- 持仓数据：每日从KraneShares官网自动下载
- 市场数据：通过yfinance API获取实时行情
- 处理数据：自动计算最新指标

## 技术架构

- **前端**：Streamlit Web应用
- **数据处理**：pandas + numpy
- **可视化**：matplotlib + seaborn
- **数据源**：yfinance API + KraneShares官网
- **报告生成**：reportlab

## 注意事项

1. 首次运行需要下载历史数据，可能需要较长时间
2. 确保网络连接正常以获取最新数据
3. 数据文件较大，建议定期清理历史数据
4. 部署时需要确保所有依赖包正确安装

## 版本历史

- v3: 完整重构，增加投资组合分析和报告功能
- v2: 基础监控功能
- v1: 初始版本 