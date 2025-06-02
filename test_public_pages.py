#!/usr/bin/env python3
"""
公开页面功能测试脚本
验证主页、分类页面、标签页面的功能
"""
import requests
import base64
import time
import json

# 测试配置
BASE_URL = 'http://localhost:8080'
credentials = base64.b64encode(b'admin:admin123').decode('ascii')
auth_headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

def print_test_result(test_name, success, details=""):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def create_test_data():
    """创建测试数据"""
    timestamp = int(time.time() * 1000000)
    
    # 创建测试分类
    category_data = {
        'name': f'前端开发_{timestamp}',
        'description': '前端开发相关的提示词',
        'is_active': True
    }
    category_response = requests.post(f'{BASE_URL}/admin/categories/', json=category_data, headers=auth_headers)
    category_id = category_response.json()['id']
    category_name = category_data['name']
    
    # 创建测试标签
    tags = []
    for i, tag_name in enumerate(['JavaScript', 'React', 'CSS']):
        tag_data = {
            'name': f'{tag_name}_{timestamp}',
            'color': ['#ff6b6b', '#51cf66', '#339af0'][i],
            'is_active': True
        }
        tag_response = requests.post(f'{BASE_URL}/admin/tags/', json=tag_data, headers=auth_headers)
        tags.append({
            'id': tag_response.json()['id'],
            'name': tag_data['name']
        })
    
    # 创建测试提示词
    prompts = []
    for i in range(5):
        prompt_data = {
            'title': f'前端提示词 {i+1}_{timestamp}',
            'content': f'这是第{i+1}个前端开发相关的提示词内容。包含详细的代码示例和最佳实践。',
            'description': f'第{i+1}个提示词的描述',
            'category_id': category_id,
            'tag_ids': [tags[j]['id'] for j in range(min(i+1, 3))],  # 逐渐增加标签数量
            'is_featured': i == 0,  # 第一个设为精选
            'is_active': True,
            'like_count': i * 3,
            'copy_count': i * 5
        }
        prompt_response = requests.post(f'{BASE_URL}/admin/prompts/', json=prompt_data, headers=auth_headers)
        prompts.append(prompt_response.json())
    
    return {
        'category_name': category_name,
        'tags': tags,
        'prompts': prompts
    }

def test_homepage():
    """测试主页功能"""
    print("\n🏠 测试主页功能")
    
    # 测试主页访问
    response = requests.get(f'{BASE_URL}/')
    success = response.status_code == 200 and 'text/html' in response.headers.get('content-type', '')
    print_test_result("主页访问", success, f"状态码: {response.status_code}")
    
    if success:
        html_content = response.text
        # 检查页面包含关键元素
        has_title = '提示词分享平台' in html_content
        has_filters = 'category-filter' in html_content and 'tag-filter' in html_content
        has_sort = 'sort-filter' in html_content
        
        print_test_result("页面标题", has_title)
        print_test_result("筛选功能", has_filters)
        print_test_result("排序功能", has_sort)
    
    # 测试分页
    page2_response = requests.get(f'{BASE_URL}/?page=2')
    success = page2_response.status_code == 200
    print_test_result("分页功能", success, f"第2页状态码: {page2_response.status_code}")
    
    # 测试排序
    hot_response = requests.get(f'{BASE_URL}/?sort=hot')
    success = hot_response.status_code == 200
    print_test_result("排序功能", success, f"热门排序状态码: {hot_response.status_code}")

def test_category_page(category_name):
    """测试分类页面"""
    print("\n📂 测试分类页面")
    
    # 测试分类页面访问
    response = requests.get(f'{BASE_URL}/category/{category_name}')
    success = response.status_code == 200
    print_test_result("分类页面访问", success, f"状态码: {response.status_code}")
    
    if success:
        html_content = response.text
        # 检查页面包含分类信息
        has_category_name = category_name in html_content
        has_breadcrumb = '首页' in html_content
        has_sort = 'sort-filter' in html_content
        
        print_test_result("分类名称显示", has_category_name)
        print_test_result("面包屑导航", has_breadcrumb)
        print_test_result("排序功能", has_sort)
    
    # 测试不存在的分类
    not_found_response = requests.get(f'{BASE_URL}/category/不存在的分类')
    success = not_found_response.status_code == 404
    print_test_result("不存在分类404", success, f"状态码: {not_found_response.status_code}")

def test_tag_page(tag_name):
    """测试标签页面"""
    print("\n🏷️ 测试标签页面")
    
    # 测试标签页面访问
    response = requests.get(f'{BASE_URL}/tag/{tag_name}')
    success = response.status_code == 200
    print_test_result("标签页面访问", success, f"状态码: {response.status_code}")
    
    if success:
        html_content = response.text
        # 检查页面包含标签信息
        has_tag_name = tag_name in html_content
        has_breadcrumb = '首页' in html_content
        has_sort = 'sort-filter' in html_content
        
        print_test_result("标签名称显示", has_tag_name)
        print_test_result("面包屑导航", has_breadcrumb)
        print_test_result("排序功能", has_sort)
    
    # 测试不存在的标签
    not_found_response = requests.get(f'{BASE_URL}/tag/不存在的标签')
    success = not_found_response.status_code == 404
    print_test_result("不存在标签404", success, f"状态码: {not_found_response.status_code}")

def test_filtering_and_sorting(category_name, tag_name):
    """测试筛选和排序功能"""
    print("\n🔍 测试筛选和排序功能")
    
    # 测试主页分类筛选
    response = requests.get(f'{BASE_URL}/?category={category_name}')
    success = response.status_code == 200
    print_test_result("主页分类筛选", success, f"状态码: {response.status_code}")
    
    # 测试主页标签筛选
    response = requests.get(f'{BASE_URL}/?tag={tag_name}')
    success = response.status_code == 200
    print_test_result("主页标签筛选", success, f"状态码: {response.status_code}")
    
    # 测试组合筛选
    response = requests.get(f'{BASE_URL}/?category={category_name}&tag={tag_name}')
    success = response.status_code == 200
    print_test_result("组合筛选", success, f"状态码: {response.status_code}")
    
    # 测试排序选项
    sort_options = ['created_at', 'hot', 'like_count', 'copy_count']
    for sort_option in sort_options:
        response = requests.get(f'{BASE_URL}/?sort={sort_option}')
        success = response.status_code == 200
        print_test_result(f"排序-{sort_option}", success, f"状态码: {response.status_code}")

def test_pagination_with_filters(category_name):
    """测试带筛选的分页"""
    print("\n📄 测试筛选分页功能")
    
    # 测试分类页面分页
    response = requests.get(f'{BASE_URL}/category/{category_name}?page=1&per_page=2')
    success = response.status_code == 200
    print_test_result("分类页面分页", success, f"状态码: {response.status_code}")
    
    # 测试主页带筛选的分页
    response = requests.get(f'{BASE_URL}/?category={category_name}&page=1&per_page=2')
    success = response.status_code == 200
    print_test_result("主页筛选分页", success, f"状态码: {response.status_code}")

def test_responsive_elements():
    """测试响应式元素（模拟不同设备）"""
    print("\n📱 测试响应式设计")
    
    # 模拟移动设备访问
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
    }
    
    response = requests.get(f'{BASE_URL}/', headers=mobile_headers)
    success = response.status_code == 200
    print_test_result("移动端访问", success, f"状态码: {response.status_code}")
    
    # 检查页面包含响应式类
    if success:
        html_content = response.text
        has_responsive_classes = 'md:grid-cols-2' in html_content and 'lg:grid-cols-3' in html_content
        print_test_result("响应式CSS类", has_responsive_classes)

def main():
    """主测试函数"""
    print("🚀 开始公开页面功能测试")
    print(f"📡 测试服务器: {BASE_URL}")
    
    try:
        # 检查服务器连接
        health_response = requests.get(f'{BASE_URL}/health')
        if health_response.status_code != 200:
            print("❌ 服务器连接失败，请确保服务器正在运行")
            return
        
        print("✅ 服务器连接正常")
        
        # 创建测试数据
        print("\n📝 创建测试数据...")
        test_data = create_test_data()
        print(f"✅ 测试数据创建完成")
        print(f"   分类: {test_data['category_name']}")
        print(f"   标签: {[tag['name'] for tag in test_data['tags']]}")
        print(f"   提示词: {len(test_data['prompts'])} 个")
        
        # 等待数据生效
        time.sleep(1)
        
        # 运行功能测试
        test_homepage()
        test_category_page(test_data['category_name'])
        test_tag_page(test_data['tags'][0]['name'])
        test_filtering_and_sorting(test_data['category_name'], test_data['tags'][0]['name'])
        test_pagination_with_filters(test_data['category_name'])
        test_responsive_elements()
        
        print("\n🎉 公开页面功能测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器在 http://localhost:8080 运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 