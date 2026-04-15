# 🤖 AI Influencers Tracker

> 自动追踪 AI 大牛和机构的 Twitter 动态，每日推送至飞书

## ✨ 功能特性

- 🔍 **自动抓取** — 使用 Playwright 浏览器自动化抓取 Twitter 最新推文
- 🧠 **AI 摘要** — 使用智谱 GLM-4-Flash（免费无限）生成中文摘要、提取关键数据和关键词
- 📊 **飞书推送** — 每日自动推送格式化报告到飞书群
- ⏰ **定时运行** — GitHub Actions 每天北京时间 8:00 自动执行
- 🌐 **双语监控** — 同时监控国内外 AI 领军人物和机构
- 📁 **报告存档** — 自动保存报告到仓库，30 天自动清理

## 👥 监控对象

### 👤 AI 大牛（19 位）

| 姓名 | 职位 | Twitter |
|------|------|---------|
| Sam Altman | OpenAI CEO | [@sama](https://twitter.com/sama) |
| Dario Amodei | Anthropic CEO | [@dario_amodei](https://twitter.com/dario_amodei) |
| Elon Musk | xAI 创始人 | [@elonmusk](https://twitter.com/elonmusk) |
| Demis Hassabis | DeepMind CEO | [@demishassabis](https://twitter.com/demishassabis) |
| Yann LeCun | Meta AI 首席科学家 | [@ylecun](https://twitter.com/ylecun) |
| Andrej Karpathy | AI 教育网红 | [@karpathy](https://twitter.com/karpathy) |
| Ilya Sutskever | OpenAI 联合创始人 | [@ilyasut](https://twitter.com/ilyasut) |
| Geoffrey Hinton | AI 教父、诺贝尔奖得主 | [@geoffreyhinton](https://twitter.com/geoffreyhinton) |
| Andrew Ng | DeepLearning.AI 创始人 | [@AndrewYNg](https://twitter.com/AndrewYNg) |
| Jim Fan | NVIDIA 高级科学家 | [@DrJimFan](https://twitter.com/DrJimFan) |
| Clement Delangue | Hugging Face CEO | [@clementdelangue](https://twitter.com/clementdelangue) |
| Thomas Wolf | Hugging Face 联合创始人 | [@Thom_Wolf](https://twitter.com/Thom_Wolf) |
| Ashish Vaswani | Transformer 作者 | [@avaswani](https://twitter.com/avaswani) |
| Aidan Gomez | Cohere CEO | [@aidangomez](https://twitter.com/aidangomez) |
| Pieter Levels | 独立开发者 | [@levelsio](https://twitter.com/levelsio) |
| Rowan Cheung | The Rundown AI 创始人 | [@rowancheung](https://twitter.com/rowancheung) |
| Matt Shumer | AI 产品开发者 | [@mshumer_](https://twitter.com/mshumer_) |
| Sergey Levine | DeepMind 研究员 | [@SergeyLevine4](https://twitter.com/SergeyLevine4) |

### 🏢 AI 机构（36 家）

**国外大模型公司（10 家）**
- OpenAI（GPT、ChatGPT、DALL-E）
- Anthropic（Claude）
- Google DeepMind（AlphaGo、Gemini）
- Meta AI（LLaMA、PyTorch）
- xAI（Grok）
- Mistral AI（Mistral、Mixtral）
- Cohere（企业大模型）
- Hugging Face（开源 AI 社区）
- Stability AI（Stable Diffusion）
- Google AI

**国外 AI 应用（4 家）**
- Midjourney（AI 绘图）
- Runway（AI 视频）
- Perplexity（AI 搜索引擎）
- Character.AI（AI 虚拟角色）

**国外 AI 基础设施（2 家）**
- NVIDIA AI（GPU、CUDA、AI 芯片）
- AWS AI（云端 AI 服务）

**国内大模型创业（6 家）**
- 智谱 AI（GLM 模型）
- 月之暗面（Kimi）
- MiniMax（海螺 AI）
- 百川智能（Baichuan）
- 阶跃星辰（Step）
- 01.AI（Yi 模型）

**国内互联网大厂（6 家）**
- 百度 AI（文心一言）
- 阿里通义（通义千问）
- 腾讯混元
- 字节豆包
- 华为云（盘古大模型）
- 科大讯飞（星火大模型）

**国内新势力车企（3 家）**
- 理想汽车（理想 AD 智驾）
- 小鹏汽车（XNGP 智驾）
- 蔚来（NIO Pilot）

**国内 AI 其他（1 家）**
- 商汤科技

## 📋 推文报告格式

每条推文包含以下信息：

```
⏰ 时间 | 🔗 链接
📝 摘要：AI 生成的一句话介绍（20字以内）
📊 数据：关键数据（如有）
🏷️ 关键词：关键词1、关键词2、关键词3
💬 互动：点赞数 | 转发数 | 回复数
```

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角 Fork 按钮，将仓库复制到你的账号下。

### 2. 配置 Secrets

进入仓库 **Settings → Secrets and variables → Actions**，添加以下 secrets：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook URL | [创建飞书机器人](#创建飞书机器人) |
| `OPENAI_API_KEY` | 智谱 API Key（可选，用于 AI 摘要） | [智谱开放平台](https://open.bigmodel.cn/) |

### 3. 启用 GitHub Actions

进入 **Actions** 标签页，点击 **I understand my workflows, go ahead and enable them**。

### 4. 手动测试

在 **Actions** 页面选择 **Twitter AI Influencers Tracker** 工作流，点击 **Run workflow** 进行测试。

## 🔧 创建飞书机器人

1. 打开飞书群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择「自定义机器人」
4. 复制 Webhook URL
5. 将 URL 配置到 GitHub Secrets 的 `FEISHU_WEBHOOK`

## ⚙️ 配置说明

### 修改监控对象

编辑 `twitter_scraper.py` 中的 `INFLUENCERS` 和 `ORGANIZATIONS` 列表：

```python
INFLUENCERS = [
    {"name": "Sam Altman", "handle": "sama", "title": "OpenAI CEO"},
    {"name": "Dario Amodei", "handle": "dario_amodei", "title": "Anthropic CEO"},
    # 添加更多...
]

ORGANIZATIONS = [
    {"name": "OpenAI", "handle": "OpenAI", "title": "GPT、ChatGPT、DALL-E"},
    # 添加更多...
]
```

### 修改运行时间

编辑 `.github/workflows/daily_scraper.yml`：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # UTC 0:00 = 北京时间 8:00
```

Cron 表达式说明：
- `0 0 * * *` — 每天 UTC 0:00（北京时间 8:00）
- `0 12 * * *` — 每天 UTC 12:00（北京时间 20:00）
- `0 */6 * * *` — 每 6 小时一次

### AI 摘要配置

默认使用智谱 GLM-4-Flash（完全免费，无限调用）。如需使用其他 OpenAI 兼容 API：

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_BASE_URL: https://open.bigmodel.cn/api/paas/v4/  # 智谱
  AI_MODEL: glm-4-flash
```

可选的 AI 服务：
- **智谱 GLM-4-Flash** — 免费，`https://open.bigmodel.cn/api/paas/v4/`
- **DeepSeek** — 低价，`https://api.deepseek.com`
- **OpenAI** — 原版，`https://api.openai.com/v1`

## 📁 项目结构

```
AI_Influencers_tracker/
├── .github/
│   └── workflows/
│       └── daily_scraper.yml    # GitHub Actions 工作流
├── reports/                     # 报告输出目录（30天自动清理）
│   ├── report_YYYY-MM-DD.json   # JSON 格式报告
│   └── report_YYYY-MM-DD.md     # Markdown 格式报告
├── twitter_scraper.py           # 主脚本
├── .gitignore
├── README.md                    # 中文文档
└── README_EN.md                 # English Documentation
```

## 🛠️ 技术栈

- **Playwright** — 浏览器自动化，抓取 Twitter
- **智谱 GLM-4-Flash** — 免费 AI 摘要服务
- **GitHub Actions** — 定时任务调度
- **飞书 Webhook** — 消息推送

## ⚠️ 注意事项

1. **Twitter 限制** — 未登录状态下只能获取有限推文，建议监控不超过 50 个账号
2. **API 免费额度** — 智谱 GLM-4-Flash 完全免费无限调用
3. **运行时间** — 每次运行约 5-10 分钟，取决于监控账号数量
4. **时区设置** — GitHub Actions 使用 UTC 时间，已配置为北京时间 8:00
5. **报告清理** — reports 目录下超过 30 天的报告会被自动删除

## 📝 更新日志

### 2026-04-15
- ✨ 添加 Dario Amodei（Anthropic CEO）到监控名单
- ✨ 添加报告自动保存到 reports 目录功能
- ✨ 添加 30 天自动清理过期报告功能
- 📝 更新 README 文档

### 2026-04-14
- 🎉 项目初始化
- ✨ 支持 AI 大牛监控
- ✨ 集成智谱 GLM-4-Flash AI 摘要
- ✨ 飞书推送功能

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**
