# AGIX Fund Monitor v3 手动操作指南

## 🎯 概述

本指南适用于纯手动操作模式，所有数据更新都需要手动执行，没有自动化功能。

## 📋 每日操作流程

### 第一步：启动应用

```bash
# 进入项目目录
cd C:\Users\18613\Desktop\cursor\FundsMonitor-MVP\v3

# 启动手动版本应用
streamlit run app_manual.py
```

应用将在浏览器中打开：`http://localhost:8501`

### 第二步：检查数据状态

在应用侧边栏中：
1. 查看是否有错误提示
2. 检查数据最后更新时间
3. 确认所有功能页面正常显示

### 第三步：更新数据（如需要）

**什么时候需要更新数据：**
- 美股收盘后（通常是北京时间早上5-6点）
- 持仓数据发生变化时
- 发现数据异常时

**更新步骤：**

#### 方法1：通过应用界面
1. 在应用侧边栏点击 "📊 更新数据" 按钮
2. 按照提示在终端中运行命令

#### 方法2：直接在终端运行
```bash
# 1. 更新持仓和市场数据
cd pipeline
python data_fetcher.py

# 2. 处理数据并生成分析结果
python data_processor.py

# 3. 返回主目录
cd ..
```

### 第四步：验证数据更新

1. **检查数据文件时间戳**
2. **刷新应用页面**
3. **查看数据最后更新时间**
4. **确认数据内容已更新**

## 🔄 数据更新详细说明

### 数据更新过程

**第一步：下载持仓数据**
```bash
python pipeline/data_fetcher.py
```
- 从KraneShares官网下载最新AGIX持仓
- 下载所有持仓股票的市场数据
- 下载基准ETF数据

**第二步：处理数据**
```bash
python pipeline/data_processor.py
```
- 计算收益率指标（DTD, WTD, MTD, YTD, Since Launch）
- 计算风险指标（年化收益率、波动率、夏普比率、最大回撤）
- 计算成交量分析
- 生成行业和国家分析

### 数据文件说明

**原始数据文件：**
- `source_data/market_data_closes.csv` - 收盘价数据
- `source_data/market_data_volumes.csv` - 成交量数据
- `holdings/*_agix_holdings.csv` - 持仓数据

**处理后数据文件：**
- `processed_data/returns.csv` - 收益率数据
- `processed_data/risk_metrics.csv` - 风险指标
- `processed_data/volume_analysis.csv` - 成交量分析
- `processed_data/holdings_sectorAnalysis.csv` - 行业分析
- `processed_data/holdings_countryAnalysis.csv` - 国家分析

## 📊 应用功能说明

### 主要页面

1. **📊 Fund Performance Comparison**
   - 收益率对比分析
   - 风险指标对比
   - 成交量分析
   - 累计收益曲线

2. **🔍 Portfolio Analysis**
   - 行业权重分布
   - 国家权重分布
   - 个股贡献度分析
   - 行业/国家贡献度分析

3. **📰 Market Sentiment Analysis**
   - 市场情绪分析（待实现）

### 交互功能

- **基准选择**：选择对比的ETF和指数
- **时间范围**：设置分析的时间范围
- **风险参数**：调整无风险利率
- **PDF导出**：生成分析报告

## ⚠️ 常见问题和解决方案

### 问题1：数据加载失败

**症状：** 应用显示"缺少必要的数据文件"

**解决方案：**
```bash
# 检查数据文件是否存在
dir source_data\*.csv
dir processed_data\*.csv

# 如果文件不存在，运行数据更新
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..
```

### 问题2：数据更新失败

**症状：** 运行数据更新脚本时出错

**解决方案：**
```bash
# 检查网络连接
ping google.com

# 检查Python依赖
pip install -r requirements.txt

# 检查磁盘空间
dir

# 重新运行更新脚本
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..
```

### 问题3：应用启动失败

**症状：** 运行`streamlit run app_manual.py`时出错

**解决方案：**
```bash
# 检查Python版本
python --version

# 检查依赖包
pip list | findstr streamlit

# 重新安装依赖
pip install -r requirements.txt

# 检查端口占用
netstat -ano | findstr :8501
```

### 问题4：数据不更新

**症状：** 运行更新脚本后，应用中的数据没有变化

**解决方案：**
```bash
# 检查文件修改时间
dir processed_data\*.csv

# 清除应用缓存
# 在应用中按 Ctrl+R 刷新页面

# 重启应用
# 关闭应用，重新运行 streamlit run app_manual.py
```

## 📅 建议的操作时间表

### 每日操作

**上午9:00-10:00（推荐）**
- 美股收盘后，数据最完整
- 用户开始工作前，数据已更新

**操作步骤：**
1. 启动应用
2. 检查数据状态
3. 如需要，更新数据
4. 验证数据更新
5. 开始使用应用

### 每周操作

**每周一上午**
- 检查上周数据完整性
- 清理旧日志文件
- 备份重要数据

### 每月操作

**每月初**
- 检查数据文件大小
- 更新Python依赖包
- 检查磁盘空间

## 🛠️ 维护和优化

### 定期维护

1. **清理日志文件**
   ```bash
   # 删除旧的日志文件
   del *.log
   ```

2. **检查磁盘空间**
   ```bash
   # 查看目录大小
   dir /s
   ```

3. **备份重要数据**
   ```bash
   # 备份数据文件
   xcopy processed_data backup\processed_data /E /I
   ```

### 性能优化

1. **清理缓存**
   - 定期重启应用
   - 清除浏览器缓存

2. **数据优化**
   - 定期清理历史数据
   - 压缩数据文件

## 📞 技术支持

如果遇到问题：

1. **查看错误信息**：仔细阅读错误提示
2. **检查日志文件**：查看详细的错误日志
3. **重启应用**：关闭并重新启动应用
4. **重新安装依赖**：`pip install -r requirements.txt`
5. **联系技术支持**：提供详细的错误信息

## 🎯 最佳实践

### 1. 数据管理
- 定期备份重要数据
- 保持数据文件整洁
- 及时清理临时文件

### 2. 应用使用
- 定期检查数据更新
- 及时处理错误提示
- 保持应用版本更新

### 3. 系统维护
- 定期更新Python依赖
- 保持足够的磁盘空间
- 定期重启系统

---

**记住：** 手动操作虽然需要更多时间，但能让你完全控制数据更新过程，确保数据的准确性和及时性！ 