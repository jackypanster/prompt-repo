"""
公开页面集成测试
测试主页、分类页面、标签页面的功能
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
def create_test_data():
    """创建测试数据"""
    import time
    timestamp = int(time.time() * 1000000)
    
    # 创建测试分类
    category_data = {
        "name": f"测试分类_{timestamp}",
        "description": "测试分类描述",
        "is_active": True
    }
    category_response = client.post("/admin/categories/", json=category_data, headers=get_auth_headers())
    category = category_response.json()
    
    # 创建测试标签
    tag_data = {
        "name": f"测试标签_{timestamp}",
        "color": "#ff6b6b",
        "is_active": True
    }
    tag_response = client.post("/admin/tags/", json=tag_data, headers=get_auth_headers())
    tag = tag_response.json()
    
    # 创建测试提示词
    prompts = []
    for i in range(3):
        prompt_data = {
            "title": f"测试提示词_{i}_{timestamp}",
            "content": f"这是第{i+1}个测试提示词的内容。包含详细的示例和说明。",
            "description": f"第{i+1}个提示词的描述",
            "category_id": category["id"],
            "tag_ids": [tag["id"]],
            "is_featured": i == 0,  # 第一个设为精选
            "is_active": True
        }
        prompt_response = client.post("/admin/prompts/", json=prompt_data, headers=get_auth_headers())
        prompts.append(prompt_response.json())
    
    return {
        "category": category,
        "tag": tag,
        "prompts": prompts
    }


class TestHomepage:
    """测试主页功能"""
    
    def test_homepage_access(self):
        """测试主页访问"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # 检查页面标题
        assert "提示词分享平台" in response.text
    
    def test_homepage_with_data(self):
        """测试有数据时的主页"""
        # 创建测试数据
        test_data = create_test_data()
        
        response = client.get("/")
        assert response.status_code == 200
        
        # 检查页面包含必要元素
        content = response.text
        assert "category-filter" in content  # 分类筛选器
        assert "tag-filter" in content      # 标签筛选器
        assert "sort-filter" in content     # 排序选择器
    
    def test_homepage_pagination(self):
        """测试主页分页"""
        response = client.get("/?page=1&per_page=5")
        assert response.status_code == 200
        
        # 测试页码范围验证
        response = client.get("/?page=0")  # 无效页码
        assert response.status_code == 422
        
        response = client.get("/?per_page=0")  # 无效每页数量
        assert response.status_code == 422
    
    def test_homepage_sorting(self):
        """测试主页排序"""
        sort_options = ["created_at", "hot", "like_count", "copy_count"]
        
        for sort_option in sort_options:
            response = client.get(f"/?sort={sort_option}")
            assert response.status_code == 200
    
    def test_homepage_filtering(self):
        """测试主页筛选"""
        test_data = create_test_data()
        
        # 按分类筛选
        response = client.get(f"/?category={test_data['category']['name']}")
        assert response.status_code == 200
        
        # 按标签筛选
        response = client.get(f"/?tag={test_data['tag']['name']}")
        assert response.status_code == 200
        
        # 组合筛选
        response = client.get(f"/?category={test_data['category']['name']}&tag={test_data['tag']['name']}")
        assert response.status_code == 200


class TestCategoryPage:
    """测试分类页面功能"""
    
    def test_category_page_access(self):
        """测试分类页面访问"""
        test_data = create_test_data()
        category_name = test_data["category"]["name"]
        
        response = client.get(f"/category/{category_name}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # 检查页面包含分类信息
        content = response.text
        assert category_name in content
        assert "首页" in content  # 面包屑导航
    
    def test_category_page_not_found(self):
        """测试访问不存在的分类"""
        response = client.get("/category/不存在的分类")
        assert response.status_code == 404
    
    def test_category_page_pagination(self):
        """测试分类页面分页"""
        test_data = create_test_data()
        category_name = test_data["category"]["name"]
        
        response = client.get(f"/category/{category_name}?page=1&per_page=2")
        assert response.status_code == 200
        
        # 测试无效参数
        response = client.get(f"/category/{category_name}?page=0")
        assert response.status_code == 422
    
    def test_category_page_sorting(self):
        """测试分类页面排序"""
        test_data = create_test_data()
        category_name = test_data["category"]["name"]
        
        sort_options = ["created_at", "hot", "like_count", "copy_count"]
        for sort_option in sort_options:
            response = client.get(f"/category/{category_name}?sort={sort_option}")
            assert response.status_code == 200


class TestTagPage:
    """测试标签页面功能"""
    
    def test_tag_page_access(self):
        """测试标签页面访问"""
        test_data = create_test_data()
        tag_name = test_data["tag"]["name"]
        
        response = client.get(f"/tag/{tag_name}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # 检查页面包含标签信息
        content = response.text
        assert tag_name in content
        assert "首页" in content  # 面包屑导航
    
    def test_tag_page_not_found(self):
        """测试访问不存在的标签"""
        response = client.get("/tag/不存在的标签")
        assert response.status_code == 404
    
    def test_tag_page_pagination(self):
        """测试标签页面分页"""
        test_data = create_test_data()
        tag_name = test_data["tag"]["name"]
        
        response = client.get(f"/tag/{tag_name}?page=1&per_page=2")
        assert response.status_code == 200
        
        # 测试无效参数
        response = client.get(f"/tag/{tag_name}?page=0")
        assert response.status_code == 422
    
    def test_tag_page_sorting(self):
        """测试标签页面排序"""
        test_data = create_test_data()
        tag_name = test_data["tag"]["name"]
        
        sort_options = ["created_at", "hot", "like_count", "copy_count"]
        for sort_option in sort_options:
            response = client.get(f"/tag/{tag_name}?sort={sort_option}")
            assert response.status_code == 200


class TestPageContent:
    """测试页面内容显示"""
    
    def test_prompt_list_display(self):
        """测试提示词列表显示"""
        test_data = create_test_data()
        
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        # 检查提示词卡片的关键元素
        for prompt in test_data["prompts"]:
            assert prompt["title"] in content
    
    def test_featured_prompt_display(self):
        """测试精选提示词显示"""
        test_data = create_test_data()
        
        response = client.get("/")
        assert response.status_code == 200
        
        # 检查精选标识
        content = response.text
        assert "精选" in content
    
    def test_category_and_tag_links(self):
        """测试分类和标签链接"""
        test_data = create_test_data()
        
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        # 检查分类和标签链接
        assert f"/category/{test_data['category']['name']}" in content
        assert f"/tag/{test_data['tag']['name']}" in content
    
    def test_empty_state(self):
        """测试空状态显示"""
        # 测试不存在的分类的空状态
        response = client.get("/category/空分类测试")
        assert response.status_code == 404
        
        # 测试不存在的标签的空状态  
        response = client.get("/tag/空标签测试")
        assert response.status_code == 404


class TestResponseFormat:
    """测试响应格式"""
    
    def test_html_content_type(self):
        """测试HTML内容类型"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_utf8_encoding(self):
        """测试UTF-8编码支持"""
        test_data = create_test_data()
        
        response = client.get("/")
        assert response.status_code == 200
        
        # 检查中文内容正确显示
        content = response.text
        assert "提示词分享平台" in content
        assert test_data["category"]["name"] in content


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_page_parameters(self):
        """测试无效页面参数"""
        # 负数页码
        response = client.get("/?page=-1")
        assert response.status_code == 422
        
        # 过大的每页数量
        response = client.get("/?per_page=1000")
        assert response.status_code == 422
        
        # 非数字参数
        response = client.get("/?page=abc")
        assert response.status_code == 422
    
    def test_invalid_sort_parameters(self):
        """测试无效排序参数"""
        # 目前排序参数不验证，任何值都接受
        response = client.get("/?sort=invalid_sort")
        assert response.status_code == 200
    
    def test_category_not_found(self):
        """测试分类不存在"""
        response = client.get("/category/不存在的分类123")
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_tag_not_found(self):
        """测试标签不存在"""
        response = client.get("/tag/不存在的标签123")
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"] 