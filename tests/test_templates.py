"""
模板系统和静态文件功能测试
测试Jinja2模板渲染和静态文件服务
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_homepage_template_rendering():
    """测试主页模板渲染"""
    response = client.get("/")
    assert response.status_code == 200
    
    # 检查返回的是HTML内容
    assert "text/html" in response.headers.get("content-type", "")
    
    # 检查HTML内容包含预期的元素
    content = response.text
    assert "<title>" in content
    assert "提示词分享平台" in content
    assert "发现优质" in content
    assert "AI提示词" in content
    
    # 检查Tailwind CSS引用
    assert "tailwindcss.com" in content
    
    # 检查Alpine.js引用
    assert "alpinejs" in content
    
    # 检查静态文件引用
    assert "/static/css/custom.css" in content
    assert "/static/js/main.js" in content

def test_static_css_accessible():
    """测试CSS静态文件可访问"""
    response = client.get("/static/css/custom.css")
    assert response.status_code == 200
    
    # 检查返回的是CSS内容
    assert "text/css" in response.headers.get("content-type", "")
    
    # 检查CSS内容
    content = response.text
    assert "提示词分享平台自定义样式" in content
    assert ".fade-in" in content
    assert "@keyframes" in content

def test_static_js_accessible():
    """测试JavaScript静态文件可访问"""
    response = client.get("/static/js/main.js")
    assert response.status_code == 200
    
    # 检查返回的是JavaScript内容
    content_type = response.headers.get("content-type", "")
    assert "javascript" in content_type or "text/plain" in content_type
    
    # 检查JavaScript内容
    content = response.text
    assert "提示词分享平台主要JavaScript文件" in content
    assert "const Utils" in content
    assert "copyPrompt" in content
    assert "likePrompt" in content

def test_static_file_not_found():
    """测试不存在的静态文件返回404"""
    response = client.get("/static/nonexistent.css")
    assert response.status_code == 404

def test_template_context_variables():
    """测试模板上下文变量"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查传递给模板的变量
    assert "发现和分享优质的AI提示词" in content

def test_responsive_design_meta():
    """测试响应式设计元标签"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    assert 'name="viewport"' in content
    assert 'width=device-width' in content
    assert 'initial-scale=1.0' in content

def test_navigation_links():
    """测试导航链接"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查导航链接
    assert 'href="/"' in content  # 首页链接
    assert 'href="/admin"' in content  # 管理链接
    assert 'href="/docs"' in content  # API文档链接

def test_feature_cards_display():
    """测试功能特性卡片显示"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查六个功能特性卡片
    assert "分类管理" in content
    assert "标签系统" in content
    assert "一键复制" in content
    assert "点赞互动" in content
    assert "智能搜索" in content
    assert "便捷管理" in content

def test_alpine_js_integration():
    """测试Alpine.js集成"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查Alpine.js的使用
    assert 'x-data="statusChecker()"' in content
    assert 'x-init="checkStatus()"' in content
    assert 'x-text="appStatus"' in content
    assert 'x-text="dbStatus"' in content

def test_status_checker_script():
    """测试状态检查脚本"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查状态检查的JavaScript函数
    assert "statusChecker()" in content
    assert "checkStatus()" in content
    assert "/health" in content
    assert "/db-health" in content

def test_css_animations_classes():
    """测试CSS动画类"""
    response = client.get("/static/css/custom.css")
    assert response.status_code == 200
    
    content = response.text
    # 检查动画相关的CSS类
    assert ".fade-in" in content
    assert ".slide-in" in content
    assert ".loading-spinner" in content
    assert ".toast" in content
    assert ".card-hover" in content
    assert "@keyframes fadeIn" in content
    assert "@keyframes spin" in content

def test_javascript_utility_functions():
    """测试JavaScript工具函数"""
    response = client.get("/static/js/main.js")
    assert response.status_code == 200
    
    content = response.text
    # 检查工具函数
    assert "showToast" in content
    assert "copyToClipboard" in content
    assert "debounce" in content
    assert "throttle" in content
    assert "formatDate" in content
    
    # 检查API封装
    assert "const API" in content
    assert "async request" in content
    assert "async get" in content
    assert "async post" in content

def test_favicon_and_meta():
    """测试网站图标和元数据"""
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    # 检查基本的HTML元数据
    assert 'lang="zh-CN"' in content
    assert 'charset="UTF-8"' in content
    assert '<title>' in content
    assert 'name="description"' in content 