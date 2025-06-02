#!/usr/bin/env python3
"""
提示词管理API的命令行测试脚本
使用requests库模拟curl测试所有管理端点
"""
import requests
import base64
import time
import json

# 测试配置
BASE_URL = 'http://localhost:8080'
credentials = base64.b64encode(b'admin:admin123').decode('ascii')
headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

def print_test_result(test_name, success, details=""):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_auth_protection():
    """测试认证保护"""
    print("\n🔐 测试认证保护")
    
    # 测试未认证访问
    no_auth_headers = {'Content-Type': 'application/json'}
    
    endpoints = [
        ('POST', '/admin/prompts/', {}),
        ('GET', '/admin/prompts/', None),
        ('PUT', '/admin/prompts/1', {}),
        ('DELETE', '/admin/prompts/1', None)
    ]
    
    for method, endpoint, data in endpoints:
        if method == 'GET' or method == 'DELETE':
            response = requests.request(method, f'{BASE_URL}{endpoint}', headers=no_auth_headers)
        else:
            response = requests.request(method, f'{BASE_URL}{endpoint}', json=data, headers=no_auth_headers)
        
        success = response.status_code == 401
        print_test_result(f"{method} {endpoint} 未认证访问", success, 
                         f"状态码: {response.status_code}")

def create_test_dependencies():
    """创建测试依赖的分类和标签"""
    timestamp = int(time.time() * 1000000)
    
    # 创建测试分类
    category_data = {
        'name': f'测试分类_{timestamp}',
        'description': '测试用分类',
        'is_active': True
    }
    category_response = requests.post(f'{BASE_URL}/admin/categories/', json=category_data, headers=headers)
    category_id = category_response.json()['id']
    
    # 创建测试标签
    tag_data = {
        'name': f'测试标签_{timestamp}',
        'color': '#ff0000',
        'is_active': True
    }
    tag_response = requests.post(f'{BASE_URL}/admin/tags/', json=tag_data, headers=headers)
    tag_id = tag_response.json()['id']
    
    return category_id, tag_id, timestamp

def test_prompt_crud():
    """测试提示词CRUD操作"""
    print("\n📝 测试提示词CRUD操作")
    
    # 创建依赖
    category_id, tag_id, timestamp = create_test_dependencies()
    
    # 1. 创建提示词
    prompt_data = {
        'title': f'测试提示词_{timestamp}',
        'content': f'这是一个测试提示词内容，时间戳：{timestamp}',
        'description': '这是测试提示词的描述',
        'category_id': category_id,
        'tag_ids': [tag_id],
        'is_featured': True,
        'is_active': True
    }
    
    create_response = requests.post(f'{BASE_URL}/admin/prompts/', json=prompt_data, headers=headers)
    success = create_response.status_code == 201
    print_test_result("创建提示词", success, f"状态码: {create_response.status_code}")
    
    if not success:
        print(f"   错误详情: {create_response.text}")
        return
    
    prompt_id = create_response.json()['id']
    created_prompt = create_response.json()
    
    # 验证创建的数据
    data_valid = (
        created_prompt['title'] == prompt_data['title'] and
        created_prompt['content'] == prompt_data['content'] and
        created_prompt['category_id'] == category_id and
        len(created_prompt['tags']) == 1
    )
    print_test_result("创建数据验证", data_valid, 
                     f"标题匹配: {created_prompt['title'] == prompt_data['title']}")
    
    # 2. 获取提示词列表
    list_response = requests.get(f'{BASE_URL}/admin/prompts/', headers=headers)
    success = list_response.status_code == 200
    print_test_result("获取提示词列表", success, f"状态码: {list_response.status_code}")
    
    if success:
        list_data = list_response.json()
        has_pagination = all(key in list_data for key in ['items', 'total', 'page', 'per_page'])
        print_test_result("列表分页信息", has_pagination, f"总数: {list_data.get('total', 0)}")
    
    # 3. 获取单个提示词
    get_response = requests.get(f'{BASE_URL}/admin/prompts/{prompt_id}', headers=headers)
    success = get_response.status_code == 200
    print_test_result("获取单个提示词", success, f"状态码: {get_response.status_code}")
    
    # 4. 更新提示词
    update_data = {
        'title': f'更新后的提示词_{timestamp}',
        'description': '更新后的描述',
        'is_featured': False
    }
    
    update_response = requests.put(f'{BASE_URL}/admin/prompts/{prompt_id}', json=update_data, headers=headers)
    success = update_response.status_code == 200
    print_test_result("更新提示词", success, f"状态码: {update_response.status_code}")
    
    if success:
        updated_prompt = update_response.json()
        update_valid = updated_prompt['title'] == update_data['title']
        print_test_result("更新数据验证", update_valid, 
                         f"新标题: {updated_prompt['title']}")
    
    # 5. 删除提示词
    delete_response = requests.delete(f'{BASE_URL}/admin/prompts/{prompt_id}', headers=headers)
    success = delete_response.status_code == 200
    print_test_result("删除提示词", success, f"状态码: {delete_response.status_code}")
    
    # 6. 验证删除
    verify_response = requests.get(f'{BASE_URL}/admin/prompts/{prompt_id}', headers=headers)
    success = verify_response.status_code == 404
    print_test_result("验证删除", success, f"状态码: {verify_response.status_code}")

def test_data_validation():
    """测试数据验证"""
    print("\n🔍 测试数据验证")
    
    # 测试缺少必需字段
    invalid_data = {
        'content': '只有内容，缺少标题'
    }
    
    response = requests.post(f'{BASE_URL}/admin/prompts/', json=invalid_data, headers=headers)
    success = response.status_code == 422
    print_test_result("缺少必需字段", success, f"状态码: {response.status_code}")
    
    # 测试字段长度限制
    category_id, tag_id, timestamp = create_test_dependencies()
    
    long_title_data = {
        'title': 'x' * 101,  # 超过100字符限制
        'content': '测试内容',
        'category_id': category_id,
        'tag_ids': [tag_id]
    }
    
    response = requests.post(f'{BASE_URL}/admin/prompts/', json=long_title_data, headers=headers)
    success = response.status_code == 422
    print_test_result("标题长度限制", success, f"状态码: {response.status_code}")

def test_tag_relations():
    """测试标签关联功能"""
    print("\n🏷️ 测试标签关联功能")
    
    # 创建依赖
    category_id, tag_id, timestamp = create_test_dependencies()
    
    # 创建额外的标签
    tag_data2 = {
        'name': f'测试标签2_{timestamp}',
        'color': '#00ff00',
        'is_active': True
    }
    tag_response2 = requests.post(f'{BASE_URL}/admin/tags/', json=tag_data2, headers=headers)
    tag_id2 = tag_response2.json()['id']
    
    # 创建包含多个标签的提示词
    prompt_data = {
        'title': f'多标签提示词_{timestamp}',
        'content': '测试多标签关联',
        'category_id': category_id,
        'tag_ids': [tag_id, tag_id2],
        'is_featured': False,
        'is_active': True
    }
    
    create_response = requests.post(f'{BASE_URL}/admin/prompts/', json=prompt_data, headers=headers)
    success = create_response.status_code == 201
    print_test_result("创建多标签提示词", success, f"状态码: {create_response.status_code}")
    
    if success:
        created_prompt = create_response.json()
        tag_count_valid = len(created_prompt['tags']) == 2
        print_test_result("多标签验证", tag_count_valid, 
                         f"标签数量: {len(created_prompt['tags'])}")
        
        prompt_id = created_prompt['id']
        
        # 测试更新标签关联
        update_data = {
            'tag_ids': [tag_id2]  # 只保留一个标签
        }
        
        update_response = requests.put(f'{BASE_URL}/admin/prompts/{prompt_id}', json=update_data, headers=headers)
        success = update_response.status_code == 200
        print_test_result("更新标签关联", success, f"状态码: {update_response.status_code}")
        
        if success:
            updated_prompt = update_response.json()
            tag_update_valid = len(updated_prompt['tags']) == 1
            print_test_result("标签更新验证", tag_update_valid, 
                             f"更新后标签数量: {len(updated_prompt['tags'])}")

def test_filtering():
    """测试筛选功能"""
    print("\n🔍 测试筛选功能")
    
    # 创建依赖
    category_id, tag_id, timestamp = create_test_dependencies()
    
    # 创建测试提示词
    prompt_data = {
        'title': f'筛选测试提示词_{timestamp}',
        'content': '测试筛选功能',
        'category_id': category_id,
        'tag_ids': [tag_id],
        'is_featured': True,
        'is_active': True
    }
    
    create_response = requests.post(f'{BASE_URL}/admin/prompts/', json=prompt_data, headers=headers)
    
    if create_response.status_code == 201:
        # 按分类筛选
        filter_response = requests.get(f'{BASE_URL}/admin/prompts/?category_id={category_id}', headers=headers)
        success = filter_response.status_code == 200
        print_test_result("按分类筛选", success, f"状态码: {filter_response.status_code}")
        
        # 按标签筛选
        filter_response = requests.get(f'{BASE_URL}/admin/prompts/?tag_id={tag_id}', headers=headers)
        success = filter_response.status_code == 200
        print_test_result("按标签筛选", success, f"状态码: {filter_response.status_code}")
        
        # 按精选状态筛选
        filter_response = requests.get(f'{BASE_URL}/admin/prompts/?is_featured=true', headers=headers)
        success = filter_response.status_code == 200
        print_test_result("按精选状态筛选", success, f"状态码: {filter_response.status_code}")

def main():
    """主测试函数"""
    print("🚀 开始提示词管理API测试")
    print(f"📡 测试服务器: {BASE_URL}")
    
    try:
        # 测试服务器连接
        health_response = requests.get(f'{BASE_URL}/health')
        if health_response.status_code != 200:
            print("❌ 服务器连接失败，请确保服务器正在运行")
            return
        
        print("✅ 服务器连接正常")
        
        # 运行所有测试
        test_auth_protection()
        test_prompt_crud()
        test_data_validation()
        test_tag_relations()
        test_filtering()
        
        print("\n🎉 所有测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器在 http://localhost:8080 运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 