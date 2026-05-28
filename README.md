# 小旅 — AI 旅行规划助手

基于 DashScope (qwen-plus) 的对话式旅行规划助手，单文件 HTML 应用，浏览器端运行。

## 快速开始

```bash
npx http-server -p 8080
# 浏览器打开 http://localhost:8080/index.html
```

首次使用需点击右上角 ⚙ 设置 DashScope API Key（阿里云百炼平台申请）。

## 功能

- **对话式行程规划**：自然语言描述需求，AI 自动提取目的地/天数/人数/风格/预算
- **多轮信息收集**：按优先级逐一询问缺失信息，支持长期偏好记忆（旅伴、饮食、健康等）
- **风格匹配**：休闲/蜜月/打卡/特种兵/亲子/老年 — 不同风格调整景点密度和行程节奏
- **天气查询**：国内和风天气 + 国际 Open-Meteo 自动切换，含 WMO 天气码/风向/风力转换
- **POI 搜索**：国内高德地图景点美食搜索 + 国际 Tabiji 目的地信息
- **民俗文化卡片**：3-5 张迷你翻转卡片（正面民俗名 + 图片 → 翻转 → 背面简介毛玻璃效果）
- **每日行程流式时间轴**：竖线时间轴 + 景点卡片 + 美食/贴士节点
- **侧边栏历史记录**：历史计划归档/恢复/删除，城市背景图磨砂效果
- **暗黑主题**：完整深色模式 UI，蓝紫色渐变品牌色

## 技术栈

| 层 | 技术 |
|---|------|
| LLM | DashScope qwen-plus (OpenAI 兼容) |
| 前端 | 单文件 HTML + CSS + 原生 JS (IIFE 隔离) |
| 存储 | localStorage 持久化 |
| 天气 | 和风天气 + Open-Meteo |
| 地图 | 高德 POI + Tabiji |
| 图片 | 远方风景 API (CSS background-image) |

## API 清单

| API | 用途 | 域名 |
|-----|------|------|
| DashScope | 主力 LLM | `dashscope.aliyuncs.com` |
| 和风天气 | 国内 7 天预报 | `*.qweatherapi.com` |
| Open-Meteo | 国际天气兜底（免费） | `api.open-meteo.com` |
| 高德地图 | 国内 POI 搜索 | `restapi.amap.com` |
| Tabiji | 国际目的地信息 | `tabiji.ai` |

## 架构

```
用户输入 → ReAct Loop (最多 10 轮)
  ├── buildSystemPrompt() — 系统提示词（含风格/偏好/工具规则）
  ├── callLLM() → DashScope qwen-plus
  ├── 工具调用执行 → ToolExecutors
  │     ├── update_trip_info / update_preference
  │     ├── get_weather (和风天气 / Open-Meteo)
  │     ├── search_attractions (高德 / Tabiji)
  │     ├── lookup_destination (Tabiji)
  │     ├── calculate / resolve_conflict
  │     └── JS 正则兜底（旅伴名/人数/饮食/健康等）
  └── 方案生成 → renderPlanHTML()
        ├── buildFolkCultureCards() → 翻转卡片
        ├── buildWeatherCardsHTML() → 天气卡片
        ├── 每日行程流式时间轴
        └── applyFolkCardImages() → 背景图
```

## 数据流

- **AgentMemory**：统一管理 tripInfo / preferences / messages / tripHistory / weatherData
- **archiveCurrentTrip**：每次生成方案后自动归档（含城市背景图 URL）
- **restoreTrip**：点击历史卡片恢复完整对话状态

## 文件

| 文件 | 说明 |
|------|------|
| `index.html` | 主应用（当前版本 v5，含所有 CSS/JS） |
| `agent_demo03.html` | 上一版本 |
| `agent_demo01.py` / `agent_demo02.py` | Python 早期原型 |
| `test_verify_all.py` | Playwright 端到端测试 |
