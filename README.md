# 提示词分享平台 - 极简MVP

这是一个"小而美"的提示词分享平台，采用单一FastAPI服务架构，让博主能够方便地发布、管理和分享日常高频使用的提示词（Prompts）。

## 技术栈

- **框架**: FastAPI (单一服务)
- **语言**: Python 3.12+
- **环境管理**: uv
- **数据库**: SQLite + WAL模式 (本地数据库)
- **前端**: Jinja2模板 + Tailwind CSS + Alpine.js
- **认证**: HTTP Basic Auth (管理功能)
- **部署**: 本地运行，24/7服务

## 快速开始

### 环境要求

- Python 3.12+
- uv (推荐的包管理工具)

### 快速启动

```bash
# 克隆项目
git clone <repository-url>
cd prompt-repo

# 使用uv同步环境和依赖
uv sync

# 启动应用
uv run uvicorn main:app --port 8080 --reload
```

### 传统安装方式

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows Git Bash)
source .venv/Scripts/activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pydantic

# 启动应用
uvicorn main:app --reload --port 8080
```

### 验证安装

访问以下端点确认应用正常运行：

- 主页: http://localhost:8080/
- 健康检查: http://localhost:8080/health
- 数据库状态: http://localhost:8080/db-health
- API 文档: http://localhost:8080/docs

## 当前功能状态

### ✅ 已完成
- **项目基础**: FastAPI应用框架 + uv环境管理
- **数据库**: SQLite + WAL模式，完整表结构和索引
- **数据模型**: 分类、标签、提示词、关联关系、点赞记录
- **基础CRUD**: 分类、标签、提示词的基础操作
- **健康检查**: 应用和数据库状态监控

### ✅ 已完成
- **项目基础**: FastAPI应用框架 + uv环境管理
- **数据库**: SQLite + WAL模式，完整表结构和索引
- **数据模型**: 分类、标签、提示词、关联关系、点赞记录
- **基础CRUD**: 分类、标签、提示词的基础操作
- **健康检查**: 应用和数据库状态监控
- **认证系统**: HTTP Basic Auth管理员认证 + IP限频防滥用
- **模板系统**: Jinja2模板引擎 + 静态文件服务
- **前端基础**: Tailwind CSS + Alpine.js + 响应式设计
- **分类管理**: 完整的分类CRUD API端点 + 认证保护

### 🚧 开发中
- **标签管理**: 标签的管理API端点
- **提示词管理**: 提示词的管理API端点
- **公开页面**: 提示词浏览和交互功能

### 📋 规划功能
- **提示词浏览**: 分页、筛选、排序
- **交互功能**: 点赞、复制统计、一键复制
- **搜索功能**: 按标题、内容、分类、标签搜索
- **响应式UI**: 移动端和桌面端适配

## 项目结构

```
prompt-repo/
├── app/                    # 应用代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── database.py        # 数据库连接和配置
│   ├── models.py          # SQLAlchemy 数据模型
│   ├── crud.py            # 基础CRUD操作
│   ├── auth/              # 认证相关模块 (开发中)
│   ├── prompts/           # 提示词管理模块 (规划中)
│   ├── categories/        # 分类管理模块 (规划中)
│   └── tags/              # 标签管理模块 (规划中)
├── tests/                 # 测试代码
│   └── test_database.py   # 数据库功能测试
├── docs/                  # 项目文档
│   ├── PRD.md            # 需求文档
│   ├── arch.md           # 架构文档
│   ├── design.md         # 设计文档
│   ├── impl.md           # 实现文档
│   └── task-todo.md      # 任务清单
├── .venv/                 # 虚拟环境 (uv管理)
├── prompts.db*            # SQLite 数据库文件 (自动创建)
├── main.py               # 项目入口点
├── pyproject.toml        # 项目配置和依赖
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明
```

## 当前API端点

### 基础端点
- `GET /` - 主页欢迎信息
- `GET /health` - 应用健康检查
- `GET /db-health` - 数据库状态检查
- `GET /docs` - FastAPI自动生成的API文档

### 认证端点
- `GET /admin` - 管理员仪表板 (需认证)
- `GET /api/test-rate-limit` - 限频测试端点

### 管理端点 (开发中)
- `POST /admin/categories` - 创建分类 (需认证)
- `GET /admin/categories` - 获取分类列表 (需认证)
- `PUT /admin/categories/{id}` - 更新分类 (需认证)
- `DELETE /admin/categories/{id}` - 删除分类 (需认证)
- `POST /admin/tags` - 创建标签 (需认证)
- `POST /admin/prompts` - 创建提示词 (需认证)

### 公开端点 (规划中)
- `GET /` - 提示词列表主页 (Jinja2渲染)
- `GET /prompt/{id}` - 提示词详情页
- `GET /category/{name}` - 分类筛选页
- `GET /tag/{name}` - 标签筛选页
- `POST /api/prompts/{id}/like` - 点赞提示词 (需限频)
- `POST /api/prompts/{id}/copy` - 复制统计 (需限频)

## 开发规范

- 每个 Python 文件代码行数（不包括空行和注释）不超过 100 行
- 遵循原子任务与顺序执行原则
- 文档优先、测试优先的开发理念
- 严格的版本控制与持续集成
- 极简设计、零配置启动、本地优先

## 文档

详细的项目文档请查看 `docs/` 目录：

- [需求文档 (PRD)](docs/PRD.md)
- [架构文档](docs/arch.md)
- [设计文档](docs/design.md)
- [实现文档](docs/impl.md)
- [任务清单](docs/task-todo.md)

## 许可证

MIT License 