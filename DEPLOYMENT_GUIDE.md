# AGIX Fund Monitor v3 部署指南

## 项目概述

AGIX Fund Monitor v3 是一个基于Streamlit的基金监控和分析平台，提供实时性能分析、风险评估和投资组合分析功能。

## 部署方案选择

### 1. 本地部署（推荐用于开发和测试）

**优点：**
- 简单快速
- 完全控制数据
- 无需网络依赖

**缺点：**
- 无法远程访问
- 需要本地维护

### 2. Streamlit Cloud部署（推荐用于生产）

**优点：**
- 免费托管
- 自动部署
- 易于管理

**缺点：**
- 需要处理数据同步问题
- 有资源限制

### 3. 云服务器部署（推荐用于企业级）

**优点：**
- 完全控制
- 高性能
- 可扩展

**缺点：**
- 成本较高
- 需要运维知识

## 详细部署步骤

### 方案一：本地部署

#### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd v3

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2. 数据准备

```bash
# 运行数据采集管道
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..
```

#### 3. 启动应用

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

### 方案二：Streamlit Cloud部署

#### 1. 准备GitHub仓库

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 推送到GitHub
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### 2. 数据同步准备

由于Streamlit Cloud无法直接运行数据采集脚本，需要预先准备数据：

```bash
# 在本地运行数据同步脚本
python data_sync.py --action sync

# 将生成的JSON文件上传到GitHub
git add data/*.json
git commit -m "Add data files"
git push
```

#### 3. 部署到Streamlit Cloud

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用GitHub账号登录
3. 选择你的仓库
4. 设置部署配置：
   - **Main file path**: `app_cloud.py`
   - **Python version**: 3.9
   - **Requirements file**: `requirements.txt`

#### 4. 配置环境变量（可选）

在Streamlit Cloud中设置以下环境变量：
- `STREAMLIT_SERVER_PORT`: 8501
- `STREAMLIT_SERVER_HEADLESS`: true

### 方案三：Docker部署

#### 1. 构建Docker镜像

```bash
# 构建镜像
docker build -t agix-monitor .

# 运行容器
docker run -p 8501:8501 agix-monitor
```

#### 2. 使用Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方案四：云服务器部署

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install python3 python3-pip python3-venv nginx -y

# 安装Docker（可选）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### 2. 应用部署

```bash
# 克隆项目
git clone <your-repo-url>
cd v3

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据管道
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..

# 启动应用
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

#### 3. 配置Nginx反向代理

创建Nginx配置文件 `/etc/nginx/sites-available/agix-monitor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/agix-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. 配置SSL证书（可选）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

## 数据管理

### 数据更新策略

#### 1. 手动更新

```bash
# 运行数据采集管道
cd pipeline
python data_fetcher.py
python data_processor.py
cd ..

# 重启应用
pkill -f streamlit
streamlit run app.py
```

#### 2. 自动更新（Cron任务）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每日上午9点更新）
0 9 * * * cd /path/to/v3 && source venv/bin/activate && cd pipeline && python data_fetcher.py && python data_processor.py
```

#### 3. 云端数据同步

```bash
# 同步数据到云端
python data_sync.py --action sync

# 从云端恢复数据
python data_sync.py --action restore
```

### 数据备份

#### 1. 本地备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/agix-monitor"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据文件
tar -czf $BACKUP_DIR/data_$DATE.tar.gz source_data/ processed_data/ holdings/

# 保留最近30天的备份
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup.sh
```

#### 2. 云端备份

```bash
# 上传到云存储
python data_sync.py --action upload --bucket your-bucket-name

# 从云存储下载
python data_sync.py --action download --bucket your-bucket-name
```

## 监控和维护

### 1. 应用监控

```bash
# 检查应用状态
ps aux | grep streamlit

# 查看日志
tail -f ~/.streamlit/logs/streamlit.log

# 检查端口占用
netstat -tlnp | grep 8501
```

### 2. 性能监控

```bash
# 监控系统资源
htop

# 监控磁盘使用
df -h

# 监控内存使用
free -h
```

### 3. 日志管理

```bash
# 配置日志轮转
sudo logrotate -f /etc/logrotate.conf

# 查看应用日志
journalctl -u streamlit -f
```

## 故障排除

### 常见问题

#### 1. 数据加载失败

**症状：** 应用显示"数据不可用"错误

**解决方案：**
```bash
# 检查数据文件是否存在
ls -la source_data/ processed_data/

# 重新运行数据管道
cd pipeline
python data_fetcher.py
python data_processor.py
```

#### 2. 依赖包安装失败

**症状：** pip安装时出现错误

**解决方案：**
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --no-cache-dir
```

#### 3. 端口被占用

**症状：** 启动时提示端口8501被占用

**解决方案：**
```bash
# 查找占用端口的进程
lsof -i :8501

# 杀死进程
kill -9 <PID>

# 或使用不同端口
streamlit run app.py --server.port=8502
```

#### 4. 内存不足

**症状：** 应用运行缓慢或崩溃

**解决方案：**
```bash
# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 优化Streamlit配置
echo "server.maxUploadSize = 200" >> .streamlit/config.toml
```

## 安全考虑

### 1. 网络安全

- 使用HTTPS协议
- 配置防火墙规则
- 定期更新系统和依赖包

### 2. 数据安全

- 定期备份重要数据
- 加密敏感信息
- 限制数据访问权限

### 3. 应用安全

- 使用强密码
- 启用双因素认证
- 监控异常访问

## 扩展和定制

### 1. 添加新功能

- 在`app.py`中添加新的页面
- 在`pipeline/`中添加数据处理逻辑
- 在`visualizer.py`中添加新的图表

### 2. 自定义主题

编辑`.streamlit/config.toml`文件：

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### 3. 性能优化

- 使用`@st.cache_data`缓存数据
- 优化数据库查询
- 使用CDN加速静态资源

## 联系和支持

如果在部署过程中遇到问题，请：

1. 查看项目文档
2. 检查日志文件
3. 提交Issue到GitHub仓库
4. 联系技术支持

---

**注意：** 本指南基于当前版本的项目结构编写，如有更新请参考最新的项目文档。 