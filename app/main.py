from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, init_database
from app.crud import check_database_health

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