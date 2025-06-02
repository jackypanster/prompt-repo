from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import get_db, init_database
from app.crud import check_database_health
from app.auth import verify_admin_credentials, rate_limit, get_rate_limit_status

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


@app.get("/")
async def homepage(request: Request):
    """主页 - 提示词列表页面"""
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "title": "提示词分享平台",
            "description": "发现和分享优质的AI提示词"
        }
    )


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