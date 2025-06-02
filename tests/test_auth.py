"""
认证功能测试
测试HTTP Basic Auth和IP限频功能
"""
import pytest
import base64
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_admin_endpoint_without_auth():
    """测试未认证访问管理端点"""
    response = client.get("/admin")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Basic"

def test_admin_endpoint_with_wrong_credentials():
    """测试错误凭证访问管理端点"""
    # 创建错误的认证头
    credentials = base64.b64encode(b"wrong:password").decode("ascii")
    headers = {"Authorization": f"Basic {credentials}"}
    
    response = client.get("/admin", headers=headers)
    assert response.status_code == 401
    assert "管理员认证失败" in response.json()["detail"]

def test_admin_endpoint_with_correct_credentials():
    """测试正确凭证访问管理端点"""
    # 使用默认的管理员凭证
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    headers = {"Authorization": f"Basic {credentials}"}
    
    response = client.get("/admin", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["admin_verified"] is True
    assert "欢迎访问管理员仪表板" in data["message"]
    assert "/admin/categories" in data["available_endpoints"]

def test_rate_limit_functionality():
    """测试限频功能"""
    # 首次访问应该成功
    response = client.get("/api/test-rate-limit")
    assert response.status_code == 200
    assert "限频测试成功" in response.json()["message"]
    
    # 连续访问，直到触发限频
    for i in range(2):  # 第2、3次访问
        response = client.get("/api/test-rate-limit")
        assert response.status_code == 200
    
    # 第4次访问应该被限频
    response = client.get("/api/test-rate-limit")
    assert response.status_code == 429
    assert "访问频率过高" in response.json()["detail"]

def test_rate_limit_status():
    """测试限频状态获取"""
    # 清理限频存储以避免与其他测试的冲突
    from app.auth import rate_limit_storage
    rate_limit_storage.clear()
    
    # 访问一次
    response = client.get("/api/test-rate-limit")
    assert response.status_code == 200
    
    # 检查限频状态
    data = response.json()
    limit_status = data["limit_status"]
    assert "ip_hash" in limit_status
    assert "count" in limit_status

def test_health_check_endpoints():
    """测试健康检查端点（无需认证）"""
    # 基础健康检查
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # 数据库健康检查
    response = client.get("/db-health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello World" in response.json()["message"]
    assert "提示词分享平台后端 MVP" in response.json()["app"]

def test_api_docs_accessible():
    """测试API文档端点可访问"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200 