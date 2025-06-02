"""
数据库CRUD操作函数
提供基础的增删改查操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Category, Tag, Prompt, PromptTag, PromptLike

# 分类CRUD操作
def create_category(db: Session, name: str, description: str = None) -> Category:
    """创建分类"""
    db_category = Category(name=name, description=description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    """根据ID获取分类"""
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """根据名称获取分类"""
    return db.query(Category).filter(Category.name == name).first()

def get_categories(db: Session) -> List[Category]:
    """获取所有分类"""
    return db.query(Category).order_by(Category.name).all()

# 标签CRUD操作
def create_tag(db: Session, name: str) -> Tag:
    """创建标签"""
    db_tag = Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
    """根据ID获取标签"""
    return db.query(Tag).filter(Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    """根据名称获取标签"""
    return db.query(Tag).filter(Tag.name == name).first()

def get_tags(db: Session) -> List[Tag]:
    """获取所有标签"""
    return db.query(Tag).order_by(Tag.name).all()

# 提示词CRUD操作
def create_prompt(
    db: Session, 
    title: str, 
    content_markdown: str, 
    category_id: Optional[int] = None
) -> Prompt:
    """创建提示词"""
    db_prompt = Prompt(
        title=title,
        content_markdown=content_markdown,
        category_id=category_id
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def get_prompt_by_id(db: Session, prompt_id: int) -> Optional[Prompt]:
    """根据ID获取提示词"""
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

def get_prompts(db: Session, skip: int = 0, limit: int = 100) -> List[Prompt]:
    """获取提示词列表"""
    return db.query(Prompt).offset(skip).limit(limit).all()

# 数据库健康检查
def check_database_health(db: Session) -> dict:
    """检查数据库健康状态"""
    try:
        # 测试基本查询
        result = db.execute(text("SELECT 1")).fetchone()
        
        # 检查WAL模式
        wal_result = db.execute(text("PRAGMA journal_mode")).fetchone()
        
        # 检查外键约束
        fk_result = db.execute(text("PRAGMA foreign_keys")).fetchone()
        
        # 获取表统计信息
        tables_info = {}
        for table_name in ['categories', 'tags', 'prompts', 'prompt_tags', 'prompt_likes']:
            count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
            tables_info[table_name] = count_result[0] if count_result else 0
        
        return {
            "status": "healthy",
            "connection": "ok" if result else "failed",
            "wal_mode": wal_result[0] if wal_result else "unknown",
            "foreign_keys": "enabled" if fk_result and fk_result[0] else "disabled",
            "tables": tables_info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 