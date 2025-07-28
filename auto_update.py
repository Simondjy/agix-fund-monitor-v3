#!/usr/bin/env python3
"""
自动化数据更新和部署脚本
用于每日自动更新数据并部署到云端
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log'),
        logging.StreamHandler()
    ]
)

class AutoUpdater:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.logger = logging.getLogger(__name__)
        
    def run_command(self, command, description=""):
        """运行命令并记录日志"""
        self.logger.info(f"开始执行: {description}")
        self.logger.info(f"命令: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.project_dir
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ {description} 成功")
                if result.stdout:
                    self.logger.info(f"输出: {result.stdout}")
                return True
            else:
                self.logger.error(f"❌ {description} 失败")
                self.logger.error(f"错误: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ {description} 异常: {e}")
            return False
    
    def check_git_status(self):
        """检查Git状态"""
        self.logger.info("检查Git状态...")
        
        # 检查是否有未提交的更改
        result = subprocess.run(
            "git status --porcelain", 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=self.project_dir
        )
        
        if result.stdout.strip():
            self.logger.warning("发现未提交的更改，请先提交或暂存")
            return False
        return True
    
    def update_data(self):
        """更新数据"""
        self.logger.info("开始更新数据...")
        
        # 1. 更新持仓数据
        if not self.run_command(
            "python pipeline/data_fetcher.py",
            "更新持仓和市场数据"
        ):
            return False
        
        # 2. 处理数据
        if not self.run_command(
            "python pipeline/data_processor.py", 
            "处理数据并生成分析结果"
        ):
            return False
        
        # 3. 同步数据到云端格式
        if not self.run_command(
            "python data_sync.py --action sync",
            "同步数据到云端格式"
        ):
            return False
        
        self.logger.info("✅ 数据更新完成")
        return True
    
    def test_application(self):
        """测试应用"""
        self.logger.info("开始测试应用...")
        
        # 启动应用进行测试
        test_process = subprocess.Popen(
            "streamlit run app_cloud.py --server.headless true --server.port 8502",
            shell=True,
            cwd=self.project_dir
        )
        
        # 等待应用启动
        time.sleep(10)
        
        try:
            # 检查应用是否正常运行
            import requests
            response = requests.get("http://localhost:8502", timeout=10)
            
            if response.status_code == 200:
                self.logger.info("✅ 应用测试通过")
                test_process.terminate()
                return True
            else:
                self.logger.error(f"❌ 应用测试失败: {response.status_code}")
                test_process.terminate()
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 应用测试异常: {e}")
            test_process.terminate()
            return False
    
    def commit_and_push(self, commit_message):
        """提交并推送代码"""
        self.logger.info("开始提交和推送代码...")
        
        # 1. 添加所有更改
        if not self.run_command(
            "git add .",
            "添加文件到暂存区"
        ):
            return False
        
        # 2. 提交更改
        if not self.run_command(
            f'git commit -m "{commit_message}"',
            "提交代码更改"
        ):
            return False
        
        # 3. 推送到远程仓库
        if not self.run_command(
            "git push origin main",
            "推送到GitHub"
        ):
            return False
        
        self.logger.info("✅ 代码推送完成")
        return True
    
    def full_update_process(self, test_mode=False):
        """完整的更新流程"""
        self.logger.info("=" * 50)
        self.logger.info("开始自动化更新流程")
        self.logger.info("=" * 50)
        
        # 1. 检查Git状态
        if not self.check_git_status():
            self.logger.error("Git状态检查失败，终止更新")
            return False
        
        # 2. 更新数据
        if not self.update_data():
            self.logger.error("数据更新失败，终止更新")
            return False
        
        # 3. 测试应用（可选）
        if test_mode:
            if not self.test_application():
                self.logger.error("应用测试失败，终止更新")
                return False
        
        # 4. 提交和推送
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Auto update: {timestamp} - 更新数据和代码"
        
        if not self.commit_and_push(commit_message):
            self.logger.error("代码推送失败")
            return False
        
        self.logger.info("=" * 50)
        self.logger.info("✅ 自动化更新流程完成")
        self.logger.info("Streamlit Cloud将自动重新部署")
        self.logger.info("=" * 50)
        return True
    
    def schedule_update(self, hour=9, minute=0):
        """设置定时更新"""
        self.logger.info(f"设置定时更新: 每天 {hour}:{minute:02d}")
        
        # 创建定时任务脚本
        script_content = f"""#!/bin/bash
cd {self.project_dir}
python auto_update.py --full-update
"""
        
        script_path = self.project_dir / "update_script.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        # 创建crontab条目
        cron_entry = f"{minute} {hour} * * * {script_path}"
        
        self.logger.info(f"Cron条目: {cron_entry}")
        self.logger.info("请手动添加到crontab: crontab -e")
        self.logger.info(f"或者运行: echo '{cron_entry}' | crontab -")

def main():
    parser = argparse.ArgumentParser(description="自动化数据更新和部署脚本")
    parser.add_argument("--full-update", action="store_true", help="执行完整更新流程")
    parser.add_argument("--update-data", action="store_true", help="仅更新数据")
    parser.add_argument("--test", action="store_true", help="测试应用")
    parser.add_argument("--schedule", action="store_true", help="设置定时更新")
    parser.add_argument("--hour", type=int, default=9, help="定时更新时间（小时）")
    parser.add_argument("--minute", type=int, default=0, help="定时更新时间（分钟）")
    
    args = parser.parse_args()
    
    updater = AutoUpdater()
    
    if args.full_update:
        updater.full_update_process(test_mode=True)
    elif args.update_data:
        updater.update_data()
    elif args.test:
        updater.test_application()
    elif args.schedule:
        updater.schedule_update(args.hour, args.minute)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 