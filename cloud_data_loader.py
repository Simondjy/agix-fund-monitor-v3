"""
云端数据加载模块
用于在云端部署环境中加载和管理数据
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit as st

class CloudDataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.cache = {}
        
    def load_json_data(self, filename):
        """从JSON文件加载数据"""
        filepath = self.data_dir / filename
        
        if filename in self.cache:
            return self.cache[filename]
            
        if not filepath.exists():
            st.error(f"数据文件不存在: {filename}")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 转换为DataFrame
            df = pd.DataFrame(data['data'], columns=data['columns'])
            if data['index']:
                df.index = data['index']
            
            # 对于市场数据文件，确保数值列被正确转换为数值类型
            if 'market_data_closes' in filename or 'market_data_volumes' in filename:
                # 将Date列设置为索引
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                
                # 将所有数值列转换为float类型
                numeric_columns = df.select_dtypes(include=['object']).columns
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
            self.cache[filename] = df
            return df
        except Exception as e:
            st.error(f"加载数据失败 {filename}: {e}")
            return None
            
    def load_all_data(self):
        """加载所有必要的数据文件"""
        data_files = {
            'returns': 'returns.json',
            'risk_metrics': 'risk_metrics.json', 
            'volume_analysis': 'volume_analysis.json',
            'market_closes': 'market_data_closes.json',
            'market_volumes': 'market_data_volumes.json',
            'holdings_tickers': 'holdings_tickers.json',
            'holdings_info': 'holdings_info.json',
            'sector_analysis': 'holdings_sectorAnalysis.json',
            'country_analysis': 'holdings_countryAnalysis.json'
        }
        
        data = {}
        for key, filename in data_files.items():
            df = self.load_json_data(filename)
            if df is not None:
                data[key] = df
                
        return data
        
    def get_data_status(self):
        """获取数据状态信息"""
        status = {}
        data_files = [
            'returns.json', 'risk_metrics.json', 'volume_analysis.json',
            'market_data_closes.json', 'market_data_volumes.json',
            'holdings_tickers.json', 'holdings_info.json',
            'holdings_sectorAnalysis.json', 'holdings_countryAnalysis.json'
        ]
        
        for filename in data_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                status[filename] = {
                    'exists': True,
                    'last_modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                    'size': filepath.stat().st_size
                }
            else:
                status[filename] = {'exists': False}
                
        return status

# 全局数据加载器实例
@st.cache_resource
def get_data_loader():
    """获取数据加载器实例（使用Streamlit缓存）"""
    return CloudDataLoader()

def load_application_data():
    """加载应用所需的所有数据"""
    loader = get_data_loader()
    data = loader.load_all_data()
    
    # 检查必要的数据是否存在
    required_data = ['returns', 'risk_metrics', 'volume_analysis', 'market_closes', 'market_volumes']
    missing_data = [key for key in required_data if key not in data]
    
    if missing_data:
        st.error(f"缺少必要的数据文件: {missing_data}")
        st.info("请确保数据文件已正确上传到云端")
        return None
        
    return data

def display_data_status():
    """显示数据状态"""
    loader = get_data_loader()
    status = loader.get_data_status()
    
    st.subheader("📊 数据状态")
    
    # 统计信息
    total_files = len(status)
    existing_files = sum(1 for info in status.values() if info['exists'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总文件数", total_files)
    with col2:
        st.metric("可用文件数", existing_files)
    with col3:
        st.metric("完整度", f"{existing_files/total_files*100:.1f}%")
    
    # 详细状态
    with st.expander("查看详细状态"):
        for filename, info in status.items():
            if info['exists']:
                st.success(f"✅ {filename} - {info['last_modified']} ({info['size']} bytes)")
            else:
                st.error(f"❌ {filename} - 文件不存在")

# 兼容性函数，用于替换原有的数据加载逻辑
def load_returns_data():
    """加载收益率数据"""
    loader = get_data_loader()
    return loader.load_json_data('returns.json')

def load_risk_metrics_data():
    """加载风险指标数据"""
    loader = get_data_loader()
    return loader.load_json_data('risk_metrics.json')

def load_volume_analysis_data():
    """加载成交量分析数据"""
    loader = get_data_loader()
    return loader.load_json_data('volume_analysis.json')

def load_market_closes_data():
    """加载收盘价数据"""
    loader = get_data_loader()
    return loader.load_json_data('market_data_closes.json')

def load_market_volumes_data():
    """加载成交量数据"""
    loader = get_data_loader()
    return loader.load_json_data('market_data_volumes.json')

def load_sector_analysis_data():
    """加载行业分析数据"""
    loader = get_data_loader()
    return loader.load_json_data('holdings_sectorAnalysis.json')

def load_country_analysis_data():
    """加载国家分析数据"""
    loader = get_data_loader()
    return loader.load_json_data('holdings_countryAnalysis.json') 