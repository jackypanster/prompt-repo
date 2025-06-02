"""
标签管理API端点
提供标签的CRUD操作，需要管理员认证
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_admin_credentials
from app.crud import (
    create_tag, get_tag_by_id, get_tag_by_name, 
    get_tags, update_tag, delete_tag
)
from app.schemas import (
    TagCreate, TagUpdate, TagRead, TagList,
    MessageResponse, ErrorResponse
)

router = APIRouter(prefix="/admin/tags", tags=["标签管理"])


@router.post("/", 
             response_model=TagRead,
             status_code=status.HTTP_201_CREATED,
             summary="创建标签",
             description="创建新的标签，标签名称必须唯一")
async def create_tag_endpoint(
    tag_data: TagCreate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """创建标签"""
    # 检查标签名是否已存在
    existing_tag = get_tag_by_name(db, tag_data.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"标签名称 '{tag_data.name}' 已存在"
        )
    
    try:
        new_tag = create_tag(db, tag_data)
        # 添加使用次数
        new_tag.usage_count = 0
        return new_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=TagList,
            summary="获取标签列表",
            description="获取标签列表，支持分页和筛选")
async def get_tags_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    active_only: bool = Query(False, description="仅显示激活的标签"),
    include_count: bool = Query(True, description="包含使用次数"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    skip = (page - 1) * per_page
    tags, total = get_tags(
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
    
    return TagList(
        items=tags,
        total=total,
        page=page,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{tag_id}",
            response_model=TagRead,
            summary="获取标签详情",
            description="根据ID获取标签详情")
async def get_tag_endpoint(
    tag_id: int,
    include_count: bool = Query(True, description="包含使用次数"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取标签详情"""
    tag = get_tag_by_id(db, tag_id, include_count=include_count)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标签 ID {tag_id} 不存在"
        )
    return tag


@router.put("/{tag_id}",
            response_model=TagRead,
            summary="更新标签",
            description="更新标签信息，只更新提供的字段")
async def update_tag_endpoint(
    tag_id: int,
    tag_data: TagUpdate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """更新标签"""
    try:
        updated_tag = update_tag(db, tag_id, tag_data)
        if not updated_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"标签 ID {tag_id} 不存在"
            )
        
        # 添加使用次数
        updated_tag = get_tag_by_id(db, tag_id, include_count=True)
        return updated_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{tag_id}",
               response_model=MessageResponse,
               summary="删除标签",
               description="删除标签，如果有关联的提示词则需要force=true")
async def delete_tag_endpoint(
    tag_id: int,
    force: bool = Query(False, description="强制删除（忽略关联的提示词）"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """删除标签"""
    try:
        success = delete_tag(db, tag_id, force=force)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"标签 ID {tag_id} 不存在"
            )
        
        return MessageResponse(
            message=f"标签 ID {tag_id} 删除成功",
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 