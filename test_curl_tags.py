#!/usr/bin/env python3
"""
标签管理API的命令行测试脚本
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

def test_tags_crud():
    """测试标签CRUD操作"""
    timestamp = int(time.time())
    
    # 1. 创建标签
    print("1. 测试创建标签")
    create_data = {
        "name": f"curl测试标签_{timestamp}",
        "color": "#ff5722",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/tags/",
        headers=headers,
        json=create_data
    )
    print_response("创建标签", response)
    
    if response.status_code != 201:
        print("❌ 创建标签失败")
        return
    
    tag_id = response.json()["id"]
    print(f"✅ 创建标签成功，ID: {tag_id}")
    
    # 2. 获取标签列表
    print("\n2. 测试获取标签列表")
    response = requests.get(
        f"{BASE_URL}/admin/tags/?page=1&per_page=5",
        headers=headers
    )
    print_response("获取标签列表", response)
    
    if response.status_code == 200:
        print("✅ 获取标签列表成功")
    else:
        print("❌ 获取标签列表失败")
    
    # 3. 获取单个标签
    print("\n3. 测试获取单个标签")
    response = requests.get(
        f"{BASE_URL}/admin/tags/{tag_id}",
        headers=headers
    )
    print_response("获取单个标签", response)
    
    if response.status_code == 200:
        print("✅ 获取单个标签成功")
    else:
        print("❌ 获取单个标签失败")
    
    # 4. 更新标签
    print("\n4. 测试更新标签")
    update_data = {
        "name": f"curl更新标签_{timestamp}",
        "color": "#4caf50",
        "is_active": False
    }
    
    response = requests.put(
        f"{BASE_URL}/admin/tags/{tag_id}",
        headers=headers,
        json=update_data
    )
    print_response("更新标签", response)
    
    if response.status_code == 200:
        print("✅ 更新标签成功")
    else:
        print("❌ 更新标签失败")
    
    # 5. 测试部分更新
    print("\n5. 测试部分更新标签（仅颜色）")
    partial_update = {
        "color": "#9c27b0"
    }
    
    response = requests.put(
        f"{BASE_URL}/admin/tags/{tag_id}",
        headers=headers,
        json=partial_update
    )
    print_response("部分更新标签", response)
    
    if response.status_code == 200:
        print("✅ 部分更新标签成功")
    else:
        print("❌ 部分更新标签失败")
    
    # 6. 删除标签
    print("\n6. 测试删除标签")
    response = requests.delete(
        f"{BASE_URL}/admin/tags/{tag_id}",
        headers=headers
    )
    print_response("删除标签", response)
    
    if response.status_code == 200:
        print("✅ 删除标签成功")
    else:
        print("❌ 删除标签失败")

def test_auth_protection():
    """测试认证保护"""
    print("\n=== 测试认证保护 ===")
    
    # 无认证访问
    response = requests.get(f"{BASE_URL}/admin/tags/")
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
        "color": "invalid_color",  # 无效颜色
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/tags/",
        headers=headers,
        json=invalid_data
    )
    print_response("无效数据验证", response)
    
    if response.status_code == 422:
        print("✅ 数据验证正常")
    else:
        print("❌ 数据验证失败")

def test_color_features():
    """测试标签颜色功能"""
    print("\n=== 测试标签颜色功能 ===")
    
    # 创建自定义颜色标签
    timestamp = int(time.time())
    color_data = {
        "name": f"颜色测试标签_{timestamp}",
        "color": "#e91e63",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/tags/",
        headers=headers,
        json=color_data
    )
    print_response("创建自定义颜色标签", response)
    
    if response.status_code == 201:
        data = response.json()
        if data["color"] == "#e91e63":
            print("✅ 自定义颜色功能正常")
        else:
            print("❌ 自定义颜色功能失败")
        
        # 清理测试数据
        tag_id = data["id"]
        requests.delete(f"{BASE_URL}/admin/tags/{tag_id}", headers=headers)
    else:
        print("❌ 创建自定义颜色标签失败")
    
    # 测试默认颜色
    default_color_data = {
        "name": f"默认颜色标签_{timestamp}",
        "is_active": True
        # 不提供color字段
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/tags/",
        headers=headers,
        json=default_color_data
    )
    print_response("创建默认颜色标签", response)
    
    if response.status_code == 201:
        data = response.json()
        if data["color"] == "#3b82f6":
            print("✅ 默认颜色功能正常")
        else:
            print("❌ 默认颜色功能失败")
        
        # 清理测试数据
        tag_id = data["id"]
        requests.delete(f"{BASE_URL}/admin/tags/{tag_id}", headers=headers)
    else:
        print("❌ 创建默认颜色标签失败")

def test_filtering():
    """测试筛选功能"""
    print("\n=== 测试筛选功能 ===")
    
    timestamp = int(time.time())
    # 创建激活标签
    active_tag = {
        "name": f"激活标签_{timestamp}",
        "color": "#4caf50",
        "is_active": True
    }
    
    # 创建非激活标签
    inactive_tag = {
        "name": f"非激活标签_{timestamp}",
        "color": "#f44336",
        "is_active": False
    }
    
    active_response = requests.post(f"{BASE_URL}/admin/tags/", headers=headers, json=active_tag)
    inactive_response = requests.post(f"{BASE_URL}/admin/tags/", headers=headers, json=inactive_tag)
    
    if active_response.status_code == 201 and inactive_response.status_code == 201:
        # 测试只获取激活标签
        response = requests.get(
            f"{BASE_URL}/admin/tags/?active_only=true&per_page=50",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            all_active = all(tag["is_active"] for tag in data["items"])
            if all_active:
                print("✅ 激活标签筛选功能正常")
            else:
                print("❌ 激活标签筛选功能失败")
        else:
            print("❌ 获取激活标签失败")
        
        # 清理测试数据
        requests.delete(f"{BASE_URL}/admin/tags/{active_response.json()['id']}", headers=headers)
        requests.delete(f"{BASE_URL}/admin/tags/{inactive_response.json()['id']}", headers=headers)
    else:
        print("❌ 创建测试标签失败")

if __name__ == "__main__":
    print("开始标签管理API的命令行测试...")
    
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
        test_color_features()
        test_filtering()
        test_tags_crud()
        
        print("\n🎉 所有标签管理命令行测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用，请确保应用在 http://localhost:8080 运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}") 