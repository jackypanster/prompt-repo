#!/usr/bin/env python3
"""
分类管理API的命令行测试脚本
模拟curl命令测试所有管理端点
"""
import requests
import json
import base64
import time

# 配置
BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "admin123"

# 认证头
credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

def print_response(title, response):
    """打印响应信息"""
    print(f"\n=== {title} ===")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应: {response.text}")

def test_categories_crud():
    """测试分类CRUD操作"""
    timestamp = int(time.time())
    
    # 1. 创建分类
    print("1. 测试创建分类")
    create_data = {
        "name": f"curl测试分类_{timestamp}",
        "description": "通过curl命令创建的测试分类",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/categories/",
        headers=headers,
        json=create_data
    )
    print_response("创建分类", response)
    
    if response.status_code != 201:
        print("❌ 创建分类失败")
        return
    
    category_id = response.json()["id"]
    print(f"✅ 创建分类成功，ID: {category_id}")
    
    # 2. 获取分类列表
    print("\n2. 测试获取分类列表")
    response = requests.get(
        f"{BASE_URL}/admin/categories/?page=1&per_page=5",
        headers=headers
    )
    print_response("获取分类列表", response)
    
    if response.status_code == 200:
        print("✅ 获取分类列表成功")
    else:
        print("❌ 获取分类列表失败")
    
    # 3. 获取单个分类
    print("\n3. 测试获取单个分类")
    response = requests.get(
        f"{BASE_URL}/admin/categories/{category_id}",
        headers=headers
    )
    print_response("获取单个分类", response)
    
    if response.status_code == 200:
        print("✅ 获取单个分类成功")
    else:
        print("❌ 获取单个分类失败")
    
    # 4. 更新分类
    print("\n4. 测试更新分类")
    update_data = {
        "name": f"curl更新分类_{timestamp}",
        "description": "通过curl命令更新的分类",
        "is_active": False
    }
    
    response = requests.put(
        f"{BASE_URL}/admin/categories/{category_id}",
        headers=headers,
        json=update_data
    )
    print_response("更新分类", response)
    
    if response.status_code == 200:
        print("✅ 更新分类成功")
    else:
        print("❌ 更新分类失败")
    
    # 5. 删除分类
    print("\n5. 测试删除分类")
    response = requests.delete(
        f"{BASE_URL}/admin/categories/{category_id}",
        headers=headers
    )
    print_response("删除分类", response)
    
    if response.status_code == 200:
        print("✅ 删除分类成功")
    else:
        print("❌ 删除分类失败")

def test_auth_protection():
    """测试认证保护"""
    print("\n=== 测试认证保护 ===")
    
    # 无认证访问
    response = requests.get(f"{BASE_URL}/admin/categories/")
    print_response("无认证访问", response)
    
    if response.status_code == 401:
        print("✅ 认证保护正常")
    else:
        print("❌ 认证保护失败")

def test_validation():
    """测试数据验证"""
    print("\n=== 测试数据验证 ===")
    
    # 无效数据
    invalid_data = {
        "name": "",  # 空名称
        "description": "x" * 300,  # 描述过长
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/categories/",
        headers=headers,
        json=invalid_data
    )
    print_response("无效数据验证", response)
    
    if response.status_code == 422:
        print("✅ 数据验证正常")
    else:
        print("❌ 数据验证失败")

if __name__ == "__main__":
    print("开始分类管理API的命令行测试...")
    
    try:
        # 测试健康检查
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 应用未启动或不可访问")
            exit(1)
        
        print("✅ 应用正常运行")
        
        # 执行测试
        test_auth_protection()
        test_validation()
        test_categories_crud()
        
        print("\n🎉 所有命令行测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用，请确保应用在 http://localhost:8080 运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}") 