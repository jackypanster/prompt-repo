"""
数据库功能测试
测试SQLite连接、WAL模式、表创建和基础CRUD操作
"""
import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, set_sqlite_pragma
from app.models import Category, Tag, Prompt, PromptTag, PromptLike
from app.crud import (
    create_category, get_category_by_name, get_categories,
    create_tag, get_tag_by_name, get_tags,
    create_prompt, get_prompt_by_id, get_prompts,
    check_database_health
)

@pytest.fixture
def test_db():
    """创建测试数据库"""
    # 使用临时文件
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # 创建测试数据库引擎
    engine = create_engine(
        f"sqlite:///{temp_db.name}",
        connect_args={"check_same_thread": False}
    )
    
    # 应用PRAGMA设置
    from sqlalchemy import event
    event.listen(engine, "connect", set_sqlite_pragma)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # 清理
    session.close()
    os.unlink(temp_db.name)

def test_wal_mode_enabled(test_db):
    """测试WAL模式是否启用"""
    result = test_db.execute(text("PRAGMA journal_mode")).fetchone()
    assert result[0].upper() == 'WAL'

def test_foreign_keys_enabled(test_db):
    """测试外键约束是否启用"""
    result = test_db.execute(text("PRAGMA foreign_keys")).fetchone()
    assert result[0] == 1

def test_create_category(test_db):
    """测试创建分类"""
    category = create_category(test_db, "测试分类", "这是一个测试分类")
    
    assert category.id is not None
    assert category.name == "测试分类"
    assert category.description == "这是一个测试分类"
    assert category.created_at is not None

def test_get_category_by_name(test_db):
    """测试根据名称获取分类"""
    # 创建分类
    create_category(test_db, "AI工具", "AI相关的提示词")
    
    # 获取分类
    category = get_category_by_name(test_db, "AI工具")
    assert category is not None
    assert category.name == "AI工具"
    
    # 测试不存在的分类
    not_found = get_category_by_name(test_db, "不存在的分类")
    assert not_found is None

def test_create_tag(test_db):
    """测试创建标签"""
    tag = create_tag(test_db, "Python")
    
    assert tag.id is not None
    assert tag.name == "Python"
    assert tag.created_at is not None

def test_create_prompt(test_db):
    """测试创建提示词"""
    # 先创建分类
    category = create_category(test_db, "编程", "编程相关")
    
    # 创建提示词
    prompt = create_prompt(
        test_db,
        title="Python代码优化",
        content_markdown="# 如何优化Python代码\n\n请优化以下代码...",
        category_id=category.id
    )
    
    assert prompt.id is not None
    assert prompt.title == "Python代码优化"
    assert prompt.category_id == category.id
    assert prompt.like_count == 0
    assert prompt.copy_count == 0

def test_foreign_key_constraint(test_db):
    """测试外键约束"""
    # 尝试创建引用不存在分类的提示词
    prompt = Prompt(
        title="测试提示词",
        content_markdown="测试内容",
        category_id=9999  # 不存在的分类ID
    )
    test_db.add(prompt)
    
    # 应该抛出外键约束错误
    with pytest.raises(Exception):
        test_db.commit()

def test_unique_constraints(test_db):
    """测试唯一约束"""
    # 测试分类名唯一性
    create_category(test_db, "唯一分类", "测试")
    
    with pytest.raises(Exception):
        create_category(test_db, "唯一分类", "重复名称")

def test_database_health_check(test_db):
    """测试数据库健康检查"""
    health = check_database_health(test_db)
    
    assert health["status"] == "healthy"
    assert health["connection"] == "ok"
    assert health["wal_mode"] == "wal"
    assert health["foreign_keys"] == "enabled"
    assert isinstance(health["tables"], dict)
    assert "categories" in health["tables"]
    assert "tags" in health["tables"]
    assert "prompts" in health["tables"]

def test_tables_created(test_db):
    """测试所有表是否正确创建"""
    tables = [
        "categories", "tags", "prompts", 
        "prompt_tags", "prompt_likes"
    ]
    
    for table in tables:
        result = test_db.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        ).fetchone()
        assert result is not None, f"表 {table} 未创建"

def test_indexes_created(test_db):
    """测试索引是否正确创建"""
    # 检查一些关键索引
    indexes_to_check = [
        "ix_categories_name",
        "ix_tags_name", 
        "ix_prompts_title",
        "ix_prompts_like_count",
        "ix_prompts_created_at"
    ]
    
    for index_name in indexes_to_check:
        result = test_db.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
        ).fetchone()
        assert result is not None, f"索引 {index_name} 未创建" 