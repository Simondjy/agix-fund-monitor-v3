# sentiment_analyzer.py
# 使用Hugging Face预训练模型进行情感分析

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd

class SentimentAnalyzer:
    def __init__(self, model_name="ProsusAI/finbert"):
        """
        初始化情感分析器
        model_name: 预训练模型名称
        """
        self.model_name = model_name
        self.analyzer = None
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        """加载预训练模型"""
        try:
            print(f"🔄 正在加载模型: {self.model_name}")
            
            # 使用pipeline方式（最简单）
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name
            )
            
            print("✅ 模型加载成功！")
            return True
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False
    
    def analyze_text(self, text):
        """分析单个文本的情感"""
        if not self.analyzer:
            print("❌ 模型未加载，请先调用 load_model()")
            return None
        
        try:
            # 限制文本长度（避免token过长）
            if len(text) > 500:
                text = text[:500] + "..."
            
            result = self.analyzer(text)
            return result[0]
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return None
    
    def analyze_news_batch(self, news_list):
        """批量分析新闻情感"""
        if not self.analyzer:
            print("❌ 模型未加载，请先调用 load_model()")
            return []
        
        results = []
        
        for i, news in enumerate(news_list):
            print(f"📊 正在分析第 {i+1}/{len(news_list)} 条新闻...")
            
            # 分析标题和摘要
            title_sentiment = self.analyze_text(news.get('title', ''))
            summary_sentiment = self.analyze_text(news.get('summary', ''))
            
            # 综合情感（简单平均）
            combined_sentiment = self._combine_sentiments(title_sentiment, summary_sentiment)
            
            results.append({
                'ticker': news.get('ticker', ''),
                'title': news.get('title', ''),
                'title_sentiment': title_sentiment,
                'summary_sentiment': summary_sentiment,
                'combined_sentiment': combined_sentiment
            })
        
        return results
    
    def _combine_sentiments(self, title_sent, summary_sent):
        """合并标题和摘要的情感"""
        if not title_sent and not summary_sent:
            return {'label': 'neutral', 'score': 0.5}
        
        # 简单的情感合并逻辑
        sentiments = []
        if title_sent:
            sentiments.append(title_sent)
        if summary_sent:
            sentiments.append(summary_sent)
        
        # 计算平均情感
        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        
        # 根据分数确定标签
        if avg_score > 0.6:
            label = 'positive'
        elif avg_score < 0.4:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {'label': label, 'score': avg_score}
    
    def save_results(self, results, output_file="news/sentiment_analysis.csv"):
        """保存情感分析结果"""
        try:
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"✅ 情感分析结果已保存到: {output_file}")
            
            # 显示统计信息
            if not df.empty:
                print("\n📊 情感分析统计:")
                sentiment_counts = df['combined_sentiment'].apply(lambda x: x['label'] if isinstance(x, dict) else 'unknown').value_counts()
                for sentiment, count in sentiment_counts.items():
                    print(f"  {sentiment}: {count} 条")
        
        except Exception as e:
            print(f"❌ 保存失败: {e}")

def main():
    """主函数 - 演示如何使用"""
    
    # 创建情感分析器
    analyzer = SentimentAnalyzer("ProsusAI/finbert")
    
    # 加载模型
    if not analyzer.load_model():
        return
    
    # 测试文本
    test_texts = [
        "Apple reports record-breaking quarterly earnings, exceeding analyst expectations",
        "Tesla stock plunges after disappointing delivery numbers",
        "Market remains stable as investors await Fed decision",
        "Company announces major layoffs and restructuring plan",
        "Innovative product launch drives strong customer adoption"
    ]
    
    print("\n🧪 测试情感分析:")
    for i, text in enumerate(test_texts, 1):
        result = analyzer.analyze_text(text)
        if result:
            print(f"  {i}. {text[:50]}...")
            print(f"     情感: {result['label']} (置信度: {result['score']:.3f})")
    
    # 如果有新闻数据，可以分析新闻
    try:
        news_df = pd.read_csv("news/holdings_news.csv")
        if not news_df.empty:
            print(f"\n📰 分析 {len(news_df)} 条新闻的情感...")
            news_list = news_df.to_dict('records')
            results = analyzer.analyze_news_batch(news_list)
            analyzer.save_results(results)
    except FileNotFoundError:
        print("📝 未找到新闻文件，跳过新闻分析")

if __name__ == "__main__":
    main() 