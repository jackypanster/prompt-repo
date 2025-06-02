"""
数据库CRUD操作函数
提供基础的增删改查操作
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from sqlalchemy.exc import IntegrityError
from app.models import Category, Tag, Prompt, PromptTag, PromptLike
from app.schemas import CategoryCreate, CategoryUpdate, TagCreate, TagUpdate

# 分类CRUD操作
def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """创建分类"""
    try:
        db_category = Category(
            name=category_data.name,
            description=category_data.description,
            is_active=category_data.is_active
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise ValueError(f"分类名称 '{category_data.name}' 已存在")

def get_category_by_id(db: Session, category_id: int, include_count: bool = False) -> Optional[Category]:
    """根据ID获取分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category and include_count:
        # 添加关联的提示词数量
        prompt_count = db.query(func.count(Prompt.id)).filter(
            and_(Prompt.category_id == category_id, Prompt.is_active == True)
        ).scalar()
        category.prompt_count = prompt_count or 0
    return category

def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """根据名称获取分类"""
    return db.query(Category).filter(Category.name == name).first()

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    include_count: bool = False,
    active_only: bool = False
) -> Tuple[List[Category], int]:
    """获取分类列表（支持分页和计数）"""
    query = db.query(Category)
    
    if active_only:
        query = query.filter(Category.is_active == True)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    categories = query.order_by(Category.name).offset(skip).limit(limit).all()
    
    # 如果需要包含提示词数量
    if include_count:
        for category in categories:
            prompt_count = db.query(func.count(Prompt.id)).filter(
                and_(Prompt.category_id == category.id, Prompt.is_active == True)
            ).scalar()
            category.prompt_count = prompt_count or 0
    
    return categories, total

def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    
    try:
        # 只更新提供的字段
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        if category_data.name:
            raise ValueError(f"分类名称 '{category_data.name}' 已存在")
        raise

def delete_category(db: Session, category_id: int, force: bool = False) -> bool:
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return False
    
    # 检查是否有关联的提示词
    if not force:
        prompt_count = db.query(func.count(Prompt.id)).filter(
            Prompt.category_id == category_id
        ).scalar()
        if prompt_count > 0:
            raise ValueError(f"无法删除分类，存在 {prompt_count} 个关联的提示词")
    
    db.delete(category)
    db.commit()
    return True

# 标签CRUD操作
def create_tag(db: Session, tag_data: TagCreate) -> Tag:
    """创建标签"""
    try:
        db_tag = Tag(
            name=tag_data.name,
            color=tag_data.color,
            is_active=tag_data.is_active
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except IntegrityError:
        db.rollback()
        raise ValueError(f"标签名称 '{tag_data.name}' 已存在")

def get_tag_by_id(db: Session, tag_id: int, include_count: bool = False) -> Optional[Tag]:
    """根据ID获取标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag and include_count:
        # 添加使用次数
        usage_count = db.query(func.count(PromptTag.id)).filter(
            and_(PromptTag.tag_id == tag_id, 
                 PromptTag.prompt.has(Prompt.is_active == True))
        ).scalar()
        tag.usage_count = usage_count or 0
    return tag

def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    """根据名称获取标签"""
    return db.query(Tag).filter(Tag.name == name).first()

def get_tags(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    include_count: bool = False,
    active_only: bool = False
) -> Tuple[List[Tag], int]:
    """获取标签列表（支持分页和计数）"""
    query = db.query(Tag)
    
    if active_only:
        query = query.filter(Tag.is_active == True)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    tags = query.order_by(Tag.name).offset(skip).limit(limit).all()
    
    # 如果需要包含使用次数
    if include_count:
        for tag in tags:
            usage_count = db.query(func.count(PromptTag.id)).filter(
                and_(PromptTag.tag_id == tag.id,
                     PromptTag.prompt.has(Prompt.is_active == True))
            ).scalar()
            tag.usage_count = usage_count or 0
    
    return tags, total

def update_tag(db: Session, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
    """更新标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None
    
    try:
        # 只更新提供的字段
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError:
        db.rollback()
        if tag_data.name:
            raise ValueError(f"标签名称 '{tag_data.name}' 已存在")
        raise

def delete_tag(db: Session, tag_id: int, force: bool = False) -> bool:
    """删除标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False
    
    # 检查是否有关联的提示词
    if not force:
        usage_count = db.query(func.count(PromptTag.id)).filter(
            PromptTag.tag_id == tag_id
        ).scalar()
        if usage_count > 0:
            raise ValueError(f"无法删除标签，存在 {usage_count} 个关联的提示词")
    
    db.delete(tag)
    db.commit()
    return True

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