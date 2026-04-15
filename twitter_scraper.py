#!/usr/bin/env python3
"""
Twitter AI Influencers Tracker
使用 Playwright 浏览器自动化抓取 AI 大牛和机构的最新推文，并推送到飞书

GitHub Actions 自动运行版本
支持 AI 摘要功能（OpenAI 兼容 API，包括智谱、DeepSeek 等）
支持保存报告到 reports 目录并自动清理过期报告
"""

import asyncio
import json
import os
import urllib.request
import re
import glob
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ============ 配置区域 ============

# AI 大牛（个人）
INFLUENCERS = [
    # OpenAI
    {"name": "Sam Altman", "handle": "sama", "title": "OpenAI CEO"},
    
    # xAI
    {"name": "Elon Musk", "handle": "elonmusk", "title": "xAI 创始人"},
    
    # DeepMind
    {"name": "Demis Hassabis", "handle": "demishassabis", "title": "DeepMind CEO"},
    {"name": "Sergey Levine", "handle": "SergeyI Levine4", "title": "DeepMind 研究员"},
    
    # Meta AI
    {"name": "Yann LeCun", "handle": "ylecun", "title": "Meta AI 首席科学家"},
    
    # AI 教育
    {"name": "Andrej Karpathy", "handle": "karpathy", "title": "AI 教育网红"},
    
    # OpenAI 系
    {"name": "Ilya Sutskever", "handle": "ilyasut", "title": "OpenAI 联合创始人"},
    
    # Anthropic
    {"name": "Dario Amodei", "handle": "dario_amodei", "title": "Anthropic CEO"},
    
    # Transformer 作者
    {"name": "Ashish Vaswani", "handle": "avaswani", "title": "Transformer 作者"},
    {"name": "Aidan Gomez", "handle": "aidangomez", "title": "Cohere CEO"},
    
    # Hugging Face
    {"name": "Clement Delangue", "handle": "clementdelangue", "title": "Hugging Face CEO"},
    {"name": "Thomas Wolf", "handle": "Thom_Wolf", "title": "Hugging Face 联合创始人"},
    
    # NVIDIA
    {"name": "Jim Fan", "handle": "DrJimFan", "title": "NVIDIA 高级科学家"},
    
    # AI 媒体
    {"name": "Rowan Cheung", "handle": "rowancheung", "title": "The Rundown AI 创始人"},
    {"name": "Matt Shumer", "handle": "mshumer_", "title": "AI 产品开发者"},
    
    # 其他
    {"name": "Geoffrey Hinton", "handle": "geoffreyhinton", "title": "AI 教父、诺贝尔奖得主"},
    {"name": "Andrew Ng", "handle": "AndrewYNg", "title": "DeepLearning.AI 创始人"},
    {"name": "Pieter Levels", "handle": "levelsio", "title": "独立开发者"},
]

# AI 机构
ORGANIZATIONS = [
    # ===== 国外大模型公司 =====
    {"name": "OpenAI", "handle": "OpenAI", "title": "GPT、ChatGPT、DALL-E"},
    {"name": "Anthropic", "handle": "AnthropicAI", "title": "Claude 模型"},
    {"name": "Google DeepMind", "handle": "DeepMind", "title": "AlphaGo、Gemini"},
    {"name": "Google AI", "handle": "GoogleAI", "title": "Google AI 研究"},
    {"name": "Meta AI", "handle": "MetaAI", "title": "LLaMA、PyTorch"},
    {"name": "xAI", "handle": "xaboratory", "title": "Grok 模型"},
    {"name": "Mistral AI", "handle": "MistralAI", "title": "Mistral、Mixtral"},
    {"name": "Cohere", "handle": "CohereForAI", "title": "企业大模型"},
    {"name": "Hugging Face", "handle": "huggingface", "title": "开源 AI 社区"},
    {"name": "Stability AI", "handle": "StabilityAI", "title": "Stable Diffusion"},
    
    # ===== 国外 AI 基础设施 =====
    {"name": "NVIDIA AI", "handle": "NVIDIAAI", "title": "GPU、CUDA、AI 芯片"},
    {"name": "AWS AI", "handle": "AWS_AI", "title": "云端 AI 服务"},
    
    # ===== 国外 AI 应用 =====
    {"name": "Midjourney", "handle": "midjourney", "title": "AI 绘图"},
    {"name": "Runway", "handle": "runwayml", "title": "AI 视频"},
    {"name": "Perplexity", "handle": "perplexity_ai", "title": "AI 搜索引擎"},
    {"name": "Character.AI", "handle": "character_ai", "title": "AI 虚拟角色"},
    
    # ===== 国内大模型创业 =====
    {"name": "智谱 AI", "handle": "ZhipuAI", "title": "GLM 模型"},
    {"name": "月之暗面", "handle": "MoonshotAI_", "title": "Kimi"},
    {"name": "MiniMax", "handle": "MiniMax_AI", "title": "海螺 AI"},
    {"name": "百川智能", "handle": "baichuan_ai", "title": "Baichuan 模型"},
    {"name": "阶跃星辰", "handle": "StepFunAI", "title": "Step 模型"},
    {"name": "01.AI", "handle": "01AI_official", "title": "Yi 模型"},
    
    # ===== 国内互联网大厂 =====
    {"name": "百度 AI", "handle": "BaiduAI", "title": "文心一言"},
    {"name": "阿里通义", "handle": "AlibabaTongyi", "title": "通义千问"},
    {"name": "腾讯混元", "handle": "TencentHY", "title": "混元大模型"},
    {"name": "字节豆包", "handle": "doubao_ai", "title": "豆包、云雀"},
    {"name": "华为云", "handle": "HuaweiCloud", "title": "盘古大模型"},
    {"name": "科大讯飞", "handle": "iflytek", "title": "星火大模型"},
    
    # ===== 国内新势力车企 =====
    {"name": "理想汽车", "handle": "LiAutoInc", "title": "理想 AD 智驾"},
    {"name": "小鹏汽车", "handle": "XPengMotors", "title": "XNGP 智驾"},
    {"name": "蔚来", "handle": "NIOGlobal", "title": "NIO Pilot"},
    
    # ===== 国内 AI 其他 =====
    {"name": "商汤科技", "handle": "SenseTime", "title": "商汤大模型"},
]

OUTPUT_DIR = Path("reports")
MAX_TWEETS_PER_USER = 3
DELAY_BETWEEN_USERS = 2

# 只抓取最近多少小时内的推文
MAX_TWEET_AGE_HOURS = 24

# 报告保留天数（超过此天数的报告将被自动删除）
REPORT_RETENTION_DAYS = 30

# AI 摘要配置（支持 OpenAI 兼容 API）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "glm-4-flash")

# ============ 报告清理 ============

def cleanup_old_reports():
    """删除超过保留天数的旧报告"""
    if not OUTPUT_DIR.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=REPORT_RETENTION_DAYS)
    deleted_count = 0
    
    # 查找所有报告文件
    patterns = ["report_*.json", "report_*.md"]
    for pattern in patterns:
        for file_path in OUTPUT_DIR.glob(pattern):
            try:
                # 从文件名提取日期 (report_YYYY-MM-DD_HH-MM-SS.json)
                filename = file_path.name
                date_str = filename.replace("report_", "").rsplit(".", 1)[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"🗑️ 已删除过期报告: {filename}")
            except Exception as e:
                # 如果无法解析日期，检查文件修改时间
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"🗑️ 已删除过期报告: {file_path.name}")
    
    if deleted_count > 0:
        print(f"✅ 共清理 {deleted_count} 个过期报告（保留期：{REPORT_RETENTION_DAYS} 天）")
    
    return deleted_count


# ============ 时间解析 ============

def parse_tweet_time(time_str: str) -> datetime:
    """解析 Twitter 时间格式"""
    now = datetime.utcnow()
    
    if not time_str:
        return now - timedelta(days=365)
    
    time_str = time_str.strip().lower()
    
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
    """使用 AI 生成推文摘要"""
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
}}"""

    try:
        data = {
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的推文分析助手。只返回 JSON。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
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
            
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('```', 1)[0]
            
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
                    "content": f"🐦 AI 动态日报 - {datetime.now().strftime('%Y-%m-%d')}"
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
                            "content": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC | 仅显示最近 {MAX_TWEET_AGE_HOURS} 小时内的推文"
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


def generate_feishu_content(personal_tweets: dict, org_tweets: dict) -> str:
    """生成飞书消息内容（优化版面布局）"""
    lines = []
    
    # ===== 统计信息 =====
    personal_total = sum(len(tweets) for tweets in personal_tweets.values())
    org_total = sum(len(tweets) for tweets in org_tweets.values())
    total = personal_total + org_total
    
    if total == 0:
        return f"**今日暂无新推文**\n\n在过去 {MAX_TWEET_AGE_HOURS} 小时内，所有监控的主体都没有发布新推文。"
    
    lines.append(f"📊 **今日统计**: {total} 条新推文 | 👤 大牛 {personal_total} 条 | 🏢 机构 {org_total} 条")
    lines.append("---")
    lines.append("")
    
    # ===== 第一部分：AI 大牛 =====
    if personal_tweets:
        lines.append("## 👤 AI 大牛动态")
        lines.append("")
        for entity, tweets in personal_tweets.items():
            if tweets:
                lines.append(f"### {entity}")
                for tweet in tweets:
                    lines.append(format_tweet(tweet))
                lines.append("")
    
    # ===== 第二部分：AI 机构 =====
    if org_tweets:
        if personal_tweets:
            lines.append("---")
            lines.append("")
        lines.append("## 🏢 AI 机构动态")
        lines.append("")
        for entity, tweets in org_tweets.items():
            if tweets:
                lines.append(f"### {entity}")
                for tweet in tweets:
                    lines.append(format_tweet(tweet))
                lines.append("")
    
    return "\n".join(lines)


def format_tweet(tweet: dict) -> str:
    """格式化单条推文（紧凑布局）"""
    lines = []
    
    time_info = tweet.get('time', '')
    summary = tweet.get('summary', '')
    key_data = tweet.get('key_data', [])
    keywords = tweet.get('keywords', [])
    
    # 第一行：时间 + 链接
    lines.append(f"**[{time_info}]** [查看原文]({tweet['url']})")
    
    # 第二行：AI 摘要（如有）
    if summary:
        lines.append(f"> {summary}")
    
    # 第三行：关键数据 + 关键词（合并）
    info_parts = []
    if key_data and any(key_data):
        data_str = " | ".join([d for d in key_data if d])
        if data_str:
            info_parts.append(f"📊 {data_str}")
    if keywords:
        keywords_str = " ".join([f"`{k}`" for k in keywords])
        info_parts.append(f"🏷️ {keywords_str}")
    
    if info_parts:
        lines.append(" | ".join(info_parts))
    
    # 第四行：互动数据
    lines.append(f"💬{tweet.get('replies', 0)} 🔁{tweet.get('retweets', 0)} ❤️{tweet.get('likes', 0)}")
    lines.append("")
    
    return "\n".join(lines)


# ============ 报告保存 ============

def save_report(personal_data: dict, org_data: dict):
    """保存报告到文件（JSON + Markdown）"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 保存 JSON 格式
    json_filename = OUTPUT_DIR / f"report_{timestamp}.json"
    json_data = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "personal": personal_data,
        "organizations": org_data
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"📄 JSON 报告已保存: {json_filename}")
    
    # 保存 Markdown 格式（与飞书内容一致）
    md_filename = OUTPUT_DIR / f"report_{timestamp}.md"
    md_content = generate_markdown_report(personal_data, org_data)
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"📄 Markdown 报告已保存: {md_filename}")
    
    return json_filename, md_filename


def generate_markdown_report(personal_tweets: dict, org_tweets: dict) -> str:
    """生成 Markdown 格式的完整报告"""
    lines = []
    
    # 标题
    lines.append(f"# 🐦 AI 动态日报")
    lines.append("")
    lines.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")
    
    # 统计信息
    personal_total = sum(len(tweets) for tweets in personal_tweets.values())
    org_total = sum(len(tweets) for tweets in org_tweets.values())
    total = personal_total + org_total
    
    lines.append("## 📊 统计概览")
    lines.append("")
    lines.append(f"- **总推文数**: {total} 条")
    lines.append(f"- **AI 大牛**: {personal_total} 条")
    lines.append(f"- **AI 机构**: {org_total} 条")
    lines.append(f"- **时间范围**: 最近 {MAX_TWEET_AGE_HOURS} 小时")
    lines.append("")
    
    if total == 0:
        lines.append("---")
        lines.append("")
        lines.append("*今日暂无新推文*")
        return "\n".join(lines)
    
    lines.append("---")
    lines.append("")
    
    # AI 大牛动态
    if personal_tweets:
        lines.append("## 👤 AI 大牛动态")
        lines.append("")
        for entity, tweets in personal_tweets.items():
            if tweets:
                lines.append(f"### {entity}")
                lines.append("")
                for tweet in tweets:
                    lines.extend(format_tweet_markdown(tweet))
                lines.append("")
    
    # AI 机构动态
    if org_tweets:
        lines.append("---")
        lines.append("")
        lines.append("## 🏢 AI 机构动态")
        lines.append("")
        for entity, tweets in org_tweets.items():
            if tweets:
                lines.append(f"### {entity}")
                lines.append("")
                for tweet in tweets:
                    lines.extend(format_tweet_markdown(tweet))
                lines.append("")
    
    # 页脚
    lines.append("---")
    lines.append("")
    lines.append(f"*本报告由 AI Influencers Tracker 自动生成*")
    lines.append(f"*监控 {len(INFLUENCERS)} 位 AI 大牛 + {len(ORGANIZATIONS)} 家 AI 机构*")
    
    return "\n".join(lines)


def format_tweet_markdown(tweet: dict) -> list:
    """格式化单条推文为 Markdown"""
    lines = []
    
    time_info = tweet.get('time', '')
    summary = tweet.get('summary', '')
    key_data = tweet.get('key_data', [])
    keywords = tweet.get('keywords', [])
    text = tweet.get('text', '')
    
    # 时间和链接
    lines.append(f"#### [{time_info}] {tweet['url']}")
    lines.append("")
    
    # 推文原文（截取前 200 字符）
    if text:
        display_text = text[:200] + "..." if len(text) > 200 else text
        lines.append(f"> {display_text}")
        lines.append("")
    
    # AI 摘要
    if summary:
        lines.append(f"**摘要**: {summary}")
    
    # 关键数据
    if key_data and any(key_data):
        data_str = " | ".join([d for d in key_data if d])
        if data_str:
            lines.append(f"**数据**: {data_str}")
    
    # 关键词
    if keywords:
        keywords_str = ", ".join([f"`{k}`" for k in keywords])
        lines.append(f"**关键词**: {keywords_str}")
    
    # 互动数据
    lines.append(f"**互动**: 💬 {tweet.get('replies', 0)} | 🔁 {tweet.get('retweets', 0)} | ❤️ {tweet.get('likes', 0)}")
    lines.append("")
    
    return lines


# ============ Twitter 抓取 ============

async def scrape_entity(page, entity: dict) -> list:
    """抓取单个主体的推文"""
    name = entity["name"]
    handle = entity["handle"]
    title = entity.get("title", "")
    display_name = f"{name} ({title})" if title else name
    url = f"https://twitter.com/{handle}"
    
    print(f"📊 正在抓取: {display_name}")
    
    try:
        await page.goto(url, timeout=30000, wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        
        recent_tweets = []
        
        try:
            await page.wait_for_selector('[data-testid="tweet"]', timeout=10000)
        except:
            print(f"  ⚠️ 无法加载 @{handle} 的推文")
            return []
        
        tweet_elements = await page.query_selector_all('[data-testid="tweet"]')
        
        for tweet_el in tweet_elements[:15]:
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
                    
                    if is_recent_tweet(time_str):
                        if OPENAI_API_KEY:
                            print(f"  🤖 生成摘要中...")
                            summary_data = generate_tweet_summary(text, name)
                            tweet_data.update(summary_data)
                            await asyncio.sleep(0.3)
                        
                        recent_tweets.append(tweet_data)
                        if len(recent_tweets) >= MAX_TWEETS_PER_USER:
                            break
                            
            except Exception as e:
                continue
        
        print(f"  ✅ 获取了 {len(recent_tweets)} 条最近推文")
        return recent_tweets
        
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        return []


async def scrape_twitter():
    """使用 Playwright 抓取 Twitter"""
    personal_results = {}
    org_results = {}
    
    use_ai_summary = bool(OPENAI_API_KEY)
    if use_ai_summary:
        print(f"🤖 AI 摘要已启用 (模型: {AI_MODEL})")
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
        
        # 抓取 AI 大牛
        print("\n" + "="*50)
        print("👤 开始抓取 AI 大牛...")
        print("="*50)
        for entity in INFLUENCERS:
            name = entity["name"]
            title = entity.get("title", "")
            display_name = f"{name} ({title})" if title else name
            
            tweets = await scrape_entity(page, entity)
            personal_results[display_name] = tweets
            
            await page.wait_for_timeout(DELAY_BETWEEN_USERS * 1000)
        
        # 抓取 AI 机构
        print("\n" + "="*50)
        print("🏢 开始抓取 AI 机构...")
        print("="*50)
        for entity in ORGANIZATIONS:
            name = entity["name"]
            title = entity.get("title", "")
            display_name = f"{name} ({title})" if title else name
            
            tweets = await scrape_entity(page, entity)
            org_results[display_name] = tweets
            
            await page.wait_for_timeout(DELAY_BETWEEN_USERS * 1000)
        
        await browser.close()
    
    return personal_results, org_results


async def main():
    """主函数"""
    print("=" * 50)
    print("🐦 AI Influencers & Organizations Twitter Tracker")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 大牛: {len(INFLUENCERS)} 位")
    print(f"🏢 机构: {len(ORGANIZATIONS)} 家")
    print(f"⏰ 只抓取最近 {MAX_TWEET_AGE_HOURS} 小时内的推文")
    print(f"🗑️ 报告保留期: {REPORT_RETENTION_DAYS} 天")
    print("=" * 50)
    
    # 清理过期报告
    print("\n📁 检查并清理过期报告...")
    cleanup_old_reports()
    
    # 抓取数据
    personal_data, org_data = await scrape_twitter()
    
    # 保存报告
    print("\n📄 保存报告...")
    save_report(personal_data, org_data)
    
    # 推送到飞书
    webhook_url = os.getenv("FEISHU_WEBHOOK", "")
    content = generate_feishu_content(personal_data, org_data)
    
    if webhook_url:
        print("\n📤 推送到飞书...")
        send_to_feishu(webhook_url, content)
    else:
        print("⚠️ 未设置 FEISHU_WEBHOOK 环境变量")
    
    # 统计
    personal_total = sum(len(tweets) for tweets in personal_data.values())
    org_total = sum(len(tweets) for tweets in org_data.values())
    total = personal_total + org_total
    
    print("\n" + "=" * 50)
    print(f"✅ 完成! 共获取 {total} 条最新推文 (大牛 {personal_total} + 机构 {org_total})")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
