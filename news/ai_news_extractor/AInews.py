from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from datetime import datetime, timedelta
import re

def save_news_to_file(sections, date_text, filename=None):
    """保存新闻内容到文件"""
    if not filename:
        # 生成文件名
        date_obj = datetime.now()
        filename = f"ai_news_{date_obj.strftime('%Y%m%d')}.json"
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    # 准备保存的数据
    news_data = {
        "date": date_text,
        "extracted_at": datetime.now().isoformat(),
        "sections": sections,
        "total_sections": len(sections)
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print(f"新闻内容已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return None

def format_content_for_display(content, max_length=800):
    """格式化内容用于显示"""
    if len(content) <= max_length:
        return content
    
    # 在句子边界截断
    truncated = content[:max_length]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    if last_period > last_newline and last_period > max_length * 0.8:
        return truncated[:last_period + 1] + "\n[内容过长，已截断]"
    elif last_newline > max_length * 0.8:
        return truncated[:last_newline] + "\n[内容过长，已截断]"
    else:
        return truncated + "\n[内容过长，已截断]"

def get_yesterday_link(driver, base_url):
    """获取昨日的新闻链接"""
    try:
        # 打开主页
        driver.get(base_url)
        
        # 等待内容加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.relative.md\\:pl-10"))
        )
        time.sleep(2)
        
        # 获取所有新闻条目
        news_items = driver.find_elements(By.CSS_SELECTOR, "li.relative.md\\:pl-10")
        
        # 获取昨日日期
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%m-%d")  # 格式如 "07-23"
        
        # 查找昨日链接
        for item in news_items:
            date_element = item.find_element(By.CSS_SELECTOR, "time")
            date_text = date_element.text
            
            # 检查是否是昨日
            if yesterday_str in date_text or "yesterday" in date_text.lower():
                link_element = item.find_element(By.CSS_SELECTOR, "a.block")
                relative_link = link_element.get_attribute("href")
                full_link = relative_link if relative_link.startswith("http") else base_url + relative_link
                return full_link, date_text
        
        # 如果没找到昨日，返回第一条
        if news_items:
            link_element = news_items[0].find_element(By.CSS_SELECTOR, "a.block")
            relative_link = link_element.get_attribute("href")
            full_link = relative_link if relative_link.startswith("http") else base_url + relative_link
            date_element = news_items[0].find_element(By.CSS_SELECTOR, "time")
            return full_link, date_element.text
            
    except Exception as e:
        print(f"获取昨日链接时出错: {e}")
        return None, None

def extract_from_specific_url(url, date_text=None):
    """从指定URL提取AI新闻内容"""
    driver = webdriver.Chrome()
    
    try:
        print(f"正在从指定URL提取内容: {url}")
        news_sections = extract_ai_news_content(driver, url)
        
        if not date_text:
            date_text = "指定日期"
        
        # 输出结果
        print(f"\n{'='*60}")
        print(f"📰 {date_text} AI新闻汇总")
        print(f"{'='*60}")
        
        if not news_sections:
            print("❌ 未能提取到任何新闻内容")
            return
        
        for i, (section_name, content) in enumerate(news_sections.items(), 1):
            print(f"\n📋 {i}. {section_name}")
            print(f"{'-'*50}")
            
            # 格式化显示内容
            formatted_content = format_content_for_display(content)
            print(formatted_content)
            
            # 显示内容长度
            print(f"\n📊 内容长度: {len(content)} 字符")
            print("-" * 50)
        
        print(f"\n✅ 成功提取了 {len(news_sections)} 个新闻部分")
        
        # 保存到文件
        save_news_to_file(news_sections, date_text)
        
        return news_sections
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        return None
        
    finally:
        driver.quit()

def extract_ai_news_content(driver, url):
    """提取AI新闻页面的具体内容"""
    try:
        # 打开新闻页面
        driver.get(url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # 获取页面内容
        page_content = driver.find_element(By.TAG_NAME, "body").text
        
        # 提取主要部分
        sections = {}
        
        # 使用更精确的正则表达式提取各个部分
        # 提取AI Twitter Recap - 改进模式
        twitter_patterns = [
            r'AI Twitter Recap\s*(.*?)(?=\s*AI Reddit Recap|\s*AI Discord Recap|\s*Discord:|$)',
            r'Twitter Recap\s*(.*?)(?=\s*Reddit Recap|\s*Discord Recap|\s*Discord:|$)',
            r'Twitter\s*(.*?)(?=\s*Reddit|\s*Discord|$)'
        ]
        
        for pattern in twitter_patterns:
            twitter_match = re.search(pattern, page_content, re.DOTALL | re.IGNORECASE)
            if twitter_match:
                twitter_content = twitter_match.group(1).strip()
                if len(twitter_content) > 20:  # 确保内容有意义
                    sections['AI Twitter Recap'] = twitter_content
                    break
        
        # 提取AI Reddit Recap
        reddit_patterns = [
            r'AI Reddit Recap\s*(.*?)(?=\s*AI Discord Recap|\s*Discord:|$)',
            r'Reddit Recap\s*(.*?)(?=\s*Discord Recap|\s*Discord:|$)',
            r'Reddit\s*(.*?)(?=\s*Discord|$)'
        ]
        
        for pattern in reddit_patterns:
            reddit_match = re.search(pattern, page_content, re.DOTALL | re.IGNORECASE)
            if reddit_match:
                reddit_content = reddit_match.group(1).strip()
                if len(reddit_content) > 20:
                    sections['AI Reddit Recap'] = reddit_content
                    break
        
        # 提取AI Discord Recap
        discord_patterns = [
            r'AI Discord Recap\s*(.*?)(?=\s*AI Twitter Recap|\s*AI Reddit Recap|$)',
            r'Discord Recap\s*(.*?)(?=\s*Twitter Recap|\s*Reddit Recap|$)',
            r'Discord:\s*(.*?)(?=\s*Twitter|\s*Reddit|$)'
        ]
        
        for pattern in discord_patterns:
            discord_match = re.search(pattern, page_content, re.DOTALL | re.IGNORECASE)
            if discord_match:
                discord_content = discord_match.group(1).strip()
                if len(discord_content) > 20:
                    sections['AI Discord Recap'] = discord_content
                    break
        
        # 如果正则表达式没有找到足够的内容，尝试使用DOM结构
        if len(sections) < 2:
            print("使用DOM结构提取内容...")
            
            # 查找所有标题元素
            headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            
            for heading in headings:
                heading_text = heading.text.strip()
                if not heading_text:
                    continue
                
                # 检查是否是我们要找的标题
                if any(keyword in heading_text.lower() for keyword in 
                       ['twitter recap', 'reddit recap', 'discord recap', 'recap']):
                    
                    # 获取该标题下的内容
                    try:
                        # 方法1：查找下一个兄弟元素
                        parent = heading.find_element(By.XPATH, "..")
                        siblings = parent.find_elements(By.XPATH, "following-sibling::*")
                        
                        content_parts = []
                        for sibling in siblings[:10]:  # 限制查找范围
                            if sibling.tag_name in ['p', 'div', 'section']:
                                sibling_text = sibling.text.strip()
                                if sibling_text and len(sibling_text) > 10:
                                    content_parts.append(sibling_text)
                        
                        if content_parts:
                            sections[heading_text] = '\n\n'.join(content_parts)
                            
                    except Exception as e:
                        print(f"提取 {heading_text} 内容时出错: {e}")
                        continue
        
        # 如果还是没有足够内容，尝试提取整个页面的主要文本
        if len(sections) < 1:
            print("提取页面主要文本内容...")
            
            # 查找主要内容区域
            main_content = driver.find_elements(By.CSS_SELECTOR, "main, article, .content, .post-content")
            if main_content:
                main_text = main_content[0].text
                sections['完整内容'] = main_text[:2000] + "..." if len(main_text) > 2000 else main_text
            else:
                # 如果没有找到主要内容区域，使用body文本
                body_text = driver.find_element(By.TAG_NAME, "body").text
                sections['页面内容'] = body_text[:2000] + "..." if len(body_text) > 2000 else body_text
        
        return sections
        
    except Exception as e:
        print(f"提取新闻内容时出错: {e}")
        return {}

def main():
    # 初始化浏览器
    driver = webdriver.Chrome()
    base_url = "https://news.smol.ai"
    
    try:
        # 1. 获取昨日链接
        print("正在获取昨日新闻链接...")
        yesterday_link, date_text = get_yesterday_link(driver, base_url)
        
        if not yesterday_link:
            print("未能获取到昨日链接")
            return
        
        print(f"找到昨日链接: {yesterday_link}")
        print(f"日期: {date_text}")
        
        # 2. 提取新闻内容
        print("\n正在提取AI新闻内容...")
        news_sections = extract_ai_news_content(driver, yesterday_link)
        
        # 3. 输出结果
        print(f"\n{'='*60}")
        print(f"📰 {date_text} AI新闻汇总")
        print(f"{'='*60}")
        
        if not news_sections:
            print("❌ 未能提取到任何新闻内容")
            return
        
        for i, (section_name, content) in enumerate(news_sections.items(), 1):
            print(f"\n📋 {i}. {section_name}")
            print(f"{'-'*50}")
            
            # 格式化显示内容
            formatted_content = format_content_for_display(content)
            print(formatted_content)
            
            # 显示内容长度
            print(f"\n📊 内容长度: {len(content)} 字符")
            print("-" * 50)
        
        print(f"\n✅ 成功提取了 {len(news_sections)} 个新闻部分")
        
        # 4. 保存到文件
        save_news_to_file(news_sections, date_text)
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    # 可以选择运行主函数或直接处理指定URL
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了URL参数，直接处理该URL
        url = sys.argv[1]
        date_text = sys.argv[2] if len(sys.argv) > 2 else "指定日期"
        extract_from_specific_url(url, date_text)
    else:
        # 否则运行主函数获取昨日新闻
        main()