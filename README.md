# 提示词分享平台 - 后端 MVP

这是一个"小而美"的提示词分享平台后端服务，旨在让博主能够方便地发布、管理他们日常高频使用的提示词（Prompts）。

## 技术栈

- **框架**: FastAPI
- **语言**: Python 3.9+
- **环境管理**: uv
- **数据库**: Supabase (PostgreSQL)
- **认证**: Supabase Auth (JWT)
- **部署**: Vercel

## 快速开始

### 环境要求

- Python 3.9+
- uv (推荐) 或 pip

### 安装依赖

使用 uv（推荐）：
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/Scripts/activate  # Windows Git Bash
# 或 source .venv/bin/activate  # Linux/macOS

# 安装依赖
uv pip install -r requirements.txt
```

使用 pip：
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/Scripts/activate  # Windows Git Bash
# 或 source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt
```

### 运行应用

```bash
uvicorn main:app --reload --port 8080
```

### 验证安装

访问以下端点确认应用正常运行：

- 主页: http://localhost:8080/
- 健康检查: http://localhost:8080/health
- API 文档: http://localhost:8080/docs

## 项目结构

```
prompt-repo/
├── app/                    # 应用代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── auth/              # 认证相关模块
│   ├── prompts/           # 提示词管理模块
│   ├── categories/        # 分类管理模块
│   ├── tags/              # 标签管理模块
│   └── models/            # Pydantic 模型
├── tests/                 # 测试代码
├── docs/                  # 项目文档
├── .venv/                 # 虚拟环境
├── main.py               # 项目入口点
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

## 开发规范

- 每个 Python 文件代码行数（不包括空行和注释）不超过 100 行
- 遵循原子任务与顺序执行原则
- 文档优先、测试优先的开发理念
- 严格的版本控制与持续集成

## 文档

详细的项目文档请查看 `docs/` 目录：

- [需求文档 (PRD)](docs/PRD.md)
- [架构文档](docs/arch.md)
- [设计文档](docs/design.md)
- [实现文档](docs/impl.md)
- [任务清单](docs/task-todo.md)

## 许可证

MIT License 