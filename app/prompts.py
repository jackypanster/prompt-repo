"""
提示词管理API端点
提供提示词的CRUD操作，需要管理员认证
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_admin_credentials
from app.crud import (
    create_prompt, get_prompt_by_id, get_prompts, 
    update_prompt, delete_prompt,
    get_category_by_id, get_tag_by_id
)
from app.schemas import (
    PromptCreate, PromptUpdate, PromptRead, PromptList,
    MessageResponse, ErrorResponse
)

router = APIRouter(prefix="/admin/prompts", tags=["提示词管理"])


@router.post("/", 
             response_model=PromptRead,
             status_code=status.HTTP_201_CREATED,
             summary="创建提示词",
             description="创建新的提示词，包含分类和标签关联")
async def create_prompt_endpoint(
    prompt_data: PromptCreate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """创建提示词"""
    try:
        new_prompt = create_prompt(db, prompt_data)
        # 获取完整的提示词信息（包含关联数据）
        full_prompt = get_prompt_by_id(db, new_prompt.id, include_relations=True)
        return full_prompt
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/",
            response_model=PromptList,
            summary="获取提示词列表",
            description="获取提示词列表，支持分页和筛选")
async def get_prompts_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[int] = Query(None, description="分类ID筛选"),
    tag_id: Optional[int] = Query(None, description="标签ID筛选"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    include_relations: bool = Query(True, description="包含分类和标签信息"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取提示词列表"""
    skip = (page - 1) * per_page
    prompts, total = get_prompts(
        db, 
        skip=skip, 
        limit=per_page, 
        category_id=category_id,
        tag_id=tag_id,
        is_featured=is_featured,
        is_active=is_active,
        include_relations=include_relations
    )
    
    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    return PromptList(
        items=prompts,
        total=total,
        page=page,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{prompt_id}",
            response_model=PromptRead,
            summary="获取提示词详情",
            description="根据ID获取提示词详情")
async def get_prompt_endpoint(
    prompt_id: int,
    include_relations: bool = Query(True, description="包含分类和标签信息"),
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """获取提示词详情"""
    prompt = get_prompt_by_id(db, prompt_id, include_relations=include_relations)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"提示词 ID {prompt_id} 不存在"
        )
    return prompt


@router.put("/{prompt_id}",
            response_model=PromptRead,
            summary="更新提示词",
            description="更新提示词信息，只更新提供的字段")
async def update_prompt_endpoint(
    prompt_id: int,
    prompt_data: PromptUpdate,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """更新提示词"""
    try:
        updated_prompt = update_prompt(db, prompt_id, prompt_data)
        if not updated_prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"提示词 ID {prompt_id} 不存在"
            )
        
        # 获取完整的提示词信息（包含关联数据）
        full_prompt = get_prompt_by_id(db, prompt_id, include_relations=True)
        return full_prompt
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{prompt_id}",
               response_model=MessageResponse,
               summary="删除提示词",
               description="删除提示词及其所有关联数据")
async def delete_prompt_endpoint(
    prompt_id: int,
    admin_verified: bool = Depends(verify_admin_credentials),
    db: Session = Depends(get_db)
):
    """删除提示词"""
    success = delete_prompt(db, prompt_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"提示词 ID {prompt_id} 不存在"
        )
    
    return MessageResponse(
        message=f"提示词 ID {prompt_id} 删除成功",
        success=True
    ) 