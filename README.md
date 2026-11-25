# AI-Text-Processor (全栈 AI 翻译系统)

## 📖 项目简介
本项目是一个从零手写并持续演进的全栈 AI 应用。从最初的单机 Flask 脚本，重构为**基于 Docker 容器化部署的分布式微服务架构**。前端提供可视化聊天界面，后端通过 **RabbitMQ** 进行异步任务分发，利用 **PostgreSQL** 追踪任务全生命周期状态，并使用 **Redis** 优化高频请求，彻底实现了 Web 接口与耗时 AI 任务的解耦。

## 🛠️ 技术栈
- **后端与框架**：Python 3, Flask
- **消息队列**：RabbitMQ (Pika, 死信队列, 持久化消息)
- **数据库**：PostgreSQL (Psycopg 3, 状态追踪), Redis (结果缓存)
- **网络通信**：Requests (原生 HTTP 请求封装，未依赖第三方 SDK)
- **前端交互**：HTML5, CSS3, JavaScript (Fetch API, FormData, 轮询机制)
- **AI 能力**：DeepSeek API (大模型对话), RapidOCR (多模态图片文字识别)
- **部署与运维**：Docker Compose (容器编排)
- **开发工具**：PyCharm, Git, AI 辅助编程工具 (Harness)

## ⚙️ 核心功能与架构演进

1. **分布式异步架构（核心重构）**：基于 Docker Compose 部署 RabbitMQ 与 PostgreSQL。Flask 接口收到请求后立即返回 `202 (Accepted)`，将翻译任务作为持久化消息（`delivery_mode=2`）投递至 RabbitMQ，由独立的后台 Consumer 异步消费，彻底解决耗时 API 阻塞主线程的问题。
2. **任务状态追踪与可靠性保障**：使用 PostgreSQL 设计 `translate_task` 数据表，追踪任务从 `pending` 到 `done/failed` 的全生命周期。引入 RabbitMQ 死信队列（DLQ）处理异常任务，结合手动 ACK 机制与 `prefetch_count`，确保消息不丢失、服务高可用。
3. **Redis 缓存优化**：在 Consumer 端引入 Redis，基于文本 MD5 作为 Key 缓存翻译结果（设置过期时间）。命中缓存直接落库返回，有效减少重复的 LLM 调用与 Token 消耗。
4. **原生 HTTP 协议封装**：未依赖任何官方 SDK，完全基于 `requests` 库手写 HTTP 请求。独立处理 Bearer 鉴权、JSON 序列化与异常重试，排查并解决了底层中文编码（latin-1）报错问题。
5. **多模态处理 (OCR)**：集成 RapidOCR 引擎，打通从“图片上传 -> 后端提取文字 -> 大模型翻译 -> 前端轮询返回”的完整流水线。
6. **前后端物理分离**：前端采用原生 Fetch API 与轮询机制（Polling）；后端基于 Flask 提供 RESTful API，并通过 `send_from_directory` 托管前端静态资源，消除跨域问题。
7. **工程安全化**：敏感配置（API Key 与数据库密码）完全脱敏，通过环境变量或占位符管理，符合基本开发安全规范。
