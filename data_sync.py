#!/usr/bin/env python3
"""
数据同步脚本
用于云端部署时的数据管理和同步
"""

import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import argparse

class DataSync:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def save_data_to_json(self, data, filename):
        """将数据保存为JSON格式"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 数据已保存: {filepath}")
        
    def load_data_from_json(self, filename):
        """从JSON文件加载数据"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    def convert_csv_to_json(self, csv_path, json_filename):
        """将CSV文件转换为JSON格式"""
        if not Path(csv_path).exists():
            print(f"❌ CSV文件不存在: {csv_path}")
            return False
            
        try:
            df = pd.read_csv(csv_path)
            data = {
                'columns': df.columns.tolist(),
                'data': df.values.tolist(),
                'index': df.index.tolist() if df.index.name else None,
                'last_updated': datetime.now().isoformat()
            }
            self.save_data_to_json(data, json_filename)
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
            
    def convert_json_to_csv(self, json_filename, csv_path):
        """将JSON格式数据转换回CSV"""
        data = self.load_data_from_json(json_filename)
        if not data:
            print(f"❌ JSON文件不存在: {json_filename}")
            return False
            
        try:
            df = pd.DataFrame(data['data'], columns=data['columns'])
            if data['index']:
                df.index = data['index']
            df.to_csv(csv_path, index=True)
            print(f"✅ CSV文件已生成: {csv_path}")
            return True
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
            
    def sync_all_data(self):
        """同步所有数据文件"""
        print("🔄 开始同步所有数据文件...")
        
        # 需要同步的文件列表
        files_to_sync = [
            ('source_data/market_data_closes.csv', 'market_data_closes.json'),
            ('source_data/market_data_volumes.csv', 'market_data_volumes.json'),
            ('source_data/holdings_tickers.csv', 'holdings_tickers.json'),
            ('source_data/holdings_info.csv', 'holdings_info.json'),
            ('processed_data/returns.csv', 'returns.json'),
            ('processed_data/risk_metrics.csv', 'risk_metrics.json'),
            ('processed_data/volume_analysis.csv', 'volume_analysis.json'),
            ('processed_data/holdings_sectorAnalysis.csv', 'holdings_sectorAnalysis.json'),
            ('processed_data/holdings_countryAnalysis.csv', 'holdings_countryAnalysis.json')
        ]
        
        success_count = 0
        for csv_path, json_filename in files_to_sync:
            if self.convert_csv_to_json(csv_path, json_filename):
                success_count += 1
                
        print(f"✅ 同步完成: {success_count}/{len(files_to_sync)} 个文件")
        return success_count == len(files_to_sync)
        
    def restore_all_data(self):
        """恢复所有数据文件"""
        print("🔄 开始恢复所有数据文件...")
        
        # 需要恢复的文件列表
        files_to_restore = [
            ('market_data_closes.json', 'source_data/market_data_closes.csv'),
            ('market_data_volumes.json', 'source_data/market_data_volumes.csv'),
            ('holdings_tickers.json', 'source_data/holdings_tickers.csv'),
            ('holdings_info.json', 'source_data/holdings_info.csv'),
            ('returns.json', 'processed_data/returns.csv'),
            ('risk_metrics.json', 'processed_data/risk_metrics.csv'),
            ('volume_analysis.json', 'processed_data/volume_analysis.csv'),
            ('holdings_sectorAnalysis.json', 'processed_data/holdings_sectorAnalysis.csv'),
            ('holdings_countryAnalysis.json', 'processed_data/holdings_countryAnalysis.csv')
        ]
        
        # 创建必要的目录
        Path('source_data').mkdir(exist_ok=True)
        Path('processed_data').mkdir(exist_ok=True)
        
        success_count = 0
        for json_filename, csv_path in files_to_restore:
            if self.convert_json_to_csv(json_filename, csv_path):
                success_count += 1
                
        print(f"✅ 恢复完成: {success_count}/{len(files_to_restore)} 个文件")
        return success_count == len(files_to_restore)
        
    def upload_to_cloud_storage(self, bucket_name, credentials_file=None):
        """上传数据到云存储（示例：AWS S3）"""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            if credentials_file:
                session = boto3.Session(profile_name=credentials_file)
                s3 = session.client('s3')
            else:
                s3 = boto3.client('s3')
                
            # 上传所有JSON文件
            for json_file in self.data_dir.glob('*.json'):
                s3.upload_file(
                    str(json_file), 
                    bucket_name, 
                    f"agix-monitor-data/{json_file.name}"
                )
                print(f"✅ 已上传: {json_file.name}")
                
            return True
        except ImportError:
            print("❌ 需要安装 boto3: pip install boto3")
            return False
        except NoCredentialsError:
            print("❌ 需要配置AWS凭证")
            return False
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            return False
            
    def download_from_cloud_storage(self, bucket_name, credentials_file=None):
        """从云存储下载数据"""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            if credentials_file:
                session = boto3.Session(profile_name=credentials_file)
                s3 = session.client('s3')
            else:
                s3 = boto3.client('s3')
                
            # 列出所有JSON文件
            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix="agix-monitor-data/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.json'):
                        filename = obj['Key'].split('/')[-1]
                        s3.download_file(
                            bucket_name, 
                            obj['Key'], 
                            str(self.data_dir / filename)
                        )
                        print(f"✅ 已下载: {filename}")
                        
            return True
        except ImportError:
            print("❌ 需要安装 boto3: pip install boto3")
            return False
        except NoCredentialsError:
            print("❌ 需要配置AWS凭证")
            return False
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="AGIX Fund Monitor 数据同步工具")
    parser.add_argument("--action", choices=["sync", "restore", "upload", "download"], 
                       required=True, help="执行的操作")
    parser.add_argument("--data-dir", default="data", help="数据目录")
    parser.add_argument("--bucket", help="云存储桶名称")
    parser.add_argument("--credentials", help="AWS凭证文件")
    
    args = parser.parse_args()
    
    sync = DataSync(args.data_dir)
    
    if args.action == "sync":
        sync.sync_all_data()
    elif args.action == "restore":
        sync.restore_all_data()
    elif args.action == "upload":
        if not args.bucket:
            print("❌ 需要指定 --bucket 参数")
            sys.exit(1)
        sync.upload_to_cloud_storage(args.bucket, args.credentials)
    elif args.action == "download":
        if not args.bucket:
            print("❌ 需要指定 --bucket 参数")
            sys.exit(1)
        sync.download_from_cloud_storage(args.bucket, args.credentials)

if __name__ == "__main__":
    main() 