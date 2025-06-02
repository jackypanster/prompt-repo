"""
数据库连接管理和配置模块
- SQLite数据库连接
- WAL模式启用
- 会话管理
"""
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

# 数据库文件路径
DATABASE_PATH = Path("prompts.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy 配置
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # SQLite特定配置
        "timeout": 20,  # 连接超时时间
    },
    echo=False,  # 生产环境设为False，开发时可设为True查看SQL
)

# 启用WAL模式的事件监听器
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    SQLite连接时设置PRAGMA
    - 启用WAL模式优化并发读写
    - 设置其他性能优化参数
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        # 启用WAL模式
        cursor.execute("PRAGMA journal_mode=WAL")
        # 设置同步模式为NORMAL（平衡性能和安全性）
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys=ON")
        # 设置缓存大小（KB）
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB
        cursor.close()

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    初始化数据库
    创建所有表
    """
    # 导入所有模型确保表被创建
    import app.models
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 验证WAL模式是否启用
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("PRAGMA journal_mode")).fetchone()
        if result and result[0].upper() == 'WAL':
            print("✅ SQLite WAL模式已启用")
        else:
            print("⚠️  WAL模式启用失败") 