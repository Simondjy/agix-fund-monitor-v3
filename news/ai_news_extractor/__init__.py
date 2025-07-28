#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻提取器包
"""

from .AInews import (
    main,
    extract_from_specific_url,
    get_yesterday_link,
    extract_ai_news_content,
    save_news_to_file,
    format_content_for_display
)

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI新闻提取器 - 从Smol AI News网站提取AI相关新闻内容"

__all__ = [
    'main',
    'extract_from_specific_url',
    'get_yesterday_link',
    'extract_ai_news_content',
    'save_news_to_file',
    'format_content_for_display'
] 