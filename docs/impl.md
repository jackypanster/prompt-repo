# **提示词分享平台 - 极简MVP实现逻辑文档 (impl.md)**

## **1. 实现概览**

基于单一FastAPI应用架构，通过路径区分和认证机制实现管理功能和公开功能的统一服务。

**核心技术栈:**
- FastAPI + Uvicorn（Web服务）
- SQLite + sqlite3（数据存储）
- Jinja2（模板渲染）
- Pydantic（数据验证）
- Python-Markdown（Markdown渲染）

## **2. 应用架构实现**

### **2.1. FastAPI应用配置**

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="提示词分享平台", version="1.0.0")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 认证配置
security = HTTPBasic()
```

### **2.2. 认证实现**

```python
import os
from fastapi import Depends, HTTPException, status

# 管理员认证
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "password")
    
    if (credentials.username != admin_username or 
        credentials.password != admin_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# IP限频装饰器
from collections import defaultdict
import time

request_counts = defaultdict(list)

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            client_ip = request.client.host
            now = time.time()
            
            # 清理过期记录
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window_seconds
            ]
            
            # 检查限频
            if len(request_counts[client_ip]) >= max_requests:
                raise HTTPException(status_code=429, detail="请求过于频繁")
            
            request_counts[client_ip].append(now)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

## **3. 数据库实现**

### **3.1. 数据库初始化**

```python
import sqlite3
from contextlib import contextmanager

DATABASE_URL = "prompts.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """创建表结构"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            );
            
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content_markdown TEXT NOT NULL,
                category_id INTEGER,
                like_count INTEGER DEFAULT 0,
                copy_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            );
            
            CREATE TABLE IF NOT EXISTS prompt_tags (
                prompt_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (prompt_id, tag_id),
                FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS prompt_likes (
                prompt_id INTEGER,
                ip_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (prompt_id, ip_hash)
            );
        """)
```

### **3.2. 核心数据操作**

```python
from typing import List, Optional
import hashlib

class PromptService:
    @staticmethod
    def create_prompt(title: str, content: str, category_id: Optional[int], tag_ids: List[int]):
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 插入提示词
            cursor.execute("""
                INSERT INTO prompts (title, content_markdown, category_id)
                VALUES (?, ?, ?)
            """, (title, content, category_id))
            
            prompt_id = cursor.lastrowid
            
            # 插入标签关联
            for tag_id in tag_ids:
                cursor.execute("""
                    INSERT INTO prompt_tags (prompt_id, tag_id) VALUES (?, ?)
                """, (prompt_id, tag_id))
            
            conn.commit()
            return prompt_id
    
    @staticmethod
    def get_prompts(page: int = 1, limit: int = 10, category_id: Optional[int] = None):
        offset = (page - 1) * limit
        
        with get_db() as conn:
            where_clause = "WHERE p.category_id = ?" if category_id else ""
            params = [category_id] if category_id else []
            params.extend([limit, offset])
            
            prompts = conn.execute(f"""
                SELECT p.*, c.name as category_name
                FROM prompts p
                LEFT JOIN categories c ON p.category_id = c.id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """, params).fetchall()
            
            return [dict(prompt) for prompt in prompts]
    
    @staticmethod
    def like_prompt(prompt_id: int, client_ip: str):
        ip_hash = hashlib.md5(client_ip.encode()).hexdigest()
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查是否已点赞
            existing = cursor.execute("""
                SELECT 1 FROM prompt_likes WHERE prompt_id = ? AND ip_hash = ?
            """, (prompt_id, ip_hash)).fetchone()
            
            if existing:
                raise HTTPException(status_code=409, detail="已经点赞过了")
            
            # 记录点赞
            cursor.execute("""
                INSERT INTO prompt_likes (prompt_id, ip_hash) VALUES (?, ?)
            """, (prompt_id, ip_hash))
            
            # 更新计数
            cursor.execute("""
                UPDATE prompts SET like_count = like_count + 1 WHERE id = ?
            """, (prompt_id,))
            
            conn.commit()
```

## **4. 路由实现**

### **4.1. 管理端点（需认证）**

```python
from pydantic import BaseModel

class PromptCreate(BaseModel):
    title: str
    content_markdown: str
    category_id: Optional[int] = None
    tag_ids: List[int] = []

@app.post("/admin/prompts")
async def create_prompt(
    prompt: PromptCreate,
    admin: str = Depends(verify_admin)
):
    prompt_id = PromptService.create_prompt(
        prompt.title, 
        prompt.content_markdown, 
        prompt.category_id, 
        prompt.tag_ids
    )
    return {"id": prompt_id, "message": "提示词创建成功"}

@app.get("/admin/prompts")
async def admin_prompts_page(
    request: Request,
    admin: str = Depends(verify_admin)
):
    prompts = PromptService.get_prompts()
    return templates.TemplateResponse("admin/prompts.html", {
        "request": request,
        "prompts": prompts
    })
```

### **4.2. 公开端点（匿名访问）**

```python
@app.get("/")
async def home_page(request: Request):
    prompts = PromptService.get_prompts()
    categories = CategoryService.get_all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "prompts": prompts,
        "categories": categories
    })

@app.get("/prompt/{prompt_id}")
async def prompt_detail(request: Request, prompt_id: int):
    prompt = PromptService.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    
    # 渲染Markdown
    import markdown
    prompt['content_html'] = markdown.markdown(prompt['content_markdown'])
    
    return templates.TemplateResponse("prompt_detail.html", {
        "request": request,
        "prompt": prompt
    })

@app.post("/api/prompts/{prompt_id}/like")
@rate_limit(max_requests=5, window_seconds=300)
async def like_prompt(request: Request, prompt_id: int):
    client_ip = request.client.host
    PromptService.like_prompt(prompt_id, client_ip)
    return {"message": "点赞成功"}

@app.post("/api/prompts/{prompt_id}/copy")
@rate_limit(max_requests=10, window_seconds=60)
async def copy_prompt(request: Request, prompt_id: int):
    PromptService.increment_copy_count(prompt_id)
    return {"message": "复制计数已更新"}
```

## **5. 模板渲染实现**

### **5.1. Jinja2模板**

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>提示词分享平台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">提示词分享</h1>
        
        <!-- 分类筛选 -->
        <div class="mb-6">
            {% for category in categories %}
            <a href="/?category_id={{category.id}}" 
               class="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded mr-2 mb-2">
                {{category.name}}
            </a>
            {% endfor %}
        </div>
        
        <!-- 提示词列表 -->
        <div class="grid gap-6">
            {% for prompt in prompts %}
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-semibold mb-2">{{prompt.title}}</h2>
                <p class="text-gray-600 mb-4">{{prompt.content_markdown[:200]}}...</p>
                <div class="flex justify-between items-center">
                    <a href="/prompt/{{prompt.id}}" class="text-blue-600 hover:underline">
                        查看详情
                    </a>
                    <div class="text-sm text-gray-500">
                        👍 {{prompt.like_count}} | 📋 {{prompt.copy_count}}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
```

### **5.2. Alpine.js交互**

```html
<!-- 复制按钮 -->
<div x-data="{ copied: false }">
    <button @click="
        navigator.clipboard.writeText('{{prompt.content_markdown}}');
        fetch('/api/prompts/{{prompt.id}}/copy', {method: 'POST'});
        copied = true;
        setTimeout(() => copied = false, 2000);
    " class="bg-blue-500 text-white px-4 py-2 rounded">
        <span x-show="!copied">复制</span>
        <span x-show="copied">已复制</span>
    </button>
</div>

<!-- 点赞按钮 -->
<div x-data="{ liked: false, likeCount: {{prompt.like_count}} }">
    <button @click="
        if (!liked) {
            fetch('/api/prompts/{{prompt.id}}/like', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.message === '点赞成功') {
                        liked = true;
                        likeCount++;
                    }
                });
        }
    " :class="liked ? 'bg-red-500' : 'bg-gray-300'" 
       class="text-white px-3 py-1 rounded">
        👍 <span x-text="likeCount"></span>
    </button>
</div>
```

## **6. 应用启动实现**

### **6.1. 启动逻辑**

```python
@app.on_event("startup")
async def startup():
    """应用启动时初始化"""
    init_database()
    insert_default_data()
    print("应用启动完成")

def insert_default_data():
    """插入默认分类"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        default_categories = [
            ("文生图", "图像生成相关提示词"),
            ("编程辅助", "编程开发相关提示词"),
            ("文本创作", "文本写作相关提示词")
        ]
        
        for name, desc in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description)
                VALUES (?, ?)
            """, (name, desc))
        
        conn.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
```

### **6.2. 错误处理**

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "服务器内部错误",
            "detail": str(exc) if app.debug else None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail
        }
    )
```

## **7. 部署实现**

### **7.1. 环境配置**

```bash
# .env文件
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# 启动命令
uv run uvicorn main:app --port 8080
```

### **7.2. 项目结构**

```
project/
├── main.py              # 主应用文件
├── prompts.db           # SQLite数据库（自动创建）
├── templates/           # Jinja2模板
│   ├── index.html
│   ├── prompt_detail.html
│   └── admin/
│       └── prompts.html
├── static/              # 静态文件
│   ├── css/
│   └── js/
├── requirements.txt     # 依赖列表
└── .env                 # 环境变量
```

通过以上实现逻辑，可以快速构建一个功能完整的极简MVP应用，满足提示词分享的核心需求。