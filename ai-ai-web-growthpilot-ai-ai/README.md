# GrowthPilot AI · 求职展示版 V1.0

面向互联网运营、新媒体运营、市场营销和创业团队的 AI 增长运营助手。GrowthPilot 将需求分析、增长策略、内容生产、数据分析和报告交付组织为一条完整工作流。

## 求职展示亮点

- **30 秒完整案例**：首页内置“北大湖滑雪民宿增长营销方案”，直接展示用户分析、市场分析、内容运营和完整报告。
- **多 Agent 工作流**：用户需求 → 市场分析 Agent → 用户洞察 Agent → 内容 Agent → 策略 Agent → 报告 Agent。
- **真实模型调用**：业务页面继续通过 OpenAI Compatible Client 调用 DeepSeek，不使用模拟模型返回。
- **一键内容包**：同时生成小红书内容、短视频脚本、公众号文章框架和营销推广文案。
- **运营数据分析**：支持 CSV / XLSX / XLS 上传，并提供可公开展示的示例运营数据。
- **企业报告输出**：生成结果支持 Markdown 展示及 PDF、Word、PPT、Excel 导出。

## 核心能力

- **Dashboard**：展示真实的今日任务、AI 工作状态、增长机会、内容产出、项目任务和当前模型状态。
- **专业 Agent**：增长策略、用户洞察、内容运营、视频创作、数据分析、运营复盘六类专业 Agent，所有 AI 结果由当前已配置模型真实返回。
- **内容中心**：全渠道内容包、小红书、公众号、短视频与内容日历；保留海报设计和图片模型接口任务。
- **视频创作**：从选题、脚本、分镜、画面描述到 AI 视频 Prompt 与发布方案；保留可灵AI、即梦AI、Runway 接口层。
- **数据分析**：上传 CSV / XLSX / XLS 文件，本地提取字段与统计摘要，交由数据分析 Agent 输出趋势、问题和优化建议。
- **项目管理**：SQLite 持久化项目、任务和 Agent 活动；当前项目会自动归档生成记录。
- **模型管理**：默认 DeepSeek，支持 OpenAI、通义千问兼容模式和自定义 OpenAI Compatible 服务；Claude Adapter 已预留。
- **报告输出**：AI 结果可导出为 Markdown、PDF、Word、PPT、Excel。
- **模板中心**：电商运营、品牌推广、新媒体运营和活动策划四类工作模板。

## 简历项目描述

> 独立设计并开发 GrowthPilot AI 增长运营助手，通过大模型 Agent 实现市场分析、内容生成、数据分析和运营方案自动化，并支持项目记录与企业报告导出。

## 本地启动

要求：Python 3.10 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port=8502
```

浏览器打开 [http://localhost:8502](http://localhost:8502)。若 `localhost` 在系统中存在 IPv6 解析问题，请不要指定 `--server.address=127.0.0.1`，保持上面的默认绑定方式。

## DeepSeek 配置

推荐新建 `.streamlit/secrets.toml`：

```toml
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

或在启动前设置：

```powershell
$env:DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

默认模型配置在 `config.py`：

```python
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
```

## 模型配置

模型密钥应放入部署平台环境变量或 Streamlit Secrets，不能写入前端页面。

```text
DEEPSEEK_API_KEY
OPENAI_API_KEY
QWEN_API_KEY
QWEN_BASE_URL
QWEN_MODEL
CUSTOM_LLM_API_KEY
CUSTOM_LLM_BASE_URL
CUSTOM_LLM_MODEL
ANTHROPIC_API_KEY
```

DeepSeek、OpenAI、通义千问兼容模式与自定义模型通过 OpenAI Compatible Client 调用。Claude 已在模型目录中注册，待后续接入 Anthropic 专属 Adapter。

## 视频与图片 Provider

`services/media_clients.py` 预留了以下接口配置：

```text
RUNWAY_API_KEY
KLING_API_KEY
JIMENG_API_KEY
TONGYI_WANXIANG_API_KEY
```

当前未写入厂商专属 SDK 调用，因此未完成真实 Provider 配置时，界面会清晰显示“等待配置 / 等待适配”，不会伪造视频或图片文件。

## 项目结构

```text
app.py                         # 多页面路由与侧边导航
app_pages/                     # Dashboard、Agent、项目、模型管理页面
services/generator.py          # 增长、内容与六类专业 Agent
services/llm_client.py         # 通用 OpenAI Compatible 调用层
services/project_store.py      # SQLite 项目、任务和活动记录
services/data_tools.py          # CSV / Excel 数据摘要
services/exporters.py           # PDF / Word / PPT / Excel 导出
services/portfolio_showcase.py  # 求职展示案例、Agent 流程与运营模板
services/media_clients.py       # 视频、图片 Provider 接口层
config.py                       # 模型注册表与密钥读取
data/growthpilot.db             # 本地运行时项目数据（不提交版本库）
```

## 公网部署

部署到 Streamlit Community Cloud、Render 或 Railway：

1. 安装：`pip install -r requirements.txt`
2. 启动：`streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
3. 在平台 Secrets / Environment Variables 配置 `DEEPSEEK_API_KEY`。
4. 生产环境请用托管 PostgreSQL / MySQL 替换 `services/project_store.py` 的 SQLite 实现，并为上传数据和导出文件配置对象存储。
