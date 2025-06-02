#!/usr/bin/env python3
"""
分类管理API测试脚本
用于调试分类创建问题
"""
import asyncio
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_category():
    """测试创建分类并查看详细错误"""
    # 准备认证头
    import base64
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    headers = {"Authorization": f"Basic {credentials}"}
    
    # 测试数据 - 使用时间戳确保唯一性
    import time
    timestamp = int(time.time())
    test_data = {
        "name": f"测试分类_{timestamp}",
        "description": "这是一个测试分类",
        "is_active": True
    }
    
    print("发送数据:", json.dumps(test_data, ensure_ascii=False, indent=2))
    
    # 发送请求
    response = client.post("/admin/categories/", json=test_data, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    
    try:
        response_data = response.json()
        print("响应内容:", json.dumps(response_data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"无法解析JSON响应: {e}")
        print(f"原始响应: {response.text}")
    
    return response

def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    print(f"健康检查: {response.status_code} - {response.json()}")

def test_db_health():
    """测试数据库健康检查"""
    response = client.get("/db-health")
    print(f"数据库健康检查: {response.status_code}")
    try:
        data = response.json()
        print("数据库状态:", json.dumps(data, ensure_ascii=False, indent=2))
    except:
        print("数据库健康检查响应:", response.text)

if __name__ == "__main__":
    print("=== 测试应用健康状态 ===")
    test_health_check()
    test_db_health()
    
    print("\n=== 测试分类创建 ===")
    test_create_category() 