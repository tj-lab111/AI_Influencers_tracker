# 🤖 AI Influencers Tracker

> Automatically track AI thought leaders and organizations on Twitter, with daily reports pushed to Feishu

## ✨ Features

- 🔍 **Auto Scraping** — Use Playwright browser automation to scrape latest tweets
- 🧠 **AI Summarization** — Generate Chinese summaries, extract key data and keywords using Zhipu GLM-4-Flash (free unlimited)
- 📊 **Feishu Push** — Automatically push formatted reports to Feishu groups daily
- ⏰ **Scheduled Runs** — GitHub Actions runs automatically at 8:00 AM Beijing time
- 🌐 **Bilingual Monitoring** — Track both international and Chinese AI leaders and organizations
- 📁 **Report Archiving** — Auto-save reports to repository with 30-day auto-cleanup

## 👥 Monitored Accounts

### 👤 AI Influencers (19)

| Name | Title | Twitter |
|------|-------|---------|
| Sam Altman | OpenAI CEO | [@sama](https://twitter.com/sama) |
| Dario Amodei | Anthropic CEO | [@dario_amodei](https://twitter.com/dario_amodei) |
| Elon Musk | xAI Founder | [@elonmusk](https://twitter.com/elonmusk) |
| Demis Hassabis | DeepMind CEO | [@demishassabis](https://twitter.com/demishassabis) |
| Yann LeCun | Meta AI Chief Scientist | [@ylecun](https://twitter.com/ylecun) |
| Andrej Karpathy | AI Education Influencer | [@karpathy](https://twitter.com/karpathy) |
| Ilya Sutskever | OpenAI Co-founder | [@ilyasut](https://twitter.com/ilyasut) |
| Geoffrey Hinton | AI Godfather, Nobel Laureate | [@geoffreyhinton](https://twitter.com/geoffreyhinton) |
| Andrew Ng | DeepLearning.AI Founder | [@AndrewYNg](https://twitter.com/AndrewYNg) |
| Jim Fan | NVIDIA Senior Scientist | [@DrJimFan](https://twitter.com/DrJimFan) |
| Clement Delangue | Hugging Face CEO | [@clementdelangue](https://twitter.com/clementdelangue) |
| Thomas Wolf | Hugging Face Co-founder | [@Thom_Wolf](https://twitter.com/Thom_Wolf) |
| Ashish Vaswani | Transformer Author | [@avaswani](https://twitter.com/avaswani) |
| Aidan Gomez | Cohere CEO | [@aidangomez](https://twitter.com/aidangomez) |
| Pieter Levels | Indie Developer | [@levelsio](https://twitter.com/levelsio) |
| Rowan Cheung | The Rundown AI Founder | [@rowancheung](https://twitter.com/rowancheung) |
| Matt Shumer | AI Product Developer | [@mshumer_](https://twitter.com/mshumer_) |
| Sergey Levine | DeepMind Researcher | [@SergeyLevine4](https://twitter.com/SergeyLevine4) |

### 🏢 AI Organizations (36)

**International LLM Companies (10)**
- OpenAI (GPT, ChatGPT, DALL-E)
- Anthropic (Claude)
- Google DeepMind (AlphaGo, Gemini)
- Meta AI (LLaMA, PyTorch)
- xAI (Grok)
- Mistral AI (Mistral, Mixtral)
- Cohere (Enterprise LLM)
- Hugging Face (Open-source AI Community)
- Stability AI (Stable Diffusion)
- Google AI

**International AI Applications (4)**
- Midjourney (AI Image Generation)
- Runway (AI Video)
- Perplexity (AI Search Engine)
- Character.AI (AI Virtual Characters)

**International AI Infrastructure (2)**
- NVIDIA AI (GPU, CUDA, AI Chips)
- AWS AI (Cloud AI Services)

**Chinese LLM Startups (6)**
- Zhipu AI (GLM Models)
- Moonshot AI (Kimi)
- MiniMax (Hailuo AI)
- Baichuan Intelligence (Baichuan)
- StepFun (Step Models)
- 01.AI (Yi Models)

**Chinese Tech Giants (6)**
- Baidu AI (Ernie Bot)
- Alibaba Tongyi (Qwen)
- Tencent Hunyuan
- ByteDance Doubao
- Huawei Cloud (Pangu)
- iFLYTEK (Spark)

**Chinese EV Companies (3)**
- Li Auto (Li AD)
- XPeng (XNGP)
- NIO (NIO Pilot)

**Other Chinese AI (1)**
- SenseTime

## 📋 Report Format

Each tweet includes:

```
⏰ Time | 🔗 Link
📝 Summary: AI-generated one-liner (max 20 chars)
📊 Data: Key metrics (if available)
🏷️ Keywords: keyword1, keyword2, keyword3
💬 Engagement: Likes | Retweets | Replies
```

## 🚀 Quick Start

### 1. Fork This Repository

Click the Fork button in the top right to copy this repo to your account.

### 2. Configure Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | How to Get |
|--------|-------------|------------|
| `FEISHU_WEBHOOK` | Feishu bot Webhook URL | [Create Feishu Bot](#create-feishu-bot) |
| `OPENAI_API_KEY` | Zhipu API Key (optional, for AI summaries) | [Zhipu Open Platform](https://open.bigmodel.cn/) |

### 3. Enable GitHub Actions

Go to **Actions** tab and click **I understand my workflows, go ahead and enable them**.

### 4. Test Run

Select **Twitter AI Influencers Tracker** workflow in Actions and click **Run workflow**.

## 🔧 Create Feishu Bot

1. Open a Feishu group chat
2. Click Group Settings → Group Bots → Add Bot
3. Select "Custom Bot"
4. Copy the Webhook URL
5. Add the URL to GitHub Secrets as `FEISHU_WEBHOOK`

## ⚙️ Configuration

### Modify Monitored Accounts

Edit `INFLUENCERS` and `ORGANIZATIONS` lists in `twitter_scraper.py`:

```python
INFLUENCERS = [
    {"name": "Sam Altman", "handle": "sama", "title": "OpenAI CEO"},
    {"name": "Dario Amodei", "handle": "dario_amodei", "title": "Anthropic CEO"},
    # Add more...
]

ORGANIZATIONS = [
    {"name": "OpenAI", "handle": "OpenAI", "title": "GPT, ChatGPT, DALL-E"},
    # Add more...
]
```

### Change Schedule

Edit `.github/workflows/daily_scraper.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # UTC 0:00 = Beijing 8:00 AM
```

Cron examples:
- `0 0 * * *` — Daily at UTC 0:00 (Beijing 8:00 AM)
- `0 12 * * *` — Daily at UTC 12:00 (Beijing 8:00 PM)
- `0 */6 * * *` — Every 6 hours

### AI Summary Configuration

Default uses Zhipu GLM-4-Flash (completely free, unlimited). For other OpenAI-compatible APIs:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_BASE_URL: https://open.bigmodel.cn/api/paas/v4/  # Zhipu
  AI_MODEL: glm-4-flash
```

Available AI services:
- **Zhipu GLM-4-Flash** — Free, `https://open.bigmodel.cn/api/paas/v4/`
- **DeepSeek** — Low cost, `https://api.deepseek.com`
- **OpenAI** — Original, `https://api.openai.com/v1`

## 📁 Project Structure

```
AI_Influencers_tracker/
├── .github/
│   └── workflows/
│       └── daily_scraper.yml    # GitHub Actions workflow
├── reports/                     # Report output (30-day auto-cleanup)
│   ├── report_YYYY-MM-DD.json   # JSON format report
│   └── report_YYYY-MM-DD.md     # Markdown format report
├── twitter_scraper.py           # Main script
├── .gitignore
├── README.md                    # Chinese documentation
└── README_EN.md                 # English documentation
```

## 🛠️ Tech Stack

- **Playwright** — Browser automation for Twitter scraping
- **Zhipu GLM-4-Flash** — Free AI summarization service
- **GitHub Actions** — Scheduled task execution
- **Feishu Webhook** — Message push notifications

## ⚠️ Notes

1. **Twitter Limits** — Unauthenticated access has limited tweet visibility; recommend monitoring max 50 accounts
2. **Free API** — Zhipu GLM-4-Flash is completely free with unlimited calls
3. **Runtime** — Each run takes ~5-10 minutes depending on account count
4. **Timezone** — GitHub Actions uses UTC; configured for Beijing 8:00 AM
5. **Report Cleanup** — Reports older than 30 days in reports/ directory are auto-deleted

## 📝 Changelog

### 2026-04-15
- ✨ Added Dario Amodei (Anthropic CEO) to monitored influencers
- ✨ Added auto-save reports to reports/ directory
- ✨ Added 30-day auto-cleanup for old reports
- 📝 Updated README documentation

### 2026-04-14
- 🎉 Project initialization
- ✨ Support for AI influencers monitoring
- ✨ Integrated Zhipu GLM-4-Flash AI summaries
- ✨ Feishu push functionality

## 📄 License

MIT License

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**⭐ If this project helps you, please give it a Star!**
