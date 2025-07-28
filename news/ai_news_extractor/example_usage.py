#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻提取器使用示例
"""

from .AInews import main, extract_from_specific_url, get_yesterday_link, extract_ai_news_content
from selenium import webdriver

def example_1_get_yesterday_news():
    """示例1: 获取昨日新闻"""
    print("=" * 60)
    print("示例1: 获取昨日新闻")
    print("=" * 60)
    
    # 直接运行主函数
    main()

def example_2_extract_specific_url():
    """示例2: 提取指定URL的新闻"""
    print("\n" + "=" * 60)
    print("示例2: 提取指定URL的新闻")
    print("=" * 60)
    
    # 指定URL和日期
    url = "https://news.smol.ai/issues/25-07-23-not-much"
    date_text = "Jul 23, 2025"
    
    extract_from_specific_url(url, date_text)

def example_3_custom_extraction():
    """示例3: 自定义提取过程"""
    print("\n" + "=" * 60)
    print("示例3: 自定义提取过程")
    print("=" * 60)
    
    driver = webdriver.Chrome()
    base_url = "https://news.smol.ai"
    
    try:
        # 1. 获取昨日链接
        print("获取昨日链接...")
        yesterday_link, date_text = get_yesterday_link(driver, base_url)
        
        if yesterday_link:
            print(f"找到链接: {yesterday_link}")
            
            # 2. 提取内容
            print("提取新闻内容...")
            news_sections = extract_ai_news_content(driver, yesterday_link)
            
            # 3. 自定义处理
            print(f"\n提取到的部分:")
            for section_name, content in news_sections.items():
                print(f"- {section_name}: {len(content)} 字符")
                
                # 可以在这里添加自定义处理逻辑
                # 比如只提取包含特定关键词的内容
                if "Qwen" in content or "Claude" in content:
                    print(f"  ⭐ 包含重要关键词!")
        
    finally:
        driver.quit()

def example_4_batch_processing():
    """示例4: 批量处理多个URL"""
    print("\n" + "=" * 60)
    print("示例4: 批量处理多个URL")
    print("=" * 60)
    
    # 示例URL列表（实际使用时需要真实的URL）
    urls_to_process = [
        ("https://news.smol.ai/issues/25-07-23-not-much", "Jul 23"),
        # 可以添加更多URL
    ]
    
    for url, date in urls_to_process:
        print(f"\n处理: {date}")
        try:
            extract_from_specific_url(url, date)
        except Exception as e:
            print(f"处理失败: {e}")

if __name__ == "__main__":
    print("AI新闻提取器使用示例")
    print("请选择要运行的示例:")
    print("1. 获取昨日新闻")
    print("2. 提取指定URL的新闻")
    print("3. 自定义提取过程")
    print("4. 批量处理多个URL")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        example_1_get_yesterday_news()
    elif choice == "2":
        example_2_extract_specific_url()
    elif choice == "3":
        example_3_custom_extraction()
    elif choice == "4":
        example_4_batch_processing()
    else:
        print("无效选择，运行默认示例...")
        example_1_get_yesterday_news() 