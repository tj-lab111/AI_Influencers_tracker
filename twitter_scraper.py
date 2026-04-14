#!/usr/bin/env python3
"""
Twitter AI Influencers Tracker
使用 Playwright 浏览器自动化抓取 AI 大牛的推文，并推送到飞书

GitHub Actions 自动运行版本
"""

import asyncio
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ============ 配置区域 ============

INFLUENCERS = [
    # AI 研究领袖
    {"name": "Sam Altman", "handle": "sama", "desc": "OpenAI CEO"},
    {"name": "Elon Musk", "handle": "elonmusk", "desc": "xAI 创始人"},
    {"name": "Demis Hassabis", "handle": "demishassabis", "desc": "DeepMind CEO"},
    {"name": "Yann LeCun", "handle": "ylecun", "desc": "Meta AI 首席科学家"},
    {"name": "Andrej Karpathy", "handle": "karpathy", "desc": "AI 教育网红"},
    {"name": "Ilya Sutskever", "handle": "ilyasut", "desc": "OpenAI 联合创始人"},
    
    # 架构创新者
    {"name": "Ashish Vaswani", "handle": "avaswani", "desc": "Transformer 作者"},
    {"name": "Aidan Gomez", "handle": "aidangomez", "desc": "Cohere CEO"},
    
    # 开源 AI
    {"name": "Clement Delangue", "handle": "clementdelangue", "desc": "Hugging Face CEO"},
    {"name": "Thomas Wolf", "handle": "Thom_Wolf", "desc": "Hugging Face 联合创始人"},
    
    # AI 研究
    {"name": "Jim Fan", "handle": "DrJimFan", "desc": "NVIDIA 高级科学家"},
    
    # AI 媒体
    {"name": "Rowan Cheung", "handle": "rowancheung", "desc": "The Rundown AI"},
    {"name": "Matt Shumer", "handle": "mshumer_", "desc": "AI 产品开发者"},
]

OUTPUT_DIR = Path("reports")
MAX_TWEETS_PER_USER = 5
DELAY_BETWEEN_USERS = 2

# ============ 飞书推送 ============

def send_to_feishu(webhook_url: str, content: str):
    """发送消息到飞书"""
    if not webhook_url:
        print("⚠️ 未配置 FEISHU_WEBHOOK，跳过推送")
        return False
    
    # 飞书消息格式
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🐦 AI 大牛 Twitter 动态日报 - {datetime.now().strftime('%Y-%m-%d')}"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content[:30000]  # 飞书限制
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") == 0:
                print("✅ 飞书推送成功")
                return True
            else:
                print(f"❌ 飞书推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 飞书推送错误: {e}")
        return False


def generate_feishu_content(data: dict) -> str:
    """ ▉
