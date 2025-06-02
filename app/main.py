from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db, init_database
from app.crud import check_database_health
from app.auth import verify_admin_credentials, rate_limit, get_rate_limit_status

# 初始化数据库
init_database()

app = FastAPI(
    title="提示词分享平台 - 后端 MVP",
    description="为博主提供提示词发布和管理的后端 API",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"message": "Hello World", "app": "提示词分享平台后端 MVP"}


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