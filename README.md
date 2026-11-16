# AI-Text-Processor (基于大模型 API 的全栈智能翻译系统)

## 📖 项目简介
本项目是一个从零手写的轻量级全栈 AI 应用。实现了从浏览器交互到本地数据库持久化的完整闭环。前端提供可视化聊天界面，后端通过调用云端大模型（DeepSeek）对用户输入的文本进行多语言翻译，并将所有对话记录结构化存储至关系型数据库。

## 🛠️ 技术栈
- **后端与并发**：Python 3, Flask, Threading, Queue (生产者-消费者模型)
- **网络通信**：**Requests** (原生 HTTP 请求封装，未依赖第三方 SDK)
- **前端交互**：HTML5, CSS3, JavaScript (Fetch API, FormData 表单上传, 轮询机制)
- **数据库**：MySQL (PyMySQL 驱动, 参数化查询防注入)
- **AI 能力**：DeepSeek API (大模型对话), RapidOCR (多模态图片文字识别)
- **开发工具**：PyCharm, Git, AI 辅助编程工具 (Harness)

## ⚙️ 核心功能与架构
1. **前后端分离**：前端使用原生 Fetch API 发送异步请求；后端使用 Flask 搭建 RESTful API（包含 `/chat` 处理对话与 `/history` 获取历史记录）。
2. **大模型 API 接入**：使用 `requests` 库独立封装 API 调用模块，通过自定义 System Prompt 实现多语言自动识别与翻译，并处理鉴权与网络异常。
3. **数据持久化**：使用 MySQL 设计 `messages` 数据表，通过 `PyMySQL` 建立连接，实现参数化 SQL 插入（防注入）与历史记录的可靠读取。
4. **工程安全化**：敏感配置（API Key 与数据库密码）已在代码中脱敏，符合基本的开发安全规范。
