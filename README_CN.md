# HealthLens Platform —— 更安全的 AI 健康咨询平台

<p align="right">
  <a href="./README.md">English</a> | <a href="./README_CN.md">中文</a>
</p>

> **在线体验：** **[https://healthlens-ai.co.uk](https://healthlens-ai.co.uk)**
> &nbsp;·&nbsp; 🎬 **视频讲解：** [YouTube](https://youtu.be/your-video-id) · [Bilibili](https://www.bilibili.com/video/your-video-id)
>
> 内置演示账号可一键体验：**`demo@healthlens.demo` / `demo1234`**（每日 20 次分析）。

**HealthLens Platform** 是一个完整的**医疗 AI 全栈产品**，而不只是单一 API。它将
**React + TypeScript** 前端、**Spring Boot（Java 21）** 后端、**FastAPI（Python）** AI 管线与
**PostgreSQL** 持久化整合为一套可部署平台，用于结构化、安全的健康咨询工作流，并已在**香港服务器**上
通过 **Nginx + HTTPS** 正式上线。

> **免责声明：** 本项目是产品设计与工程原型，**不是医疗器械，不构成医疗建议**，
> 也**不得用于**诊断、治疗或临床决策。

---

## 目录

- [项目概述](#项目概述)
- [技术栈总览](#技术栈总览)
- [核心功能](#核心功能)
- [架构](#架构)
- [健康咨询工作流](#健康咨询工作流)
- [分析模式（Mock / OpenAI / DeepSeek）](#分析模式mock--openai--deepseek)
- [部署与网络说明（重要）](#部署与网络说明重要)
- [快速开始](#快速开始)
- [API 概览](#api-概览)
- [测试与 CI](#测试与-ci)
- [环境变量](#环境变量)
- [安全策略](#安全策略摘要)
- [局限性与路线图](#局限性)

---

## 项目概述

当用户输入「胸口发闷、喘不上气」时，这类咨询天然不确定、被焦虑驱动、且关乎安全。
通用聊天机器人也许回答得很流畅——但有时也很危险。

HealthLens 让每条健康描述流经一条**设计好的咨询工作流**：信号提取 → 风险裁定（规则
和/或 AI）→ 规则安全网 → 紧急升级 → 面向健康状况的说明 → 安全校验。**Mock 模式**下
由规则单独裁定风险；**AI 模式**（OpenAI/DeepSeek）下 AI 先裁定，规则只能**抬高**风险、不能降低。

本仓库是 **平台版**：用户账号、JWT 保护接口、按用户的分析历史（含清空）、按账号的每日额度、
中英文界面、可切换的 **Mock / OpenAI / DeepSeek** 分析模式、Docker Compose 一键本地全栈运行、
GitHub Actions CI，以及一套正式上线的生产部署。

---

## 技术栈总览

一个仓库同时展示 **全栈 + AI 工程 + DevOps**，跨越三种语言。

| 层 | 技术 |
| --- | --- |
| **前端** | React 19、TypeScript、Vite、React Router、Axios、Context API（认证 / 国际化 / 分析模式）、Vitest、自定义 CSS |
| **后端** | Java 21、Spring Boot 3.3、Spring Security、JWT（jjwt）、Spring Data JPA / Hibernate、Bean Validation、BCrypt、RestClient、Maven |
| **AI 服务** | Python 3、FastAPI、Pydantic v2、OpenAI SDK（OpenAI 与 DeepSeek 均通过 Chat Completions 调用）、确定性正则提取器、pytest |
| **数据库** | PostgreSQL 16、Flyway 版本化迁移 |
| **基础设施** | Docker & Docker Compose（多服务）、Nginx 反向代理 + HTTPS、GitHub Actions CI、基于 `.env` 的配置 |
| **工程实践** | 分层架构、DTO 校验、全局异常处理、Provider 抽象（Mock/OpenAI/DeepSeek）、单元 + 集成测试、国际化、健康检查、密钥隔离 |

**面试可重点讲的亮点**

- **多语言微服务架构** —— Java 编排层通过内部 HTTP 调用 Python AI 服务，最上层是 TypeScript SPA。
- **带安全默认值的 Provider 抽象** —— LLM Provider（Mock / OpenAI / DeepSeek）按请求可插拔选择；
  未知 Provider 会**显式报错**，而不是悄悄用付费模型兜底。
- **安全优先的 AI 设计** —— 规则引擎作为安全网，只能**抬高**风险；关键词紧急升级器可覆盖偏低的体征风险。
- **生产级关注点** —— JWT 认证、BCrypt 加密、Flyway 迁移、按账号每日限流、CORS 配置、
  全局错误响应、HTTPS 部署。

---

## 核心功能

| 功能 | 说明 |
| --- | --- |
| **Mock / OpenAI / DeepSeek 模式** | 分析页按请求选择模式；**生产默认 DeepSeek**，规则安全网始终生效 |
| **结构化 AI 管线** | 提取 → 规则风险 → AI 风险裁定 → 紧急升级 → 说明 → 安全校验 |
| **紧急覆盖** | 红旗症状（胸痛、中风征象、呼吸困难、出血等）提升分诊，即使数字体征风险仍为低 |
| **按风险分级的说明** | 低风险：安慰 + 日常建议；中风险：可能原因 + 步骤；高/紧急：急救电话 + 第一步措施 |
| **JWT 认证** | 注册、登录、受 JWT 保护的分析接口；密码使用 BCrypt 加密 |
| **按用户的分析历史** | 持久化、浏览、查看详情，并支持**清空全部** |
| **每日额度** | 按账号的每日分析上限（默认 10，演示账号 20），服务端强制并在界面展示 |
| **自动创建演示账号** | 启动时自动开通演示账号，招聘方可一键体验 |
| **双语界面与提取** | 中英文界面与 API；中英文体征模式（如 `heart rate 200` 与 `心率200`） |
| **全栈 Docker 化** | 一条命令启动前端、后端、AI 服务与 Postgres；前端源码挂载便于热更新 |
| **CI** | GitHub Actions 运行后端、AI 服务与前端检查 |

---

## 架构

```text
浏览器（https://healthlens-ai.co.uk）
        |
        v
Nginx 反向代理  +  HTTPS/TLS    （香港服务器）
        |
        |  提供 SPA 静态资源 & 代理 /api/*
        v
React + TypeScript（前端 :5173 开发 / 生产为静态构建）
        |
        | REST  /api/*（受保护路由需 JWT）
        v
Spring Boot（后端 :8080）   ── JWT 认证 · 校验 · 额度 · 持久化
        |
        | 内部 HTTP  POST /analyse
        v
FastAPI AI 服务（:8000）    ── 提取 · 风险裁定 · 升级 · 说明 · 安全校验
        |
        v
PostgreSQL（:5432）         ── 用户 + 分析历史（Flyway 迁移）
```

![平台架构](./docs/images/01-architecture.png)

| 层 | 技术 | 职责 |
| --- | --- | --- |
| 前端 | React 19 + TypeScript + Vite | 认证页、分析界面、历史、国际化、模式选择、额度展示 |
| 后端 | Spring Boot 3 + Java 21 | JWT 认证、请求校验、分析编排、每日额度、持久化 |
| AI 服务 | FastAPI + Pydantic | 完整分析管线 + 评估套件；Provider 抽象 |
| 数据库 | PostgreSQL + Flyway | 用户（`V2`）、分析记录（`V3`）、版本化迁移 |
| 基础设施 | Docker Compose、Nginx、GitHub Actions | 本地全栈、生产反向代理 + HTTPS、CI |

### 仓库结构

```text
healthlens-platform/
├── frontend/          React SPA（TypeScript、Vite）
├── backend/           Spring Boot API（Java 21、Maven）
├── ai-service/        FastAPI 内部 AI 分析服务（Python）
├── docs/              平台架构、API 契约、部署文档
├── infra/             Postgres / nginx 说明
├── docker-compose.yml 本地多服务编排
├── Makefile           常用命令（Unix）
└── .env.example       环境变量模板
```

---

## 健康咨询工作流

```text
用户输入（React）— mode: mock | openai | deepseek
   ↓
Spring Boot  POST /api/analysis（JWT · 校验 · 每日额度 · 持久化）
   ↓
FastAPI AI 服务
   ↓
信号提取              （regex/mock 或 OpenAI/DeepSeek → 结构化字段）
   ↓
规则风险（安全网）    （始终计算）
   ↓
风险裁定              mock：仅规则
                      ai：  AI 裁定 → 与规则合并（取较高等级，不降级）
   ↓
紧急升级              （红旗关键词 → 可强制紧急分诊与风险等级）
   ↓
情况说明              （AI 模式下 LLM 解读 + 分级行动建议模板）
   ↓
安全校验              （免责声明、禁止诊断/用药 — 中英文）
   ↓
写入 PostgreSQL 并返回前端
```

**关键设计：** **AI 模式**下 AI 先裁定风险，**规则引擎作安全网**且只能抬高风险。
**Mock 模式**下仅规则裁定。仅症状、无数字体征的紧急情况由**升级检测器**
（`ai-service/app/escalation.py`）捕获。详见
[`ai-service/docs/TRIAGE_POLICY.md`](./ai-service/docs/TRIAGE_POLICY.md)。

### 平台能评估哪些方面

> **不是诊断。** 系统对自由文本健康描述做**风险分诊与安全提示**，不能替代临床诊断。

| 类别 | 输入示例 | 用途 |
| --- | --- | --- |
| **心率** | `heart rate 100`、`心率200` | 阈值标志（>100 偏高，>120 很高） |
| **血压** | `BP 150/95`、`血压200` | 升高 / 极高收缩压或舒张压 |
| **情绪** | anxious、焦虑、压力大、心情低落 | 焦虑/压力或情绪低落标志 |
| **睡眠** | can't sleep、睡不着、失眠 | 睡眠质量差标志 |
| **紧急症状** | 胸痛、呼吸困难、中风征象、大出血等 | 关键词升级 → **紧急**分诊（无需数字体征） |
| **自由症状描述** | 「胸口发闷」「浑身不舒服」 | **AI 模式**下理解更好；Mock 依赖规则/关键词 |

**暂不支持：** 血糖、体温、血氧、化验、影像、用药分析或经临床验证的协议。

---

## 分析模式（Mock / OpenAI / DeepSeek）

**默认模式：DeepSeek** —— 新访客以及不带 `mode` 的 API 请求都走 DeepSeek。用户可随时在分析页
切换到 **Mock**、**OpenAI** 或 **DeepSeek**。

| | **Mock** | **OpenAI** | **DeepSeek** |
| --- | --- | --- | --- |
| **用途** | 离线演示、CI、零 API 成本 | 本地开发或 OpenAI 部署 | 香港线上部署（默认） |
| **提取** | 正则 / 预设样例 | OpenAI → 结构化字段 | DeepSeek → 结构化字段；失败则 regex 回退 |
| **风险** | 仅规则 | AI 裁定 → 规则安全网 | DeepSeek 裁定 → 规则安全网 |
| **说明** | 模板化「情况说明」 | OpenAI Chat Completions + 行动建议 | DeepSeek Chat Completions + 行动建议 |
| **Provider 标签** | `mock` | `openai` 或 `mock-ai`（无 Key） | `deepseek` |
| **切换** | 从付费模式切到 Mock 时弹出**确认对话框** | | |

服务端环境变量（`LLM_PROVIDER` / `EXTRACTOR_PROVIDER`）决定后端实现的默认行为与评估套件；
未知取值会**报错**，不会悄悄回退到付费模型。API Key 只能保存在本地或服务器 `.env` 中，
不能提交 Git、写入日志或前端代码。

---

## 部署与网络说明（重要）

线上站点运行在**香港服务器**上，前面是 **Nginx + HTTPS**：
**[https://healthlens-ai.co.uk](https://healthlens-ai.co.uk)**。

测试时请留意以下真实网络约束：

### 1）大陆访问可能有延迟 / 丢包

- 服务器位于**香港**，从中国大陆访问需要**跨境**。跨境路由可能带来**延迟**和偶发**丢包**，
  因此首次加载或分析请求可能较慢，甚至偶尔超时。
- 站点**未做 ICP 备案**（海外/香港部署属正常情况）；从大陆访问的稳定性通常不如香港或国际网络。
- **如果某次请求较慢或失败，直接重试即可。** 网络越快越稳（香港、国际或优质线路），体验越好。

### 2）OpenAI 地域限制

- **OpenAI 的 API 在香港 / 中国大陆地区不可用。** 从香港服务器发起时，即使 Key 有效，
  **OpenAI 模式也可能失败或被拒绝**。
- 因此**生产默认使用 DeepSeek** —— 它的 API 从香港服务器可正常访问，用于线上演示。
- **OpenAI 模式主要用于在受支持地区的本地开发**，或部署在其他受支持区域。若你在线上选择
  OpenAI 模式并报错，这属于预期中的地域限制 —— 请切换到 **DeepSeek**（或 **Mock**）。
- OpenAI 支持的国家/地区列表：
  <https://help.openai.com/en/articles/8660928-openai-api-supported-countries-and-territories>

---

## 快速开始

### Docker Compose（推荐）

```bash
cp .env.example .env
docker compose up -d --build
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

然后打开 **http://localhost:5173** → 注册或使用**演示账号**
（`demo@healthlens.demo` / `demo1234`）→ 默认分析模式为 **DeepSeek**
（可在分析页切换到 Mock 或 OpenAI）。

修改前端代码后请强制刷新浏览器（`Ctrl+Shift+R`）。Compose 已将 `./frontend` 挂载进容器以便热更新。

### 服务地址（本地）

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:5173 |
| 后端健康检查 | http://localhost:8080/api/health |
| AI 服务 | http://localhost:8000/health |
| AI OpenAPI | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### 典型使用流程

1. 在 `/register` 或 `/login` **注册**或**登录**。后端启动时会自动创建**演示账号**
   （`demo@healthlens.demo` / `demo1234`，**每日 20 次**）；登录页展示凭据并提供一键填入按钮。
   普通账号使用默认额度（`ANALYSIS_DAILY_LIMIT`，通常为 10）。
2. 在分析页切换 **English / 中文**；默认模式为 **DeepSeek**（也可手动切到 **Mock** / **OpenAI**）。
3. 输入健康描述（或使用示例文本）并提交。
4. 查看分诊、体征风险、「情况说明」、Provider 标签与安全校验。
5. 在**历史**页浏览记录、查看详情或**清空历史**。分析页底部会显示每日额度（已用 / 上限）。

单独启动各服务：[`docs/development.md`](./docs/development.md)。

---

## API 概览

### 对外 API — Spring Boot（`/api`）

| 方法 | 路径 | 认证 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/api/health` | — | 后端健康检查 |
| `POST` | `/api/auth/register` | — | 注册账号，返回 JWT |
| `POST` | `/api/auth/login` | — | 登录，返回 JWT |
| `POST` | `/api/analysis` | JWT | 提交健康描述并持久化（受额度限制） |
| `GET` | `/api/analysis` | JWT | 当前用户历史列表 |
| `GET` | `/api/analysis/{id}` | JWT | 分析详情 |
| `GET` | `/api/analysis/quota` | JWT | 当前每日额度（上限 / 已用 / 剩余） |
| `DELETE` | `/api/analysis` | JWT | 清空当前用户全部历史 |

```http
POST /api/analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "胸口痛，喘不上气。",
  "language": "zh",
  "mode": "deepseek"
}
```

`language`：`"en"` 或 `"zh"`（与界面同步）。`mode`：`"mock"`、`"openai"`、`"deepseek"`
或旧版 `"ai"`（缺省时默认 **`deepseek`**）。达到每日上限时，API 返回 **HTTP 429** 及中英文提示。

### 内部 API — FastAPI（后端 → ai-service）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/analyse` | 运行咨询工作流 |
| `POST` | `/evaluation/run?provider=mock` | 运行安全与质量评估套件 |

完整契约：[`docs/api-contracts.md`](./docs/api-contracts.md)。

---

## 测试与 CI

```bash
# 全部（Make，Unix）
make test

# AI 服务
cd ai-service && pip install -r requirements.txt && pytest -v

# 后端
cd backend && ./mvnw test        # Windows: .\mvnw.cmd test

# 前端单元测试 + 构建
cd frontend && npm ci && npm test && npm run build
```

评估套件（mock 模式，无需 API Key）：

```bash
curl -X POST "http://127.0.0.1:8000/evaluation/run?provider=mock"
```

**持续集成：** GitHub Actions 在 push/PR 时运行后端、AI 服务与前端检查。

---

## 环境变量

复制 `.env.example` 为 `.env`。主要变量：

| 变量 | 用途 |
| --- | --- |
| `POSTGRES_*` | 数据库凭据 |
| `AI_SERVICE_BASE_URL` | 后端 → FastAPI（Docker 内为 `http://ai-service:8000`） |
| `VITE_API_BASE_URL` | 前端 → 后端（Docker 内为 `/api`，由 Vite 代理到 backend） |
| `JWT_SECRET` | 令牌签名（**生产环境必填**） |
| `JWT_EXPIRATION_MS` | 令牌有效期（默认 24 小时） |
| `ANALYSIS_DAILY_LIMIT` | 按账号的每日分析上限（默认 10） |
| `DEMO_ACCOUNT_*` / `DEMO_ANALYSIS_DAILY_LIMIT` | 自动创建的演示账号及其更高额度（默认 20） |
| `LLM_PROVIDER` | `mock` \| `openai` \| `deepseek` —— AI 服务 LLM 后端（默认 **`deepseek`**） |
| `EXTRACTOR_PROVIDER` | 默认 **`deepseek`**；离线演示可设为 `mock` |
| `OPENAI_API_KEY` | **OpenAI 模式** —— 仅写在 `.env`（勿提交 Git） |
| `DEEPSEEK_API_KEY` | **DeepSeek 模式** —— `LLM_PROVIDER=deepseek` 时必填 |
| `DEEPSEEK_BASE_URL` | 默认 `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 默认 `deepseek-v4-flash` |
| `DEEPSEEK_TIMEOUT_SECONDS` | 默认 `60` |
| `ENABLE_LEGACY_FRONTEND` | 在 AI 服务上暴露旧版静态 UI（`/legacy`） |

切勿提交真实密钥。生产 JWT 配置见 [`docs/deployment.md`](./docs/deployment.md)。

---

## 安全策略（摘要）

五层设计 —— 完整说明见
[`ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md`](./ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md)：

1. 医疗范围检测
2. 不安全建议防护（不诊断 / 不开药）
3. 风险感知回复
4. 紧急升级（覆盖以体征为主的风险等级）
5. 高风险情况引导人工就医

核心原则：**不对称的审慎** —— 不确定时宁可升级，也不轻易安慰。

---

## 局限性

- **非临床用途。** 阈值与红旗模式为演示设计，非经临床验证的协议。
- **体征导向的规则引擎。** 症状类紧急依赖关键词；Mock 模式下新颖表述可能漏检。
- **Mock 模式准确性低。** 正则提取与纯规则仅供演示/CI —— 正式分析请用 AI 模式。
- **地域 / 网络约束。** 香港地区无法使用 OpenAI 模式；大陆访问可能有延迟/丢包
  （见[部署与网络说明](#部署与网络说明重要)）。

## 路线图

- [x] Mock / OpenAI / DeepSeek 模式与规则安全网
- [x] 中英文说明与安全校验（免责声明）
- [x] 分析历史清空 + 按账号每日额度
- [x] 生产部署（香港服务器 Nginx + HTTPS）
- [ ] 扩展红旗覆盖与升级指标
- [ ] 多轮澄清式追问
- [ ] 临床专家审核阈值与红旗词表
- [ ] 扩展体征（体温、血氧等）与症状提取

---

## 许可证

作品集 / 演示用途。不得用于临床场景。
