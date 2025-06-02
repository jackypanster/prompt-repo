# 提示词分享平台 - 后端 MVP 项目入口点
from app.main import app

# 导出app实例供uvicorn使用
__all__ = ["app"] 