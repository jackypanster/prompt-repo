"""
分类管理功能测试
测试分类CRUD操作的API端点和业务逻辑
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
def get_unique_category_data():
    """生成唯一的测试分类数据"""
    import time
    timestamp = int(time.time() * 1000000)  # 微秒级时间戳
    return {
        "name": f"测试分类_{timestamp}",
        "description": "这是一个测试分类",
        "is_active": True
    }

def get_unique_category_update():
    """生成唯一的更新数据"""
    import time
    timestamp = int(time.time() * 1000000)
    return {
        "name": f"更新后的分类名_{timestamp}",
        "description": "更新后的描述",
        "is_active": False
    }


class TestCategoryAuth:
    """测试分类端点的认证保护"""
    
    def test_create_category_without_auth(self):
        """测试未认证创建分类"""
        response = client.post("/admin/categories/", json=get_unique_category_data())
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Basic"
    
    def test_get_categories_without_auth(self):
        """测试未认证获取分类列表"""
        response = client.get("/admin/categories/")
        assert response.status_code == 401
    
    def test_update_category_without_auth(self):
        """测试未认证更新分类"""
        response = client.put("/admin/categories/1", json=get_unique_category_update())
        assert response.status_code == 401
    
    def test_delete_category_without_auth(self):
        """测试未认证删除分类"""
        response = client.delete("/admin/categories/1")
        assert response.status_code == 401


class TestCategoryCRUD:
    """测试分类CRUD操作"""
    
    def test_create_category_success(self):
        """测试成功创建分类"""
        test_data = get_unique_category_data()
        response = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == test_data["name"]
        assert data["description"] == test_data["description"]
        assert data["is_active"] == test_data["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["prompt_count"] == 0
    
    def test_create_category_duplicate_name(self):
        """测试创建重复名称的分类"""
        test_data = get_unique_category_data()
        # 先创建一个分类
        response1 = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response1.status_code == 201
        
        # 尝试创建同名分类
        response2 = client.post(
            "/admin/categories/", 
            json=test_data,  # 使用相同的数据
            headers=get_auth_headers()
        )
        assert response2.status_code == 400
        assert "已存在" in response2.json()["detail"]
    
    def test_create_category_invalid_data(self):
        """测试使用无效数据创建分类"""
        invalid_data = {
            "name": "",  # 空名称
            "description": "x" * 300,  # 描述过长
            "is_active": True
        }
        response = client.post(
            "/admin/categories/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_get_categories_list(self):
        """测试获取分类列表"""
        # 先创建几个分类
        for i in range(3):
            category_data = {
                "name": f"分类{i+1}",
                "description": f"描述{i+1}",
                "is_active": True
            }
            client.post(
                "/admin/categories/", 
                json=category_data,
                headers=get_auth_headers()
            )
        
        # 获取分类列表
        response = client.get("/admin/categories/", headers=get_auth_headers())
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data
        assert len(data["items"]) >= 3
    
    def test_get_categories_with_pagination(self):
        """测试分页获取分类列表"""
        response = client.get(
            "/admin/categories/?page=1&per_page=2", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["items"]) <= 2
    
    def test_get_category_by_id(self):
        """测试根据ID获取分类"""
        test_data = get_unique_category_data()
        # 先创建一个分类
        create_response = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        category_id = create_response.json()["id"]
        
        # 获取分类详情
        response = client.get(
            f"/admin/categories/{category_id}", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == test_data["name"]
        assert "prompt_count" in data
    
    def test_get_category_not_found(self):
        """测试获取不存在的分类"""
        response = client.get(
            "/admin/categories/99999", 
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_update_category_success(self):
        """测试成功更新分类"""
        test_data = get_unique_category_data()
        update_data = get_unique_category_update()
        # 先创建一个分类
        create_response = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        category_id = create_response.json()["id"]
        
        # 更新分类
        response = client.put(
            f"/admin/categories/{category_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_active"] == update_data["is_active"]
    
    def test_update_category_partial(self):
        """测试部分更新分类"""
        test_data = get_unique_category_data()
        # 先创建一个分类
        create_response = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        category_id = create_response.json()["id"]
        
        # 只更新名称
        import time
        timestamp = int(time.time() * 1000000)
        partial_update = {"name": f"部分更新的名称_{timestamp}"}
        response = client.put(
            f"/admin/categories/{category_id}",
            json=partial_update,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == partial_update["name"]
        # 其他字段保持不变
        assert data["description"] == test_data["description"]
    
    def test_update_category_not_found(self):
        """测试更新不存在的分类"""
        response = client.put(
            "/admin/categories/99999",
            json=get_unique_category_update(),
            headers=get_auth_headers()
        )
        assert response.status_code == 404
    
    def test_delete_category_success(self):
        """测试成功删除分类"""
        test_data = get_unique_category_data()
        # 先创建一个分类
        create_response = client.post(
            "/admin/categories/", 
            json=test_data,
            headers=get_auth_headers()
        )
        category_id = create_response.json()["id"]
        
        # 删除分类
        response = client.delete(
            f"/admin/categories/{category_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
        
        # 验证分类已被删除
        get_response = client.get(
            f"/admin/categories/{category_id}",
            headers=get_auth_headers()
        )
        assert get_response.status_code == 404
    
    def test_delete_category_not_found(self):
        """测试删除不存在的分类"""
        response = client.delete(
            "/admin/categories/99999",
            headers=get_auth_headers()
        )
        assert response.status_code == 404


class TestCategoryValidation:
    """测试分类数据验证"""
    
    def test_category_name_too_long(self):
        """测试分类名过长"""
        invalid_data = {
            "name": "x" * 100,  # 超过50字符限制
            "description": "正常描述",
            "is_active": True
        }
        response = client.post(
            "/admin/categories/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_category_description_too_long(self):
        """测试分类描述过长"""
        invalid_data = {
            "name": "正常名称",
            "description": "x" * 300,  # 超过200字符限制
            "is_active": True
        }
        response = client.post(
            "/admin/categories/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_category_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_data = {
            "description": "只有描述",
            "is_active": True
            # 缺少name字段
        }
        response = client.post(
            "/admin/categories/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422


class TestCategoryFiltering:
    """测试分类筛选功能"""
    
    def test_filter_active_categories(self):
        """测试筛选激活的分类"""
        # 创建激活和非激活的分类
        active_category = {
            "name": "激活分类",
            "description": "激活的分类",
            "is_active": True
        }
        inactive_category = {
            "name": "非激活分类", 
            "description": "非激活的分类",
            "is_active": False
        }
        
        client.post("/admin/categories/", json=active_category, headers=get_auth_headers())
        client.post("/admin/categories/", json=inactive_category, headers=get_auth_headers())
        
        # 只获取激活的分类
        response = client.get(
            "/admin/categories/?active_only=true", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        # 验证返回的分类都是激活状态
        for category in data["items"]:
            assert category["is_active"] is True 