# 提示词分享平台 - 极简MVP架构文档

## 1. 架构概览

本MVP采用**单一服务**的极简架构设计：

- **FastAPI应用**: 24/7运行，同时提供管理功能和公开访问功能
- **认证机制**: 管理端点通过HTTP Basic Auth保护，公开端点匿名访问
- **数据存储**: 本地SQLite数据库（启用WAL模式）

```
博主管理 ──> FastAPI(/admin/*) ──┐
                                  ├──> SQLite(prompts.db)
公众访问 ──> FastAPI(/*) ─────────┘
```

## 2. 核心组件

### 2.1 FastAPI应用 (单一服务)
- **用途**: 统一服务，同时处理管理和公开访问
- **认证**: 管理端点使用HTTP Basic Auth保护
- **管理功能**: 提示词CRUD、分类管理、标签管理（/admin/*路径）
- **公开功能**: 服务器端渲染、复制计数、点赞、筛选（/*路径）
- **技术**: FastAPI + Jinja2 + SQLAlchemy + Python-Markdown + Tailwind CSS + Alpine.js
- **端口**: 8080 (单一端口)

### 2.2 数据存储
- **数据库**: SQLite (`prompts.db`)
- **模式**: WAL模式优化并发读写
- **权限**: 严格文件系统权限控制

## 3. 数据模型

```sql
-- 提示词表
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    category_id INTEGER,
    like_count INTEGER DEFAULT 0,
    copy_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- 提示词-标签关联表
CREATE TABLE prompt_tags (
    prompt_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (prompt_id, tag_id)
);

-- 点赞记录表（防重复点赞）
CREATE TABLE prompt_likes (
    prompt_id INTEGER,
    ip_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prompt_id, ip_hash)
);
```

## 4. API设计

### 4.1 管理端点 (需认证)
```
POST /admin/prompts          # 创建提示词
PUT  /admin/prompts/{id}     # 更新提示词
DELETE /admin/prompts/{id}   # 删除提示词
GET  /admin/prompts          # 管理提示词列表
POST /admin/categories       # 创建分类
POST /admin/tags             # 创建标签
```

### 4.2 公开端点 (匿名访问)
```
# 页面路由 (Jinja2渲染)
GET  /                       # 首页（提示词列表）
GET  /prompt/{id}            # 提示词详情页
GET  /category/{name}        # 分类筛选页
GET  /tag/{name}             # 标签筛选页

# 交互API
POST /api/prompts/{id}/copy  # 复制计数 +1
POST /api/prompts/{id}/like  # 点赞操作
```

## 5. 前端技术栈

- **模板引擎**: Jinja2（服务器端渲染）
- **样式框架**: Tailwind CSS
- **UI组件**: Basecoat UI（Shadcn风格的HTML组件）
- **轻量交互**: Alpine.js（复制按钮、点赞按钮）
- **Markdown渲染**: Python-Markdown（服务器端）

## 6. 部署架构

```
本地服务器
├── prompts.db (SQLite数据库)
└── FastAPI应用 (端口8080, 24/7运行)
    ├── /admin/* (需认证)
    ├── /* (公开访问)
    └── uvicorn main:app --port 8080
```

## 7. 安全机制

- **管理端点**: HTTP Basic Auth认证保护
- **公开端点**: IP限频防滥用（点赞、复制）
- **数据安全**: Pydantic输入校验、XSS防护
- **文件权限**: SQLite文件严格权限控制
- **HTTPS**: 强制HTTPS访问

## 8. 开发工具

- **包管理**: uv
- **启动命令**: 
  - 开发: `uv run uvicorn main:app --reload --port 8080`
  - 生产: `uv run uvicorn main:app --port 8080`
- **依赖**: FastAPI, Jinja2, SQLAlchemy, Python-Markdown, Tailwind CLI

## 9. MVP后扩展方向

- 用户系统和权限管理
- 全文搜索功能（SQLite FTS）
- 数据库扩展或云数据库
- 云部署方案
- 评论和分享功能
