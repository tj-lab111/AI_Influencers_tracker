#!/usr/bin/env python3
"""
Twitter AI Influencers Tracker
使用 Playwright 浏览器自动化抓取 AI 大牛的最新推文，并推送到飞书

GitHub Actions 自动运行版本
支持 AI 摘要功能（OpenAI 兼容 API，包括智谱、DeepSeek 等）
"""

import asyncio
import json
import os
import urllib.request
import re
from datetime import datetime, timedelta
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

# 只抓取最近多少小时内的推文
MAX_TWEET_AGE_HOURS = 24

# AI 摘要配置（支持 OpenAI 兼容 API）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "glm-4-flash")  # 智谱默认模型

# ============ 时间解析 ============

def parse_tweet_time(time_str: str) -> datetime:
    """
    解析 Twitter 时间格式
    支持: "2h", "3m", "1d", "Apr 14", "Dec 25, 2023"
    """
    now = datetime.utcnow()
    
    if not time_str:
        return now - timedelta(days=365)
    
    time_str = time_str.strip().lower()
    
    # 相对时间: "2h", "3m", "1d"
    match = re.match(r'^(\d+)([hmd])$', time_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'm':
            return now - timedelta(minutes=num)
        elif unit == 'h':
            return now - timedelta(hours=num)
        elif unit == 'd':
            return now - timedelta(days=num)
    
    # 绝对时间: "Apr 14" 或 "Dec 25, 2023"
    try:
        if ',' in time_str:
            return datetime.strptime(time_str, '%b %d, %Y')
        else:
            parsed = datetime.strptime(time_str, '%b %d')
            return parsed.replace(year=now.year)
    except:
        pass
    
    return now - timedelta(days=365)


def is_recent_tweet(time_str: str, max_age_hours: int = MAX_TWEET_AGE_HOURS) -> bool:
    """检查推文是否在指定时间内"""
    tweet_time = parse_tweet_time(time_str)
    now = datetime.utcnow()
    age = now - tweet_time
    return age.total_seconds() <= max_age_hours * 3600


# ============ AI 摘要 ============

def generate_tweet_summary(tweet_text: str, author_name: str) -> dict:
    """
    使用 AI 生成推文摘要
    返回: {
        "summary": "一句话介绍",
        "key_data": ["数据1", "数据2"],
        "keywords": ["关键词1", "关键词2", "关键词3"]
    }
    """
    if not OPENAI_API_KEY:
        return {"summary": "", "key_data": [], "keywords": []}
    
    prompt = f"""分析这条来自 {author_name} 的推文，提取以下信息：

推文内容：
{tweet_text}

请以 JSON 格式返回（不要有其他内容）：
{{
    "summary": "一句话中文介绍这条推文的核心内容（20字以内）",
    "key_data": ["关键数据1（如有数字、指标等）", "关键数据2（没有则留空）"],
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}

注意：
- 如果推文中没有明确的数字/数据，key_data 可以为空数组
- 关键词要准确反映推文主题
- summary 要简洁有力"""

    try:
        data = {
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的推文分析助手，擅长提取关键信息。只返回 JSON，不要有其他内容。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        # 使用自定义 Base URL（支持智谱、DeepSeek 等）
        api_url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content'].strip()
            
            # 尝试解析 JSON
            # 有时 AI 会返回 ```json ... ```，需要清理
            if content.startswith('```'):
                content = content.split('\n', 1)[1]  # 去掉第一行
                content = content.rsplit('```', 1)[0]  # 去掉最后的 ```
            
            parsed = json.loads(content)
            return {
                "summary": parsed.get("summary", ""),
                "key_data": parsed.get("key_data", []),
                "keywords": parsed.get("keywords", [])
            }
            
    except Exception as e:
        print(f"  ⚠️ AI 摘要失败: {e}")
        return {"summary": "", "key_data": [], "keywords": []}


# ============ 飞书推送 ============

def send_to_feishu(webhook_url: str, content: str):
    """发送消息到飞书"""
    if not webhook_url:
        print("⚠️ 未配置 FEISHU_WEBHOOK，跳过推送")
        return False
    
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
                    "content": content[:30000]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC | 仅显示最近 {MAX_TWEET_AGE_HOURS} 小时内的推文"
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
    """生成飞书消息内容（带 AI 摘要）"""
    lines = []
    total_tweets = 0
    
    for influencer, tweets in data.items():
        if tweets:
            total_tweets += len(tweets)
            lines.append(f"### 🎯 {influencer}")
            lines.append("")
            
            for tweet in tweets:
                time_info = tweet.get('time', '')
                summary = tweet.get('summary', '')
                key_data = tweet.get('key_data', [])
                keywords = tweet.get('keywords', [])
                
                # 推文链接
                lines.append(f"**[{time_info}]** [查看原文]({tweet['url']})")
                
                # 一句话介绍
                if summary:
                    lines.append(f"> 💡 {summary}")
                
                # 关键数据
                if key_data and any(key_data):
                    data_str = " | ".join([d for d in key_data if d])
                    if data_str:
                        lines.append(f"📊 **关键数据**: {data_str}")
                
                # 关键词
                if keywords:
                    keywords_str = " ".join([f"`{k}`" for k in keywords])
                    lines.append(f"🏷️ **关键词**: {keywords_str}")
                
                # 互动数据
                lines.append(f"💬 {tweet.get('replies', 0)} | 🔁 {tweet.get('retweets', 0)} | ❤️ {tweet.get('likes', 0)}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    if total_tweets == 0:
        return f"**今日暂无新推文**\n\n在过去 {MAX_TWEET_AGE_HOURS} 小时内，所有监控的 AI 大牛都没有发布新推文。"
    
    header = f"📊 **今日统计**: 共 {total_tweets} 条新推文\n\n"
    return header + "\n".join(lines)


# ============ Twitter 抓取 ============

async def scrape_twitter():
    """使用 Playwright 抓取 Twitter"""
    results = {}
    use_ai_summary = bool(OPENAI_API_KEY)
    
    if use_ai_summary:
        print(f"🤖 AI 摘要已启用 (模型: {AI_MODEL}, API: {OPENAI_BASE_URL})")
    else:
        print("⚠️ 未配置 OPENAI_API_KEY，跳过 AI 摘要")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        for influencer in INFLUENCERS:
            name = influencer["name"]
            handle = influencer["handle"]
            url = f"https://twitter.com/{handle}"
            
            print(f"📊 正在抓取: {name} (@{handle})")
            
            try:
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await page.wait_for_timeout(3000)
                
                all_tweets = []
                recent_tweets = []
                
                try:
                    await page.wait_for_selector('[data-testid="tweet"]', timeout=10000)
                except:
                    print(f"  ⚠️ 无法加载 @{handle} 的推文")
                    results[name] = []
                    continue
                
                tweet_elements = await page.query_selector_all('[data-testid="tweet"]')
                
                for i, tweet_el in enumerate(tweet_elements[:15]):
                    try:
                        text_el = await tweet_el.query_selector('[data-testid="tweetText"]')
                        text = await text_el.inner_text() if text_el else ""
                        
                        time_el = await tweet_el.query_selector('time')
                        time_str = ""
                        if time_el:
                            time_str = await time_el.inner_text()
                        
                        link_el = await tweet_el.query_selector('a[href*="/status/"]')
                        tweet_url = ""
                        if link_el:
                            href = await link_el.get_attribute('href')
                            if href:
                                tweet_url = f"https://twitter.com{href}"
                        
                        replies = retweets = likes = 0
                        
                        reply_el = await tweet_el.query_selector('[data-testid="reply"]')
                        if reply_el:
                            reply_text = await reply_el.inner_text()
                            try:
                                replies = int(reply_text.replace(',', '').replace('K', '000').replace('M', '000000'))
                            except:
                                pass
                        
                        retweet_el = await tweet_el.query_selector('[data-testid="retweet"]')
                        if retweet_el:
                            retweet_text = await retweet_el.inner_text()
                            try:
                                retweets = int(retweet_text.replace(',', '').replace('K', '000').replace('M', '000000'))
                            except:
                                pass
                        
                        like_el = await tweet_el.query_selector('[data-testid="like"]')
                        if like_el:
                            like_text = await like_el.inner_text()
                            try:
                                likes = int(like_text.replace(',', '').replace('K', '000').replace('M', '000000'))
                            except:
                                pass
                        
                        if text and tweet_url:
                            tweet_data = {
                                "text": text,
                                "url": tweet_url,
                                "time": time_str,
                                "replies": replies,
                                "retweets": retweets,
                                "likes": likes
                            }
                            all_tweets.append(tweet_data)
                            
                            if is_recent_tweet(time_str):
                                # 生成 AI 摘要
                                if use_ai_summary:
                                    print(f"  🤖 生成摘要中...")
                                    summary_data = generate_tweet_summary(text, name)
                                    tweet_data.update(summary_data)
                                    await asyncio.sleep(0.5)  # 避免 API 限流
                                
                                recent_tweets.append(tweet_data)
                                if len(recent_tweets) >= MAX_TWEETS_PER_USER:
                                    break
                                    
                    except Exception as e:
                        continue
                
                results[name] = recent_tweets
                print(f"  ✅ 获取了 {len(recent_tweets)} 条最近推文 (共 {len(all_tweets)} 条)")
                
                await page.wait_for_timeout(DELAY_BETWEEN_USERS * 1000)
                
            except Exception as e:
                print(f"  ❌ 抓取 @{handle} 失败: {e}")
                results[name] = []
        
        await browser.close()
    
    return results


def save_report(data: dict):
    """保存报告到文件"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = OUTPUT_DIR / f"report_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存: {filename}")
    return filename


async def main():
    """主函数"""
    print("=" * 50)
    print("🐦 AI Influencers Twitter Tracker")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 只抓取最近 {MAX_TWEET_AGE_HOURS} 小时内的推文")
    print("=" * 50)
    
    data = await scrape_twitter()
    save_report(data)
    
    webhook_url = os.getenv("FEISHU_WEBHOOK", "")
    content = generate_feishu_content(data)
    
    if webhook_url:
        send_to_feishu(webhook_url, content)
    else:
        print("⚠️ 未设置 FEISHU_WEBHOOK 环境变量")
    
    total = sum(len(tweets) for tweets in data.values())
    print("=" * 50)
    print(f"✅ 完成! 共获取 {total} 条最新推文")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
