#HoldingsCompanyNews

# 先读取Tickers.csv，然后在yahoo finance上获取每个公司的相关新闻，并输出csv

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import time
import os
import json
from typing import List, Dict, Optional
import sys
import traceback

class HoldingsCompanyNews:
    def __init__(self, tickers_file_path: str = "source_data/holdings_tickers.csv"):
        """
        初始化HoldingsCompanyNews类
        
        Args:
            tickers_file_path: tickers CSV文件路径
        """
        self.tickers_file_path = tickers_file_path
        self.tickers = []
        self.news_data = []
        self.output_dir = "company_news"
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_tickers(self) -> List[str]:
        """
        从CSV文件加载tickers
        
        Returns:
            ticker列表
        """
        try:
            df = pd.read_csv(self.tickers_file_path)
            self.tickers = df['Ticker'].tolist()
            print(f"成功加载 {len(self.tickers)} 个tickers")
            return self.tickers
        except Exception as e:
            print(f"加载tickers时出错: {e}")
            return []
    
    def get_company_info(self, ticker: str, max_retries: int = 3) -> Dict:
        """
        获取公司基本信息
        
        Args:
            ticker: 股票代码
            max_retries: 最大重试次数
            
        Returns:
            公司信息字典
        """
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                return {
                    'ticker': ticker,
                    'name': info.get('longName', info.get('shortName', 'Unknown')),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'country': info.get('country', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'website': info.get('website', 'Unknown')
                }
            except Exception as e:
                if "Too Many Requests" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间
                    print(f"获取 {ticker} 公司信息时遇到速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取 {ticker} 公司信息时出错: {e}")
                    return {
                        'ticker': ticker,
                        'name': 'Unknown',
                        'sector': 'Unknown',
                        'industry': 'Unknown',
                        'country': 'Unknown',
                        'market_cap': 0,
                        'website': 'Unknown'
                    }
    
    def get_yahoo_news(self, ticker: str, days_back: int = 7, max_retries: int = 3) -> List[Dict]:
        """
        从Yahoo Finance获取公司新闻
        
        Args:
            ticker: 股票代码
            days_back: 获取多少天前的新闻
            max_retries: 最大重试次数
            
        Returns:
            新闻列表
        """
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker)
                
                # 获取新闻
                news = stock.news
                
                if not news:
                    return []
                
                # 过滤最近几天的新闻
                cutoff_date = datetime.now() - timedelta(days=days_back)
                filtered_news = []
                
                for article in news:
                    try:
                        # 转换时间戳
                        pub_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                        
                        if pub_time >= cutoff_date:
                            filtered_news.append({
                                'ticker': ticker,
                                'title': article.get('title', ''),
                                'summary': article.get('summary', ''),
                                'link': article.get('link', ''),
                                'publisher': article.get('publisher', ''),
                                'publish_time': pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'provider_publish_time': article.get('providerPublishTime', 0),
                                'type': article.get('type', ''),
                                'uuid': article.get('uuid', '')
                            })
                    except Exception as e:
                        print(f"处理 {ticker} 新闻文章时出错: {e}")
                        continue
                
                print(f"为 {ticker} 获取到 {len(filtered_news)} 条新闻")
                return filtered_news
                
            except Exception as e:
                if "Too Many Requests" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间
                    print(f"获取 {ticker} 新闻时遇到速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"获取 {ticker} 新闻时出错: {e}")
                    return []
    
    def get_alternative_news(self, ticker: str, company_name: str) -> List[Dict]:
        """
        获取替代新闻源（当Yahoo Finance没有新闻时）
        
        Args:
            ticker: 股票代码
            company_name: 公司名称
            
        Returns:
            新闻列表
        """
        # 这里可以集成其他新闻API，如NewsAPI、Alpha Vantage等
        # 目前返回空列表，可以根据需要扩展
        return []
    
    def process_ticker(self, ticker: str) -> List[Dict]:
        """
        处理单个ticker的新闻获取
        
        Args:
            ticker: 股票代码
            
        Returns:
            该ticker的新闻列表
        """
        print(f"\n处理ticker: {ticker}")
        
        # 获取公司信息
        company_info = self.get_company_info(ticker)
        
        # 获取Yahoo Finance新闻
        yahoo_news = self.get_yahoo_news(ticker)
        
        # 如果没有Yahoo新闻，尝试其他来源
        if not yahoo_news:
            print(f"Yahoo Finance没有 {ticker} 的新闻，尝试其他来源...")
            yahoo_news = self.get_alternative_news(ticker, company_info['name'])
        
        # 添加公司信息到新闻数据
        for news in yahoo_news:
            news.update({
                'company_name': company_info['name'],
                'sector': company_info['sector'],
                'industry': company_info['industry'],
                'country': company_info['country'],
                'market_cap': company_info['market_cap'],
                'website': company_info['website']
            })
        
        return yahoo_news
    
    def save_to_csv(self, filename: str = None) -> str:
        """
        保存新闻数据到CSV文件
        
        Args:
            filename: 输出文件名
            
        Returns:
            保存的文件路径
        """
        if not self.news_data:
            print("没有新闻数据可保存")
            return ""
        
        if not filename:
            today = datetime.now().strftime('%Y%m%d')
            filename = f"holdings_company_news_{today}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df = pd.DataFrame(self.news_data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"新闻数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")
            return ""
    
    def save_to_json(self, filename: str = None) -> str:
        """
        保存新闻数据到JSON文件
        
        Args:
            filename: 输出文件名
            
        Returns:
            保存的文件路径
        """
        if not self.news_data:
            print("没有新闻数据可保存")
            return ""
        
        if not filename:
            today = datetime.now().strftime('%Y%m%d')
            filename = f"holdings_company_news_{today}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.news_data, f, ensure_ascii=False, indent=2)
            print(f"新闻数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存JSON文件时出错: {e}")
            return ""
    
    def run(self, days_back: int = 7, delay: float = 3.0) -> Dict:
        """
        运行完整的新闻获取流程
        
        Args:
            days_back: 获取多少天前的新闻
            delay: 请求之间的延迟（秒）
            
        Returns:
            处理结果统计
        """
        print("开始获取持仓公司新闻...")
        
        # 加载tickers
        tickers = self.load_tickers()
        if not tickers:
            return {"error": "无法加载tickers"}
        
        # 统计信息
        stats = {
            "total_tickers": len(tickers),
            "processed_tickers": 0,
            "successful_tickers": 0,
            "total_news": 0,
            "errors": []
        }
        
        # 处理每个ticker
        for i, ticker in enumerate(tickers, 1):
            try:
                print(f"\n进度: {i}/{len(tickers)} - 处理 {ticker}")
                
                # 获取新闻
                news_list = self.process_ticker(ticker)
                
                if news_list:
                    self.news_data.extend(news_list)
                    stats["successful_tickers"] += 1
                    stats["total_news"] += len(news_list)
                
                stats["processed_tickers"] += 1
                
                # 添加延迟避免请求过于频繁
                if i < len(tickers):
                    time.sleep(delay)
                    
            except Exception as e:
                error_msg = f"处理 {ticker} 时出错: {str(e)}"
                print(error_msg)
                stats["errors"].append(error_msg)
                continue
        
        # 保存结果
        if self.news_data:
            csv_path = self.save_to_csv()
            json_path = self.save_to_json()
            
            stats["csv_file"] = csv_path
            stats["json_file"] = json_path
        
        print(f"\n处理完成!")
        print(f"总tickers: {stats['total_tickers']}")
        print(f"成功处理: {stats['successful_tickers']}")
        print(f"总新闻数: {stats['total_news']}")
        print(f"错误数: {len(stats['errors'])}")
        
        return stats


def main():
    """
    主函数
    """
    # 创建新闻获取器实例
    news_getter = HoldingsCompanyNews()
    
    # 运行新闻获取 - 获取最近24小时的新闻
    stats = news_getter.run(days_back=1, delay=5.0)
    
    # 打印统计信息
    if "error" not in stats:
        print("\n=== 处理统计 ===")
        for key, value in stats.items():
            if key != "errors":
                print(f"{key}: {value}")
        
        if stats["errors"]:
            print(f"\n错误列表:")
            for error in stats["errors"]:
                print(f"- {error}")


if __name__ == "__main__":
    main()
