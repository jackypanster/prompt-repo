"""
分类管理API端点
提供分类的CRUD操作，需要管理员认证
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_admin_credentials
from app.crud import (
    create_category, get_category_by_id, get_category_by_name, 
    get_categories, update_category, delete_category
)
from app.schemas import (
    CategoryCreate, CategoryUpdate, CategoryRead, CategoryList,
    MessageResponse, ErrorResponse
)

router = APIRouter(prefix="/admin/categories", tags=["分类管理"])


@router.post("/", 
             response_model=CategoryRead,
             status_code=status.HTTP_201_CREATED,
             summary="创建分类",
             description="创建新的分类，分类名称必须唯一")
async def create_category_endpoint(
    category_data: CategoryCreate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """创建分类"""
    # 检查分类名是否已存在
    existing_category = get_category_by_name(db, category_data.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分类名称 '{category_data.name}' 已存在"
        )
    
    try:
        new_category = create_category(db, category_data)
        # 添加提示词数量
        new_category.prompt_count = 0
        return new_category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=CategoryList,
            summary="获取分类列表",
            description="获取分类列表，支持分页和筛选")
async def get_categories_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    active_only: bool = Query(False, description="仅显示激活的分类"),
    include_count: bool = Query(True, description="包含提示词数量"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    skip = (page - 1) * per_page
    categories, total = get_categories(
        db, 
        skip=skip, 
        limit=per_page, 
        include_count=include_count,
        active_only=active_only
    )
    
    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    return CategoryList(
        items=categories,
        total=total,
        page=page,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{category_id}",
            response_model=CategoryRead,
            summary="获取分类详情",
            description="根据ID获取分类详情")
async def get_category_endpoint(
    category_id: int,
    include_count: bool = Query(True, description="包含提示词数量"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取分类详情"""
    category = get_category_by_id(db, category_id, include_count=include_count)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 ID {category_id} 不存在"
        )
    return category


@router.put("/{category_id}",
            response_model=CategoryRead,
            summary="更新分类",
            description="更新分类信息，只更新提供的字段")
async def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """更新分类"""
    try:
        updated_category = update_category(db, category_id, category_data)
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"分类 ID {category_id} 不存在"
            )
        
        # 添加提示词数量
        updated_category = get_category_by_id(db, category_id, include_count=True)
        return updated_category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}",
               response_model=MessageResponse,
               summary="删除分类",
               description="删除分类，如果有关联的提示词则需要force=true")
async def delete_category_endpoint(
    category_id: int,
    force: bool = Query(False, description="强制删除（忽略关联的提示词）"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """删除分类"""
    try:
        success = delete_category(db, category_id, force=force)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"分类 ID {category_id} 不存在"
            )
        
        return MessageResponse(
            message=f"分类 ID {category_id} 删除成功",
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 