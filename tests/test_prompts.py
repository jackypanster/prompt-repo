"""
提示词管理功能测试
测试提示词CRUD操作的API端点和业务逻辑
"""
import pytest
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 测试用的认证头
def get_auth_headers():
    """获取管理员认证头"""
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    return {"Authorization": f"Basic {credentials}"}

# 测试数据生成函数
def create_test_category():
    """创建测试分类"""
    import time
    timestamp = int(time.time() * 1000000)
    category_data = {
        "name": f"测试分类_{timestamp}",
        "description": "测试用分类",
        "is_active": True
    }
    response = client.post("/admin/categories/", json=category_data, headers=get_auth_headers())
    return response.json()["id"]

def create_test_tags():
    """创建测试标签"""
    import time
    timestamp = int(time.time() * 1000000)
    tags = []
    for i in range(2):
        tag_data = {
            "name": f"测试标签_{timestamp}_{i}",
            "color": f"#ff{i}00{i}",
            "is_active": True
        }
        response = client.post("/admin/tags/", json=tag_data, headers=get_auth_headers())
        tags.append(response.json()["id"])
    return tags

def get_unique_prompt_data():
    """生成唯一的测试提示词数据"""
    import time
    timestamp = int(time.time() * 1000000)
    category_id = create_test_category()
    tag_ids = create_test_tags()
    
    return {
        "title": f"测试提示词_{timestamp}",
        "content": f"这是一个测试提示词内容，时间戳：{timestamp}",
        "description": "这是测试提示词的描述",
        "category_id": category_id,
        "tag_ids": tag_ids,
        "is_featured": True,
        "is_active": True
    }

def get_unique_prompt_update():
    """生成唯一的更新数据"""
    import time
    timestamp = int(time.time() * 1000000)
    return {
        "title": f"更新后的提示词_{timestamp}",
        "content": f"更新后的内容_{timestamp}",
        "description": "更新后的描述",
        "is_featured": False,
        "is_active": False
    }


class TestPromptAuth:
    """测试提示词端点的认证保护"""
    
    def test_create_prompt_without_auth(self):
        """测试未认证创建提示词"""
        response = client.post("/admin/prompts/", json=get_unique_prompt_data())
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Basic"
    
    def test_get_prompts_without_auth(self):
        """测试未认证获取提示词列表"""
        response = client.get("/admin/prompts/")
        assert response.status_code == 401
    
    def test_update_prompt_without_auth(self):
        """测试未认证更新提示词"""
        response = client.put("/admin/prompts/1", json=get_unique_prompt_update())
        assert response.status_code == 401
    
    def test_delete_prompt_without_auth(self):
        """测试未认证删除提示词"""
        response = client.delete("/admin/prompts/1")
        assert response.status_code == 401


class TestPromptCRUD:
    """测试提示词CRUD操作"""
    
    def test_create_prompt_success(self):
        """测试成功创建提示词"""
        test_data = get_unique_prompt_data()
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == test_data["title"]
        assert data["content"] == test_data["content"]
        assert data["description"] == test_data["description"]
        assert data["category_id"] == test_data["category_id"]
        assert data["is_featured"] == test_data["is_featured"]
        assert data["is_active"] == test_data["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # 验证关联数据
        assert data["category"] is not None
        assert len(data["tags"]) == 2
        assert data["like_count"] == 0
        assert data["copy_count"] == 0
    
    def test_create_prompt_invalid_category(self):
        """测试创建提示词时分类不存在"""
        test_data = get_unique_prompt_data()
        test_data["category_id"] = 99999  # 不存在的分类ID
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "分类 ID 99999 不存在" in response.json()["detail"]
    
    def test_create_prompt_invalid_tag(self):
        """测试创建提示词时标签不存在"""
        test_data = get_unique_prompt_data()
        test_data["tag_ids"] = [99999]  # 不存在的标签ID
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "标签 ID 99999 不存在" in response.json()["detail"]
    
    def test_create_prompt_without_tags(self):
        """测试创建不含标签的提示词"""
        test_data = get_unique_prompt_data()
        test_data["tag_ids"] = []  # 空标签列表
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["tags"]) == 0
    
    def test_get_prompts_list(self):
        """测试获取提示词列表"""
        # 先创建几个提示词
        for i in range(3):
            test_data = get_unique_prompt_data()
            client.post("/admin/prompts/", json=test_data, headers=get_auth_headers())
        
        # 获取提示词列表
        response = client.get("/admin/prompts/", headers=get_auth_headers())
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data
        assert len(data["items"]) >= 3
        
        # 验证每个提示词包含关联数据
        for prompt in data["items"]:
            assert "category" in prompt
            assert "tags" in prompt
    
    def test_get_prompts_with_pagination(self):
        """测试分页获取提示词列表"""
        response = client.get(
            "/admin/prompts/?page=1&per_page=2", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["items"]) <= 2
    
    def test_get_prompts_with_filters(self):
        """测试筛选获取提示词列表"""
        # 创建测试数据
        test_data = get_unique_prompt_data()
        create_response = client.post("/admin/prompts/", json=test_data, headers=get_auth_headers())
        category_id = test_data["category_id"]
        tag_id = test_data["tag_ids"][0]
        
        # 按分类筛选
        response = client.get(
            f"/admin/prompts/?category_id={category_id}", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        for prompt in data["items"]:
            assert prompt["category_id"] == category_id
        
        # 按标签筛选
        response = client.get(
            f"/admin/prompts/?tag_id={tag_id}", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        data = response.json()
        # 验证返回的提示词包含该标签
        assert data["total"] >= 1
    
    def test_get_prompt_by_id(self):
        """测试根据ID获取提示词"""
        test_data = get_unique_prompt_data()
        # 先创建一个提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 获取提示词详情
        response = client.get(
            f"/admin/prompts/{prompt_id}", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == prompt_id
        assert data["title"] == test_data["title"]
        assert "category" in data
        assert "tags" in data
        assert len(data["tags"]) == 2
    
    def test_get_prompt_not_found(self):
        """测试获取不存在的提示词"""
        response = client.get(
            "/admin/prompts/99999", 
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_update_prompt_success(self):
        """测试成功更新提示词"""
        test_data = get_unique_prompt_data()
        update_data = get_unique_prompt_update()
        
        # 先创建一个提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 更新提示词
        response = client.put(
            f"/admin/prompts/{prompt_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["description"] == update_data["description"]
        assert data["is_featured"] == update_data["is_featured"]
        assert data["is_active"] == update_data["is_active"]
    
    def test_update_prompt_tags(self):
        """测试更新提示词的标签关联"""
        test_data = get_unique_prompt_data()
        
        # 先创建一个提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 创建新的标签
        new_tag_ids = create_test_tags()
        
        # 更新标签关联
        update_data = {"tag_ids": new_tag_ids}
        response = client.put(
            f"/admin/prompts/{prompt_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tags"]) == 2
        # 验证新标签ID
        returned_tag_ids = [tag["id"] for tag in data["tags"]]
        assert set(returned_tag_ids) == set(new_tag_ids)
    
    def test_update_prompt_partial(self):
        """测试部分更新提示词"""
        test_data = get_unique_prompt_data()
        
        # 先创建一个提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 只更新标题
        partial_update = {"title": "仅更新标题"}
        response = client.put(
            f"/admin/prompts/{prompt_id}",
            json=partial_update,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == partial_update["title"]
        # 其他字段保持不变
        assert data["content"] == test_data["content"]
        assert data["description"] == test_data["description"]
    
    def test_update_prompt_not_found(self):
        """测试更新不存在的提示词"""
        response = client.put(
            "/admin/prompts/99999",
            json=get_unique_prompt_update(),
            headers=get_auth_headers()
        )
        assert response.status_code == 404
    
    def test_delete_prompt_success(self):
        """测试成功删除提示词"""
        test_data = get_unique_prompt_data()
        
        # 先创建一个提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 删除提示词
        response = client.delete(
            f"/admin/prompts/{prompt_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
        
        # 验证提示词已被删除
        get_response = client.get(
            f"/admin/prompts/{prompt_id}",
            headers=get_auth_headers()
        )
        assert get_response.status_code == 404
    
    def test_delete_prompt_not_found(self):
        """测试删除不存在的提示词"""
        response = client.delete(
            "/admin/prompts/99999",
            headers=get_auth_headers()
        )
        assert response.status_code == 404


class TestPromptValidation:
    """测试提示词数据验证"""
    
    def test_prompt_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_data = {
            "content": "只有内容，缺少标题",
            "category_id": create_test_category()
        }
        response = client.post(
            "/admin/prompts/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_prompt_title_too_long(self):
        """测试标题过长"""
        test_data = get_unique_prompt_data()
        test_data["title"] = "x" * 101  # 超过100字符限制
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_prompt_content_too_long(self):
        """测试内容过长"""
        test_data = get_unique_prompt_data()
        test_data["content"] = "x" * 5001  # 超过5000字符限制
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422


class TestPromptRelations:
    """测试提示词关联关系"""
    
    def test_create_prompt_with_multiple_tags(self):
        """测试创建包含多个标签的提示词"""
        test_data = get_unique_prompt_data()
        # 确保有多个标签
        additional_tags = create_test_tags()
        test_data["tag_ids"].extend(additional_tags)
        
        response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["tags"]) == len(test_data["tag_ids"])
    
    def test_update_prompt_clear_tags(self):
        """测试清空提示词的标签关联"""
        test_data = get_unique_prompt_data()
        
        # 先创建一个有标签的提示词
        create_response = client.post(
            "/admin/prompts/", 
            json=test_data,
            headers=get_auth_headers()
        )
        prompt_id = create_response.json()["id"]
        
        # 清空标签
        update_data = {"tag_ids": []}
        response = client.put(
            f"/admin/prompts/{prompt_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tags"]) == 0 