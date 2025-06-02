# **提示词分享平台 - 极简MVP设计文档 (design.md)**

## **1. 设计概览**

本MVP采用**单一FastAPI应用**架构，通过路径和认证机制区分管理功能和公开功能：

- **管理功能**: `/admin/*` 路径，HTTP Basic Auth认证保护
- **公开功能**: `/*` 路径，匿名访问
- **统一数据**: SQLite数据库统一存储，WAL模式优化并发

**核心设计原则**: 极简、零配置、本地优先、易维护

## **2. 核心模块设计**

### **2.1. 数据模型设计**

**核心表结构:**
- `prompts`: 提示词主表（id, title, content_markdown, category_id, like_count, copy_count, timestamps）
- `categories`: 分类表（id, name, description）
- `tags`: 标签表（id, name）
- `prompt_tags`: 多对多关联表（prompt_id, tag_id）
- `prompt_likes`: 点赞记录表（prompt_id, ip_hash）防重复点赞

**Pydantic模型:**
- `PromptCreate/Update/Read`: 提示词数据模型
- `CategoryCreate/Read`: 分类数据模型  
- `TagCreate/Read`: 标签数据模型

### **2.2. 认证与权限设计**

**双层访问控制:**
- **管理端点**: HTTP Basic Auth，环境变量配置用户名密码
- **公开端点**: 无认证，IP限频防滥用（点赞、复制）

**权限逻辑:**
```python
# 管理端点装饰器
@admin_required  # HTTP Basic Auth
async def admin_endpoints():
    pass

# 公开端点装饰器  
@rate_limit(ip_based=True)  # IP限频
async def public_endpoints():
    pass
```

### **2.3. 路由设计**

**管理路由 (/admin/*):**
- `POST /admin/prompts` - 创建提示词
- `PUT /admin/prompts/{id}` - 更新提示词
- `DELETE /admin/prompts/{id}` - 删除提示词
- `GET /admin/prompts` - 管理列表页面
- `POST /admin/categories` - 创建分类
- `POST /admin/tags` - 创建标签

**公开路由 (/*) :**
- `GET /` - 首页（Jinja2渲染）
- `GET /prompt/{id}` - 提示词详情页
- `GET /category/{name}` - 分类筛选页
- `GET /tag/{name}` - 标签筛选页
- `POST /api/prompts/{id}/copy` - 复制计数
- `POST /api/prompts/{id}/like` - 点赞操作

## **3. 前端设计**

### **3.1. 技术栈**
- **服务器端渲染**: Jinja2模板引擎
- **样式框架**: Tailwind CSS
- **UI组件**: Basecoat UI（Shadcn风格）
- **轻量交互**: Alpine.js（复制、点赞按钮）

### **3.2. 页面结构**
- **首页**: 提示词列表、分类筛选、标签筛选、热门排序
- **详情页**: Markdown内容渲染、复制按钮、点赞按钮
- **管理页**: 简单的CRUD表单（仅管理员可访问）

### **3.3. 响应式设计**
- 移动优先设计
- Tailwind断点适配
- 核心功能在所有设备可用

## **4. 数据交互设计**

### **4.1. 数据库操作**
- **连接管理**: 上下文管理器确保连接释放
- **事务处理**: 多表操作使用事务保证一致性
- **WAL模式**: 优化读写并发性能

### **4.2. 核心业务逻辑**
- **提示词创建**: 主表插入 + 标签关联（事务）
- **提示词更新**: 基础信息更新 + 标签关联重建
- **统计操作**: 原子性计数更新 + IP去重

## **5. 安全与性能设计**

### **5.1. 安全机制**
- **输入校验**: Pydantic模型自动验证
- **XSS防护**: Jinja2自动转义 + Markdown安全渲染
- **防滥用**: IP基础限频（点赞、复制）
- **文件权限**: SQLite文件严格权限控制

### **5.2. 性能优化**
- **数据库索引**: 常用查询字段建索引
- **分页查询**: LIMIT/OFFSET基础分页
- **缓存策略**: 分类标签内存缓存（可选）

## **6. 部署设计**

### **6.1. 单一服务部署**
```bash
# 开发环境
uv run uvicorn main:app --reload --port 8080

# 生产环境  
uv run uvicorn main:app --port 8080
```

### **6.2. 零配置启动**
- 自动创建SQLite数据库和表结构
- 自动插入默认分类和标签
- 环境变量配置管理员认证信息

### **6.3. 数据管理**
- SQLite文件直接备份
- 日志记录关键操作
- 错误统一处理和记录

## **7. 扩展考虑**

### **7.1. 功能扩展**
- 用户系统（多用户支持）
- 全文搜索（SQLite FTS）
- 评论系统
- API版本控制

### **7.2. 技术升级**
- 数据库扩展（SQLite扩展或云数据库）
- 云部署（Docker容器化）
- 缓存层（Redis）
- 监控和日志系统