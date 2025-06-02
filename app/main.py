from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import get_db, init_database
from app.crud import check_database_health
from app.auth import verify_admin_credentials, rate_limit, get_rate_limit_status
from app.categories import router as categories_router
from app.tags import router as tags_router
from app.prompts import router as prompts_router
from app.public import router as public_router

# 初始化数据库
init_database()

app = FastAPI(
    title="提示词分享平台 - 极简MVP",
    description="一体化的提示词发布、管理和分享平台",
    version="0.3.0"
)

# 配置模板引擎
templates = Jinja2Templates(directory="templates")

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册管理路由
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(prompts_router)

# 注册公开页面路由（放在最后，让它能处理根路径）
app.include_router(public_router)


# 主页现在由public_router处理


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/db-health")
async def database_health_check(db: Session = Depends(get_db)):
    """数据库健康检查端点"""
    return check_database_health(db)


@app.get("/admin")
async def admin_dashboard(admin_verified: bool = Depends(verify_admin_credentials)):
    """管理员仪表板（需要认证）"""
    return {
        "message": "欢迎访问管理员仪表板",
        "admin_verified": admin_verified,
        "available_endpoints": [
            "/admin/categories",
            "/admin/tags", 
            "/admin/prompts"
        ]
    }


@app.get("/api/test-rate-limit")
@rate_limit(max_requests=3, window_minutes=1)
async def test_rate_limit(request: Request):
    """测试限频功能的端点"""
    limit_status = get_rate_limit_status(request)
    return {
        "message": "限频测试成功",
        "limit_status": limit_status,
        "tip": "尝试快速访问此端点超过3次，会触发429错误"
    } 