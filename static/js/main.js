// 提示词分享平台主要JavaScript文件

// 通用工具函数
const Utils = {
    // 显示toast提示
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast fixed top-4 right-4 z-50 px-4 py-2 rounded-md shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            type === 'warning' ? 'bg-yellow-500' : 
            'bg-blue-500'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 3000);
    },

    // 复制文本到剪贴板
    async copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // 回退方案
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                const success = document.execCommand('copy');
                document.body.removeChild(textArea);
                return success;
            }
        } catch (error) {
            console.error('复制失败:', error);
            return false;
        }
    },

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    },

    // 格式化日期
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        
        return date.toLocaleDateString('zh-CN');
    },

    // 简单的模板引擎
    template(template, data) {
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data[key] || '';
        });
    }
};

// API请求封装
const API = {
    baseURL: '',
    
    async request(url, options = {}) {
        try {
            const response = await fetch(this.baseURL + url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    },

    async get(url) {
        return this.request(url);
    },

    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// 复制功能
async function copyPrompt(promptId, content) {
    try {
        // 复制到剪贴板
        const success = await Utils.copyToClipboard(content);
        
        if (success) {
            // 调用API统计复制次数
            try {
                await API.post(`/api/prompts/${promptId}/copy`);
            } catch (error) {
                // 即使统计失败，复制功能依然可用
                console.warn('复制统计失败:', error);
            }
            
            Utils.showToast('已复制到剪贴板！', 'success');
        } else {
            Utils.showToast('复制失败，请手动选择文本复制', 'error');
        }
    } catch (error) {
        Utils.showToast('复制失败', 'error');
    }
}

// 点赞功能
async function likePrompt(promptId) {
    try {
        await API.post(`/api/prompts/${promptId}/like`);
        Utils.showToast('点赞成功！', 'success');
        
        // 更新点赞数显示
        const likeCountElement = document.querySelector(`#like-count-${promptId}`);
        if (likeCountElement) {
            const currentCount = parseInt(likeCountElement.textContent) || 0;
            likeCountElement.textContent = currentCount + 1;
        }
        
        // 更新按钮状态
        const likeButton = document.querySelector(`#like-button-${promptId}`);
        if (likeButton) {
            likeButton.classList.add('liked');
            likeButton.disabled = true;
        }
        
    } catch (error) {
        if (error.message.includes('429')) {
            Utils.showToast('操作过于频繁，请稍后再试', 'warning');
        } else if (error.message.includes('已点赞')) {
            Utils.showToast('您已经点赞过了', 'warning');
        } else {
            Utils.showToast('点赞失败', 'error');
        }
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 添加键盘快捷键支持
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K 打开搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // 添加平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 为外部链接添加target="_blank"
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        if (!link.hostname === window.location.hostname) {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        }
    });

    console.log('提示词分享平台 v0.3.0 已加载');
});

// 导出到全局作用域
window.Utils = Utils;
window.API = API;
window.copyPrompt = copyPrompt;
window.likePrompt = likePrompt; 