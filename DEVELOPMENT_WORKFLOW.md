# AGIX Fund Monitor v3 开发工作流程指南

## 🎯 开发环境设置

### 1. 分支管理

**推荐的分支策略：**
- `main` - 生产环境，用户使用的稳定版本
- `develop` - 开发环境，新功能开发和测试
- `feature/xxx` - 功能分支，开发具体功能

### 2. 开发工具

**必需工具：**
- Python 3.8+
- Git
- 代码编辑器（VS Code推荐）
- 浏览器（测试用）

## 📋 日常开发流程

### 第一步：开始新功能开发

```bash
# 1. 确保在develop分支
git checkout develop

# 2. 拉取最新代码
git pull origin develop

# 3. 创建功能分支（可选）
git checkout -b feature/new-feature

# 4. 开始开发
# 编辑代码文件...
```

### 第二步：本地开发和测试

```bash
# 1. 启动本地应用进行开发
streamlit run app.py

# 2. 或者启动云端版本进行测试
streamlit run app_cloud.py

# 3. 在浏览器中测试功能
# http://localhost:8501
```

### 第三步：更新和测试数据

```bash
# 1. 更新数据（如果需要）
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..

# 2. 测试数据同步
python data_sync.py --action sync

# 3. 测试应用是否正常工作
streamlit run app_cloud.py
```

### 第四步：提交代码

```bash
# 1. 检查更改
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "Add new feature: [功能描述]"

# 4. 推送到远程仓库
git push origin develop
```

### 第五步：合并到生产环境

```bash
# 1. 切换到main分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 合并develop分支
git merge develop

# 4. 推送到GitHub
git push origin main

# 5. Streamlit Cloud会自动重新部署
```

## 🔄 数据更新流程

### 手动更新（开发时）

```bash
# 1. 更新持仓数据
cd pipeline
python data_fetcher.py

# 2. 处理数据
python data_processor.py
cd ..

# 3. 同步到云端格式
python data_sync.py --action sync

# 4. 测试应用
streamlit run app_cloud.py
```

### 自动化更新（生产环境）

```bash
# 使用自动化脚本
python auto_update.py --full-update
```

### 定时更新设置

```bash
# 设置每天上午9点自动更新
python auto_update.py --schedule --hour 9 --minute 0
```

## 🧪 测试策略

### 1. 功能测试

**测试清单：**
- [ ] 数据加载是否正常
- [ ] 所有页面是否可访问
- [ ] 图表是否正确显示
- [ ] 交互功能是否正常
- [ ] PDF导出是否工作

### 2. 数据测试

```bash
# 测试数据完整性
python -c "
import pandas as pd
import json

# 检查JSON数据文件
data_files = [
    'data/returns.json',
    'data/risk_metrics.json',
    'data/volume_analysis.json'
]

for file in data_files:
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        print(f'✅ {file} - 数据行数: {len(data[\"data\"])}')
    except Exception as e:
        print(f'❌ {file} - 错误: {e}')
"
```

### 3. 性能测试

```bash
# 测试应用启动时间
time streamlit run app_cloud.py --server.headless true

# 测试数据加载时间
python -c "
import time
from cloud_data_loader import load_application_data

start_time = time.time()
data = load_application_data()
end_time = time.time()

print(f'数据加载时间: {end_time - start_time:.2f}秒')
"
```

## 🚀 部署流程

### 1. 开发环境部署

```bash
# 在develop分支上测试
git checkout develop
streamlit run app_cloud.py
```

### 2. 生产环境部署

```bash
# 1. 确保代码已测试通过
python auto_update.py --test

# 2. 合并到main分支
git checkout main
git merge develop

# 3. 推送到GitHub
git push origin main

# 4. Streamlit Cloud自动部署
```

### 3. 部署验证

**检查清单：**
- [ ] 访问Streamlit Cloud应用URL
- [ ] 检查数据是否正确加载
- [ ] 测试所有功能
- [ ] 检查错误日志

## 📊 数据管理

### 1. 数据更新频率

**建议更新频率：**
- **持仓数据**: 每日更新（交易日后）
- **市场数据**: 每日更新（收盘后）
- **分析数据**: 数据更新后自动重新计算

### 2. 数据备份

```bash
# 创建数据备份
python data_sync.py --action sync
git add data/*.json
git commit -m "Backup data: $(date)"
git push origin main
```

### 3. 数据验证

```bash
# 验证数据完整性
python -c "
import pandas as pd
from pathlib import Path

# 检查必要的数据文件
required_files = [
    'source_data/market_data_closes.csv',
    'source_data/market_data_volumes.csv',
    'processed_data/returns.csv',
    'processed_data/risk_metrics.csv'
]

for file in required_files:
    if Path(file).exists():
        df = pd.read_csv(file)
        print(f'✅ {file} - 行数: {len(df)}')
    else:
        print(f'❌ {file} - 文件不存在')
"
```

## 🔧 故障排除

### 1. 常见问题

**问题1: 数据加载失败**
```bash
# 解决方案
python data_sync.py --action restore
streamlit run app_cloud.py
```

**问题2: 应用启动失败**
```bash
# 检查依赖
pip install -r requirements.txt

# 检查端口占用
netstat -ano | findstr :8501
```

**问题3: Git推送失败**
```bash
# 拉取最新代码
git pull origin main

# 解决冲突后重新推送
git push origin main
```

### 2. 日志查看

```bash
# 查看应用日志
tail -f ~/.streamlit/logs/streamlit.log

# 查看自动化更新日志
tail -f auto_update.log
```

## 📈 性能优化

### 1. 代码优化

- 使用`@st.cache_data`缓存数据
- 优化数据加载逻辑
- 减少不必要的计算

### 2. 数据优化

- 定期清理历史数据
- 压缩数据文件
- 使用增量更新

### 3. 部署优化

- 使用CDN加速
- 优化镜像大小
- 配置缓存策略

## 🎯 最佳实践

### 1. 代码规范

- 使用清晰的变量名
- 添加适当的注释
- 遵循PEP 8规范

### 2. 提交规范

```
格式: <类型>: <描述>

类型:
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

示例:
feat: 添加新的风险指标计算
fix: 修复数据加载失败问题
docs: 更新部署指南
```

### 3. 测试规范

- 每次提交前进行测试
- 保持测试覆盖率
- 定期进行集成测试

## 📞 支持

如果遇到问题：

1. 查看日志文件
2. 检查GitHub Issues
3. 联系技术支持
4. 查看项目文档

---

**记住：** 开发是一个迭代过程，持续改进和优化是关键！ 