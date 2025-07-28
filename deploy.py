#!/usr/bin/env python3
"""
AGIX Fund Monitor v3 部署脚本
用于自动化部署流程，包括数据准备、环境检查和部署配置
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def install_dependencies():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def check_data_files():
    """检查必要的数据文件是否存在"""
    print("📊 检查数据文件...")
    required_files = [
        "source_data/market_data_closes.csv",
        "source_data/market_data_volumes.csv", 
        "source_data/holdings_tickers.csv",
        "processed_data/returns.csv",
        "processed_data/risk_metrics.csv",
        "processed_data/volume_analysis.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  缺少数据文件: {missing_files}")
        print("请先运行数据采集管道:")
        print("  cd pipeline")
        print("  python data_fetcher.py")
        print("  python data_processor.py")
        return False
    
    print("✅ 数据文件检查通过")
    return True

def run_data_pipeline():
    """运行数据采集管道"""
    print("🔄 运行数据采集管道...")
    try:
        # 运行数据采集
        subprocess.run([sys.executable, "pipeline/data_fetcher.py"], 
                      check=True, capture_output=True, text=True)
        print("✅ 数据采集完成")
        
        # 运行数据处理
        subprocess.run([sys.executable, "pipeline/data_processor.py"], 
                      check=True, capture_output=True, text=True)
        print("✅ 数据处理完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据管道运行失败: {e}")
        return False

def create_deployment_package():
    """创建部署包"""
    print("📦 创建部署包...")
    
    # 创建部署目录
    deploy_dir = Path("deployment")
    deploy_dir.mkdir(exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        "app.py",
        "visualizer.py", 
        "pdf_generator.py",
        "utils.py",
        "requirements.txt",
        "README.md"
    ]
    
    dirs_to_copy = [
        "pipeline",
        "source_data", 
        "processed_data",
        "holdings",
        ".streamlit"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, deploy_dir / file_name)
            print(f"  📄 复制文件: {file_name}")
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, deploy_dir / dir_name, dirs_exist_ok=True)
            print(f"  📁 复制目录: {dir_name}")
    
    print("✅ 部署包创建完成")
    return True

def test_streamlit_app():
    """测试Streamlit应用"""
    print("🧪 测试Streamlit应用...")
    try:
        # 启动Streamlit应用进行测试
        process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8502"])
        
        # 等待应用启动
        import time
        time.sleep(10)
        
        # 检查应用是否正常运行
        import requests
        try:
            response = requests.get("http://localhost:8502", timeout=5)
            if response.status_code == 200:
                print("✅ Streamlit应用测试通过")
                process.terminate()
                return True
            else:
                print(f"❌ 应用响应异常: {response.status_code}")
                process.terminate()
                return False
        except requests.RequestException:
            print("❌ 无法连接到Streamlit应用")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ 应用测试失败: {e}")
        return False

def generate_deployment_instructions():
    """生成部署说明"""
    instructions = """
# AGIX Fund Monitor v3 部署说明

## 本地部署

1. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

2. 运行数据管道:
   ```bash
   cd pipeline
   python data_fetcher.py
   python data_processor.py
   ```

3. 启动应用:
   ```bash
   streamlit run app.py
   ```

## 云端部署 (Streamlit Cloud)

1. 将代码推送到GitHub仓库
2. 在Streamlit Cloud中连接仓库
3. 设置部署配置:
   - Python版本: 3.8+
   - 依赖文件: requirements.txt
   - 主文件: app.py

## 云端部署 (其他平台)

### Heroku
1. 创建Procfile:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. 部署命令:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Docker
1. 创建Dockerfile:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. 构建和运行:
   ```bash
   docker build -t agix-monitor .
   docker run -p 8501:8501 agix-monitor
   ```

## 数据更新

设置定时任务更新数据:
```bash
# 每日更新数据
0 9 * * * cd /path/to/project && python pipeline/data_fetcher.py && python pipeline/data_processor.py
```

## 注意事项

1. 确保所有数据文件都已正确生成
2. 云端部署时需要定期更新数据
3. 监控应用性能和资源使用情况
4. 定期备份重要数据文件
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("✅ 部署说明已生成: DEPLOYMENT_GUIDE.md")

def main():
    parser = argparse.ArgumentParser(description="AGIX Fund Monitor v3 部署脚本")
    parser.add_argument("--skip-data", action="store_true", help="跳过数据管道运行")
    parser.add_argument("--test-only", action="store_true", help="仅运行测试")
    parser.add_argument("--create-package", action="store_true", help="仅创建部署包")
    
    args = parser.parse_args()
    
    print("🚀 AGIX Fund Monitor v3 部署脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    if args.test_only:
        # 仅测试模式
        if not check_data_files():
            sys.exit(1)
        if not test_streamlit_app():
            sys.exit(1)
        print("✅ 测试完成")
        return
    
    if args.create_package:
        # 仅创建部署包
        create_deployment_package()
        generate_deployment_instructions()
        print("✅ 部署包创建完成")
        return
    
    # 完整部署流程
    if not args.skip_data:
        if not run_data_pipeline():
            sys.exit(1)
    
    if not check_data_files():
        sys.exit(1)
    
    if not test_streamlit_app():
        sys.exit(1)
    
    create_deployment_package()
    generate_deployment_instructions()
    
    print("\n🎉 部署准备完成!")
    print("📋 请查看 DEPLOYMENT_GUIDE.md 获取详细部署说明")
    print("📦 部署包已创建在 deployment/ 目录中")

if __name__ == "__main__":
    main() 