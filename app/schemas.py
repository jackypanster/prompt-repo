"""
Pydantic模型定义
用于API输入输出数据验证和序列化
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# 基础模型
class TimestampMixin(BaseModel):
    """时间戳混入类"""
    created_at: datetime
    updated_at: datetime


# 分类相关模型
class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")
    is_active: bool = Field(True, description="是否激活")


class CategoryCreate(CategoryBase):
    """创建分类的输入模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类的输入模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=200, description="分类描述") 
    is_active: Optional[bool] = Field(None, description="是否激活")


class CategoryRead(CategoryBase, TimestampMixin):
    """分类输出模型"""
    id: int = Field(..., description="分类ID")
    prompt_count: Optional[int] = Field(0, description="关联的提示词数量")
    
    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    """分类列表响应模型"""
    items: List[CategoryRead]
    total: int = Field(..., description="总数量")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")


# 标签相关模型（为后续任务预留）
class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=30, description="标签名称")
    color: Optional[str] = Field("#3b82f6", max_length=7, description="标签颜色（十六进制）")
    is_active: bool = Field(True, description="是否激活")


class TagCreate(TagBase):
    """创建标签的输入模型"""
    pass


class TagUpdate(BaseModel):
    """更新标签的输入模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=30, description="标签名称")
    color: Optional[str] = Field(None, max_length=7, description="标签颜色（十六进制）")
    is_active: Optional[bool] = Field(None, description="是否激活")


class TagRead(TagBase, TimestampMixin):
    """标签输出模型"""
    id: int = Field(..., description="标签ID")
    usage_count: Optional[int] = Field(0, description="使用次数")
    
    model_config = ConfigDict(from_attributes=True)


class TagList(BaseModel):
    """标签列表响应模型"""
    items: List[TagRead]
    total: int = Field(..., description="总数量")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")


# 提示词相关模型（为后续任务预留）
class PromptBase(BaseModel):
    """提示词基础模型"""
    title: str = Field(..., min_length=1, max_length=100, description="提示词标题")
    content: str = Field(..., min_length=1, max_length=5000, description="提示词内容")
    description: Optional[str] = Field(None, max_length=300, description="提示词描述")
    category_id: int = Field(..., description="分类ID")
    tag_ids: List[int] = Field(default=[], description="标签ID列表")
    is_featured: bool = Field(False, description="是否精选")
    is_active: bool = Field(True, description="是否激活")


class PromptCreate(PromptBase):
    """创建提示词的输入模型"""
    pass


class PromptUpdate(BaseModel):
    """更新提示词的输入模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="提示词标题")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="提示词内容")
    description: Optional[str] = Field(None, max_length=300, description="提示词描述")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")
    is_featured: Optional[bool] = Field(None, description="是否精选")
    is_active: Optional[bool] = Field(None, description="是否激活")


class PromptRead(PromptBase, TimestampMixin):
    """提示词输出模型"""
    id: int = Field(..., description="提示词ID")
    category: Optional[CategoryRead] = Field(None, description="分类信息")
    tags: List[TagRead] = Field(default=[], description="标签列表")
    like_count: int = Field(0, description="点赞数")
    copy_count: int = Field(0, description="复制数")
    
    model_config = ConfigDict(from_attributes=True)


# 通用响应模型
class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(True, description="操作是否成功")
    data: Optional[dict] = Field(None, description="附加数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间") 