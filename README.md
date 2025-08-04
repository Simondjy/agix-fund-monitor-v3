# AGIX Fund Monitor v3

一个基于Streamlit的AGIX基金监控和分析平台，提供实时性能分析、风险评估和投资组合分析功能。

## 🚀 在线访问

**应用已部署到Streamlit Cloud，可直接访问：**
```
https://agix-fund-monitor-v3-xxxxx.streamlit.app
```

用户无需安装任何软件，直接打开浏览器即可使用！

## 项目概述

本项目是一个完整的基金监控系统，包含：
- **数据采集管道**：自动下载AGIX持仓数据和市场行情数据
- **数据处理引擎**：计算各种金融指标和风险指标
- **可视化界面**：基于Streamlit的交互式Web应用
- **报告生成**：支持PDF报告导出功能
- **云端部署**：支持Streamlit Cloud一键部署

## 目录结构

```
v3/
├── app.py                    # 本地开发版本（Streamlit主应用）
├── app_cloud.py              # 云端部署版本
├── cloud_data_loader.py      # 云端数据加载器
├── data_sync.py              # 数据同步工具
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
├── data/                    # 云端数据文件（JSON格式）
│   ├── *.json              # 转换后的JSON数据文件
├── holdings/                # AGIX持仓文件
│   └── *_agix_holdings.csv  # 每日持仓数据
├── visualizer.py            # 可视化工具
├── pdf_generator.py         # PDF报告生成器
├── utils.py                 # 工具函数
├── requirements.txt         # Python依赖包
├── .streamlit/              # Streamlit配置
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

### 6. 数据状态监控
- 实时显示数据可用性
- 数据文件状态检查
- 云端数据同步状态

## 快速开始

### 方式一：在线使用（推荐）
直接访问部署好的应用：
```
https://agix-fund-monitor-v3-xxxxx.streamlit.app
```

### 方式二：本地开发

#### 环境要求
- Python 3.8+
- Git

#### 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/Simondjy/agix-fund-monitor-v3.git
cd agix-fund-monitor-v3

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行数据管道
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..

# 4. 启动本地应用
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

## Git操作指南

### 日常开发流程

#### 1. 更新数据
```bash
# 运行数据采集管道
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..

# 同步数据到云端格式
python data_sync.py --action sync

# 提交更改
git add .
git commit -m "Update data - $(date +%Y-%m-%d)"
git push origin main
```

#### 2. 修改代码
```bash
# 在本地修改代码后
git add .
git commit -m "Add new feature: description"
git push
```

#### 3. 查看状态
```bash
# 查看文件状态
git status

# 查看提交历史
git log --oneline -10

# 查看分支
git branch -a
```

### 分支管理
```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 数据更新和维护

### 自动数据更新
项目支持自动数据更新：
- **持仓数据**：每日从KraneShares官网自动下载
- **市场数据**：通过yfinance API获取实时行情
- **处理数据**：自动计算最新指标

### 手动数据更新
```bash
# 1. 更新原始数据
cd pipeline
python data_fetcher.py

# 2. 处理数据
python data_processor.py
cd ..

# 3. 同步到云端格式
python data_sync.py --action sync

# 4. 提交并推送
git add .
git commit -m "Update data - $(date +%Y-%m-%d)"
git push
```

### 数据同步工具
```bash
# 同步所有数据到JSON格式
python data_sync.py --action sync

# 从JSON恢复CSV格式
python data_sync.py --action restore

# 查看帮助
python data_sync.py --help
```

## 云端部署

### Streamlit Cloud部署（已配置）

项目已配置为Streamlit Cloud部署：
- **主文件**：`app_cloud.py`
- **Python版本**：3.9
- **依赖文件**：`requirements.txt`

### 部署流程
1. 代码推送到GitHub后，Streamlit Cloud自动重新部署
2. 部署时间：2-5分钟
3. 部署状态可在Streamlit Cloud控制台查看

### 环境变量配置
在Streamlit Cloud中可配置：
- `STREAMLIT_SERVER_PORT`: 8501
- `STREAMLIT_SERVER_HEADLESS`: true

## 故障排除

### 常见问题

#### 1. 数据加载失败
```bash
# 检查数据文件
ls -la source_data/ processed_data/

# 重新运行数据管道
cd pipeline
python data_fetcher.py
python data_processor.py
```

#### 2. 依赖包安装失败
```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --no-cache-dir
```

#### 3. 云端部署失败
- 检查GitHub仓库连接
- 确认主文件路径为 `app_cloud.py`
- 查看Streamlit Cloud日志

#### 4. 端口被占用
```bash
# 查找占用进程
lsof -i :8501

# 使用不同端口
streamlit run app.py --server.port=8502
```

## 技术架构

- **前端**：Streamlit Web应用
- **数据处理**：pandas + numpy
- **可视化**：matplotlib + seaborn
- **数据源**：yfinance API + KraneShares官网
- **报告生成**：reportlab
- **云端部署**：Streamlit Cloud
- **版本控制**：Git + GitHub

## 开发规范

### 代码提交规范
```bash
# 功能更新
git commit -m "feat: add new feature"

# 数据更新
git commit -m "data: update market data"

# 修复bug
git commit -m "fix: resolve data loading issue"

# 文档更新
git commit -m "docs: update README"
```

### 文件命名规范
- Python文件：小写字母，下划线分隔
- 数据文件：描述性名称，日期格式
- 配置文件：小写字母，点分隔

## 注意事项

1. **首次运行**：需要下载历史数据，可能需要较长时间
2. **网络连接**：确保网络连接正常以获取最新数据
3. **数据文件**：文件较大，建议定期清理历史数据
4. **云端部署**：确保所有依赖包正确安装
5. **数据同步**：更新数据后记得运行同步脚本

## 版本历史

- **v3.1**：添加云端部署和数据同步功能
- **v3.0**：完整重构，增加投资组合分析和报告功能
- **v2.0**：基础监控功能
- **v1.0**：初始版本

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。

## 联系方式


---

**最后更新**：2025年1月 