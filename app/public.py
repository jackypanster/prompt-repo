"""
公开页面路由
提供提示词浏览和展示功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import (
    get_prompts, get_prompts_by_category_name, get_prompts_by_tag_name,
    get_categories, get_tags
)

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["公开页面"])

def get_pagination_info(page: int, per_page: int, total: int) -> dict:
    """计算分页信息"""
    total_pages = (total + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    # 计算页码范围（显示当前页前后2页）
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    page_range = list(range(start_page, end_page + 1))
    
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "page_range": page_range,
        "start_page": start_page,
        "end_page": end_page
    }

@router.get("/")
async def homepage(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=50, description="每页数量"),
    sort: str = Query("created_at", description="排序方式"),
    category: Optional[str] = Query(None, description="分类筛选"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    db: Session = Depends(get_db)
):
    """主页 - 提示词列表"""
    skip = (page - 1) * per_page
    
    # 获取筛选参数
    category_id = None
    tag_id = None
    
    if category:
        from app.crud import get_category_by_name
        cat = get_category_by_name(db, category)
        if cat:
            category_id = cat.id
    
    if tag:
        from app.crud import get_tag_by_name
        tag_obj = get_tag_by_name(db, tag)
        if tag_obj:
            tag_id = tag_obj.id
    
    # 获取提示词列表
    prompts, total = get_prompts(
        db=db,
        skip=skip,
        limit=per_page,
        category_id=category_id,
        tag_id=tag_id,
        is_active=True,
        include_relations=True,
        order_by=sort
    )
    
    # 获取分类和标签列表用于筛选菜单
    categories, _ = get_categories(db, active_only=True, include_count=True)
    tags, _ = get_tags(db, active_only=True, include_count=True)
    
    # 计算分页信息
    pagination = get_pagination_info(page, per_page, total)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "提示词分享平台",
            "description": "发现和分享优质的AI提示词",
            "prompts": prompts,
            "categories": categories,
            "tags": tags,
            "pagination": pagination,
            "current_sort": sort,
            "current_category": category,
            "current_tag": tag,
            "sort_options": [
                {"value": "created_at", "label": "最新"},
                {"value": "hot", "label": "最热门"},
                {"value": "like_count", "label": "最多点赞"},
                {"value": "copy_count", "label": "最多复制"}
            ]
        }
    )

@router.get("/category/{category_name}")
async def category_page(
    category_name: str,
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=50, description="每页数量"),
    sort: str = Query("created_at", description="排序方式"),
    db: Session = Depends(get_db)
):
    """分类筛选页面"""
    skip = (page - 1) * per_page
    
    # 获取该分类下的提示词
    prompts, total, category = get_prompts_by_category_name(
        db=db,
        category_name=category_name,
        skip=skip,
        limit=per_page,
        order_by=sort
    )
    
    if not category:
        raise HTTPException(status_code=404, detail=f"分类 '{category_name}' 不存在")
    
    # 获取所有分类和标签用于导航
    categories, _ = get_categories(db, active_only=True, include_count=True)
    tags, _ = get_tags(db, active_only=True, include_count=True)
    
    # 计算分页信息
    pagination = get_pagination_info(page, per_page, total)
    
    return templates.TemplateResponse(
        request=request,
        name="category.html",
        context={
            "title": f"分类：{category.name}",
            "description": category.description or f"浏览 {category.name} 分类的所有提示词",
            "category": category,
            "prompts": prompts,
            "categories": categories,
            "tags": tags,
            "pagination": pagination,
            "current_sort": sort,
            "sort_options": [
                {"value": "created_at", "label": "最新"},
                {"value": "hot", "label": "最热门"},
                {"value": "like_count", "label": "最多点赞"},
                {"value": "copy_count", "label": "最多复制"}
            ]
        }
    )

@router.get("/tag/{tag_name}")
async def tag_page(
    tag_name: str,
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=50, description="每页数量"),
    sort: str = Query("created_at", description="排序方式"),
    db: Session = Depends(get_db)
):
    """标签筛选页面"""
    skip = (page - 1) * per_page
    
    # 获取该标签下的提示词
    prompts, total, tag = get_prompts_by_tag_name(
        db=db,
        tag_name=tag_name,
        skip=skip,
        limit=per_page,
        order_by=sort
    )
    
    if not tag:
        raise HTTPException(status_code=404, detail=f"标签 '{tag_name}' 不存在")
    
    # 获取所有分类和标签用于导航
    categories, _ = get_categories(db, active_only=True, include_count=True)
    tags, _ = get_tags(db, active_only=True, include_count=True)
    
    # 计算分页信息
    pagination = get_pagination_info(page, per_page, total)
    
    return templates.TemplateResponse(
        request=request,
        name="tag.html",
        context={
            "title": f"标签：{tag.name}",
            "description": f"浏览带有 {tag.name} 标签的所有提示词",
            "tag": tag,
            "prompts": prompts,
            "categories": categories,
            "tags": tags,
            "pagination": pagination,
            "current_sort": sort,
            "sort_options": [
                {"value": "created_at", "label": "最新"},
                {"value": "hot", "label": "最热门"},
                {"value": "like_count", "label": "最多点赞"},
                {"value": "copy_count", "label": "最多复制"}
            ]
        }
    ) 