# 互联网+智慧护理移动护理平台 APP

一个面向居家养老与上门护理场景的全栈项目，包含后端 API、前端页面、Vue 开发版、数据库初始化脚本以及 Docker 部署方案。

## 项目结构

- `backend/`：Flask 后端服务
- `frontend/`：传统静态页面
- `frontend-vue/`：Vue 前端开发版
- `deploy/`：Docker Compose 与 Nginx 配置
- `docs/`：项目文档与图片资源

## 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8+
- Redis 7+
- Docker / Docker Compose（可选）

## 安装依赖

### 1. 安装后端依赖

进入 `backend` 目录后安装 Python 依赖：

```bash
cd backend
pip install -r ../requirements.txt
```

如果你使用的是虚拟环境，建议先创建并激活虚拟环境，再执行上述命令。

### 2. 安装前端依赖

进入 `frontend-vue` 目录后安装前端依赖：

```bash
cd frontend-vue
npm install
```

## 数据库初始化

在后端依赖安装完成后，执行数据库初始化脚本：

```bash
cd backend
python seed.py
```

> 说明：`seed.py` 会创建表结构并初始化基础服务项目数据。

## 启动项目

### 方式一：本地开发联调

#### 启动后端

```bash
cd backend
python run.py
```

后端默认地址：

- `http://127.0.0.1:5000/`
- API 前缀：`http://127.0.0.1:5000/api/...`

#### 启动前端开发环境

```bash
cd frontend-vue
npm run dev
```

前端开发地址：

- `http://127.0.0.1:5173`

### 方式二：生产/演示模式

#### 先构建前端

```bash
cd frontend-vue
npm run build
```

#### 再启动后端

```bash
cd ../backend
python run.py
```

然后访问：

- 项目首页：`http://127.0.0.1:5000/`
- 管理端：`http://127.0.0.1:5000/admin`

## Docker 部署

如果你使用 Docker 部署，可以直接执行：

```bash
cd deploy
docker compose up -d
```

## 常用命令

### 后端

```bash
cd backend
python seed.py
python run.py
```

### 前端开发版

```bash
cd frontend-vue
npm install
npm run dev
npm run build
```

## Git 提交

```bash
git add .
git commit -m "更新内容"
git push
```

## 说明

- 后端已逐步迁移为异步数据库架构。
- 若更改了数据库配置，请确认 `backend/app/config.py` 中的 `DATABASE_URL` 已正确设置。
- 如果你使用 Docker，请优先确认 MySQL 和 Redis 服务已正常启动。
