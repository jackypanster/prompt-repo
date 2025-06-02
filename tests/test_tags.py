"""
标签管理功能测试
测试标签CRUD操作的API端点和业务逻辑
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
def get_unique_tag_data():
    """生成唯一的测试标签数据"""
    import time
    timestamp = int(time.time() * 1000000)  # 微秒级时间戳
    return {
        "name": f"测试标签_{timestamp}",
        "color": "#ff5722",
        "is_active": True
    }

def get_unique_tag_update():
    """生成唯一的更新数据"""
    import time
    timestamp = int(time.time() * 1000000)
    return {
        "name": f"更新后的标签名_{timestamp}",
        "color": "#4caf50",
        "is_active": False
    }


class TestTagAuth:
    """测试标签端点的认证保护"""
    
    def test_create_tag_without_auth(self):
        """测试未认证创建标签"""
        response = client.post("/admin/tags/", json=get_unique_tag_data())
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Basic"
    
    def test_get_tags_without_auth(self):
        """测试未认证获取标签列表"""
        response = client.get("/admin/tags/")
        assert response.status_code == 401
    
    def test_update_tag_without_auth(self):
        """测试未认证更新标签"""
        response = client.put("/admin/tags/1", json=get_unique_tag_update())
        assert response.status_code == 401
    
    def test_delete_tag_without_auth(self):
        """测试未认证删除标签"""
        response = client.delete("/admin/tags/1")
        assert response.status_code == 401


class TestTagCRUD:
    """测试标签CRUD操作"""
    
    def test_create_tag_success(self):
        """测试成功创建标签"""
        test_data = get_unique_tag_data()
        response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == test_data["name"]
        assert data["color"] == test_data["color"]
        assert data["is_active"] == test_data["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["usage_count"] == 0
    
    def test_create_tag_duplicate_name(self):
        """测试创建重复名称的标签"""
        test_data = get_unique_tag_data()
        # 先创建一个标签
        response1 = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response1.status_code == 201
        
        # 尝试创建同名标签
        response2 = client.post(
            "/admin/tags/", 
            json=test_data,  # 使用相同的数据
            headers=get_auth_headers()
        )
        assert response2.status_code == 400
        assert "已存在" in response2.json()["detail"]
    
    def test_create_tag_invalid_data(self):
        """测试使用无效数据创建标签"""
        invalid_data = {
            "name": "",  # 空名称
            "color": "invalid_color",  # 无效颜色
            "is_active": True
        }
        response = client.post(
            "/admin/tags/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_get_tags_list(self):
        """测试获取标签列表"""
        # 先创建几个标签
        for i in range(3):
            tag_data = {
                "name": f"标签{i+1}",
                "color": f"#ff{i+1}00{i+1}",
                "is_active": True
            }
            client.post(
                "/admin/tags/", 
                json=tag_data,
                headers=get_auth_headers()
            )
        
        # 获取标签列表
        response = client.get("/admin/tags/", headers=get_auth_headers())
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data
        assert len(data["items"]) >= 3
    
    def test_get_tags_with_pagination(self):
        """测试分页获取标签列表"""
        response = client.get(
            "/admin/tags/?page=1&per_page=2", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["items"]) <= 2
    
    def test_get_tag_by_id(self):
        """测试根据ID获取标签"""
        test_data = get_unique_tag_data()
        # 先创建一个标签
        create_response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        tag_id = create_response.json()["id"]
        
        # 获取标签详情
        response = client.get(
            f"/admin/tags/{tag_id}", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == tag_id
        assert data["name"] == test_data["name"]
        assert "usage_count" in data
    
    def test_get_tag_not_found(self):
        """测试获取不存在的标签"""
        response = client.get(
            "/admin/tags/99999", 
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_update_tag_success(self):
        """测试成功更新标签"""
        test_data = get_unique_tag_data()
        update_data = get_unique_tag_update()
        # 先创建一个标签
        create_response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        tag_id = create_response.json()["id"]
        
        # 更新标签
        response = client.put(
            f"/admin/tags/{tag_id}",
            json=update_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["color"] == update_data["color"]
        assert data["is_active"] == update_data["is_active"]
    
    def test_update_tag_partial(self):
        """测试部分更新标签"""
        test_data = get_unique_tag_data()
        # 先创建一个标签
        create_response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        tag_id = create_response.json()["id"]
        
        # 只更新颜色
        partial_update = {"color": "#9c27b0"}
        response = client.put(
            f"/admin/tags/{tag_id}",
            json=partial_update,
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["color"] == partial_update["color"]
        # 其他字段保持不变
        assert data["name"] == test_data["name"]
    
    def test_update_tag_not_found(self):
        """测试更新不存在的标签"""
        response = client.put(
            "/admin/tags/99999",
            json=get_unique_tag_update(),
            headers=get_auth_headers()
        )
        assert response.status_code == 404
    
    def test_delete_tag_success(self):
        """测试成功删除标签"""
        test_data = get_unique_tag_data()
        # 先创建一个标签
        create_response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        tag_id = create_response.json()["id"]
        
        # 删除标签
        response = client.delete(
            f"/admin/tags/{tag_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
        
        # 验证标签已被删除
        get_response = client.get(
            f"/admin/tags/{tag_id}",
            headers=get_auth_headers()
        )
        assert get_response.status_code == 404
    
    def test_delete_tag_not_found(self):
        """测试删除不存在的标签"""
        response = client.delete(
            "/admin/tags/99999",
            headers=get_auth_headers()
        )
        assert response.status_code == 404


class TestTagValidation:
    """测试标签数据验证"""
    
    def test_tag_name_too_long(self):
        """测试标签名过长"""
        invalid_data = {
            "name": "x" * 50,  # 超过30字符限制
            "color": "#ff5722",
            "is_active": True
        }
        response = client.post(
            "/admin/tags/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_tag_color_invalid(self):
        """测试无效颜色格式"""
        invalid_data = {
            "name": "正常标签名",
            "color": "not_a_color",  # 无效颜色格式
            "is_active": True
        }
        response = client.post(
            "/admin/tags/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422
    
    def test_tag_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_data = {
            "color": "#ff5722",
            "is_active": True
            # 缺少name字段
        }
        response = client.post(
            "/admin/tags/", 
            json=invalid_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 422


class TestTagFiltering:
    """测试标签筛选功能"""
    
    def test_filter_active_tags(self):
        """测试筛选激活的标签"""
        # 创建激活和非激活的标签
        active_tag = {
            "name": "激活标签",
            "color": "#4caf50",
            "is_active": True
        }
        inactive_tag = {
            "name": "非激活标签", 
            "color": "#f44336",
            "is_active": False
        }
        
        client.post("/admin/tags/", json=active_tag, headers=get_auth_headers())
        client.post("/admin/tags/", json=inactive_tag, headers=get_auth_headers())
        
        # 只获取激活的标签
        response = client.get(
            "/admin/tags/?active_only=true", 
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        
        data = response.json()
        # 验证返回的标签都是激活状态
        for tag in data["items"]:
            assert tag["is_active"] is True


class TestTagColors:
    """测试标签颜色功能"""
    
    def test_create_tag_with_custom_color(self):
        """测试创建自定义颜色的标签"""
        test_data = get_unique_tag_data()
        test_data["color"] = "#e91e63"
        
        response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["color"] == "#e91e63"
    
    def test_create_tag_default_color(self):
        """测试创建使用默认颜色的标签"""
        test_data = get_unique_tag_data()
        del test_data["color"]  # 不提供颜色，使用默认值
        
        response = client.post(
            "/admin/tags/", 
            json=test_data,
            headers=get_auth_headers()
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["color"] == "#3b82f6"  # 默认颜色 