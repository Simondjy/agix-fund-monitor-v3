# AI新闻提取器

这是一个专门用于提取 [Smol AI News](https://news.smol.ai) 网站AI新闻内容的工具。它能够自动获取昨日的AI新闻链接，并提取其中的Twitter Recap、Reddit Recap、Discord Recap等各个部分的内容。

## 功能特性

- 🔍 **自动获取昨日新闻**: 自动识别并获取昨日的AI新闻链接
- 📰 **内容提取**: 提取AI Twitter Recap、AI Reddit Recap、AI Discord Recap等部分
- 💾 **内容保存**: 将提取的内容保存为JSON格式文件
- 🎯 **指定URL处理**: 支持直接处理指定的新闻URL
- 📊 **格式化输出**: 美观的控制台输出，包含内容长度统计
- 🔧 **灵活配置**: 支持自定义内容提取和处理逻辑

## 安装依赖

```bash
pip install selenium
```

确保已安装Chrome浏览器和ChromeDriver。

## 使用方法

### 1. 获取昨日新闻

```bash
# 从news目录运行
python run_ai_news_extractor.py

# 或者直接进入ai_news_extractor目录运行
cd ai_news_extractor
python AInews.py
```

这将自动获取昨日的AI新闻链接并提取内容。

### 2. 处理指定URL

```bash
# 从news目录运行
python run_ai_news_extractor.py "https://news.smol.ai/issues/25-07-23-not-much" "Jul 23"

# 或者直接进入ai_news_extractor目录运行
cd ai_news_extractor
python AInews.py "https://news.smol.ai/issues/25-07-23-not-much" "Jul 23"
```

### 3. 使用示例脚本

```bash
# 从news目录运行
python run_example.py

# 或者直接进入ai_news_extractor目录运行
cd ai_news_extractor
python example_usage.py
```

然后选择要运行的示例：
- 1: 获取昨日新闻
- 2: 提取指定URL的新闻
- 3: 自定义提取过程
- 4: 批量处理多个URL

## 输出格式

### 控制台输出

```
============================================================
📰 Jul 23 AI新闻汇总
============================================================

📋 1. AI Reddit Recap
--------------------------------------------------
/r/LocalLlama + /r/localLLM Recap
1. Qwen3 and Qwen3-Coder Release Performance, Benchmarks, and User Experiences
2. Agentic Coding Model Face-offs: Kimi K2 vs Claude Sonnet 4
3. Governmental and Industry Initiatives for Open-Source AI and LLM Architectures
...

📊 内容长度: 505 字符
--------------------------------------------------

✅ 成功提取了 2 个新闻部分
新闻内容已保存到: data\ai_news_20250724.json
```

### JSON文件格式

```json
{
  "date": "Jul 23",
  "extracted_at": "2025-07-24T12:04:50.686830",
  "sections": {
    "AI Reddit Recap": "...",
    "AI Discord Recap": "..."
  },
  "total_sections": 2
}
```

## 主要函数

### `main()`
主函数，获取昨日新闻并提取内容。

### `get_yesterday_link(driver, base_url)`
获取昨日的新闻链接。

**参数:**
- `driver`: Selenium WebDriver实例
- `base_url`: 网站基础URL

**返回:**
- `(link, date_text)`: 链接和日期文本的元组

### `extract_ai_news_content(driver, url)`
提取指定URL的AI新闻内容。

**参数:**
- `driver`: Selenium WebDriver实例
- `url`: 要提取内容的URL

**返回:**
- `dict`: 包含各个部分内容的字典

### `extract_from_specific_url(url, date_text=None)`
从指定URL提取AI新闻内容。

**参数:**
- `url`: 要处理的URL
- `date_text`: 日期文本（可选）

### `save_news_to_file(sections, date_text, filename=None)`
保存新闻内容到JSON文件。

**参数:**
- `sections`: 新闻内容字典
- `date_text`: 日期文本
- `filename`: 文件名（可选）

## 内容提取逻辑

1. **正则表达式匹配**: 使用多种模式匹配AI Twitter Recap、AI Reddit Recap、AI Discord Recap等部分
2. **DOM结构解析**: 如果正则表达式匹配失败，尝试使用DOM结构解析
3. **备用方案**: 如果以上方法都失败，提取整个页面的主要文本内容

## 文件结构

```
news/
├── ai_news_extractor/           # AI新闻提取器主目录
│   ├── __init__.py             # 包初始化文件
│   ├── AInews.py               # 主程序文件
│   ├── example_usage.py        # 使用示例
│   ├── README.md               # 说明文档
│   └── data/                   # 数据存储目录
│       └── ai_news_*.json      # 生成的新闻文件
├── run_ai_news_extractor.py    # 主运行脚本
├── run_example.py              # 示例运行脚本
└── HoldingsCompanyNews.py      # 其他新闻相关文件
```

## 注意事项

1. 确保网络连接正常
2. 需要安装Chrome浏览器和ChromeDriver
3. 某些网站可能有反爬虫机制，建议适当调整等待时间
4. 提取的内容长度可能因页面结构而异
5. 文件会保存在 `ai_news_extractor/data/` 目录下

## 扩展功能

你可以基于这个工具进行以下扩展：

1. **关键词过滤**: 只提取包含特定关键词的内容
2. **内容分析**: 对提取的内容进行情感分析或主题分类
3. **定时任务**: 设置定时任务自动获取每日新闻
4. **数据库存储**: 将提取的内容存储到数据库中
5. **API接口**: 创建Web API接口供其他应用调用

## 故障排除

### 常见问题

1. **ChromeDriver错误**: 确保ChromeDriver版本与Chrome浏览器版本匹配
2. **网络超时**: 增加等待时间或检查网络连接
3. **内容提取失败**: 检查网站结构是否发生变化，可能需要更新选择器
4. **路径错误**: 确保在正确的目录下运行脚本

### 调试模式

可以在代码中添加更多的调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

本项目仅供学习和研究使用。 