"""
数据库模型定义
定义所有表结构和关系
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    """分类表"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    prompts = relationship("Prompt", back_populates="category", cascade="all, delete-orphan")

class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    prompt_tags = relationship("PromptTag", back_populates="tag", cascade="all, delete-orphan")

class Prompt(Base):
    """提示词主表"""
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content_markdown = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    # 统计字段
    like_count = Column(Integer, default=0, index=True)
    copy_count = Column(Integer, default=0, index=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("Category", back_populates="prompts")
    prompt_tags = relationship("PromptTag", back_populates="prompt", cascade="all, delete-orphan")
    likes = relationship("PromptLike", back_populates="prompt", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('ix_prompts_stats', 'like_count', 'copy_count'),
        Index('ix_prompts_created', 'created_at'),
    )

class PromptTag(Base):
    """提示词-标签多对多关联表"""
    __tablename__ = "prompt_tags"
    
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    prompt = relationship("Prompt", back_populates="prompt_tags")
    tag = relationship("Tag", back_populates="prompt_tags")
    
    # 唯一约束：防止重复关联
    __table_args__ = (
        UniqueConstraint('prompt_id', 'tag_id', name='uq_prompt_tag'),
        Index('ix_prompt_tags_prompt', 'prompt_id'),
        Index('ix_prompt_tags_tag', 'tag_id'),
    )

class PromptLike(Base):
    """点赞记录表（防重复点赞）"""
    __tablename__ = "prompt_likes"
    
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    ip_hash = Column(String(64), nullable=False)  # IP地址的哈希值
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    prompt = relationship("Prompt", back_populates="likes")
    
    # 唯一约束：同一IP只能为同一提示词点赞一次
    __table_args__ = (
        UniqueConstraint('prompt_id', 'ip_hash', name='uq_prompt_like'),
        Index('ix_prompt_likes_prompt', 'prompt_id'),
        Index('ix_prompt_likes_ip', 'ip_hash'),
    ) 