"""
认证和权限控制模块
- HTTP Basic Auth管理员认证
- IP限频装饰器防滥用
- 权限验证装饰器
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from functools import wraps
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import collections

# HTTP Basic Auth 实例
security = HTTPBasic()

# IP限频存储：{ip_hash: {"count": int, "window_start": datetime}}
rate_limit_storage: Dict[str, Dict] = {}

# 管理员认证配置（从环境变量读取，默认值仅用于开发）
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def hash_ip(ip: str) -> str:
    """对IP地址进行哈希处理以保护隐私"""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """验证管理员凭证"""
    # 使用constant_time_compare防止时序攻击
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), 
        ADMIN_USERNAME.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), 
        ADMIN_PASSWORD.encode("utf8")
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="管理员认证失败",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    # 优先检查代理头
    forwarded_ip = request.headers.get("X-Forwarded-For")
    if forwarded_ip:
        return forwarded_ip.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 回退到连接IP
    return request.client.host if request.client else "unknown"

def rate_limit(max_requests: int = 5, window_minutes: int = 5):
    """IP限频装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = get_client_ip(request)
            ip_hash = hash_ip(client_ip)
            now = datetime.now(timezone.utc)
            
            # 清理过期的限频记录
            cleanup_expired_limits()
            
            # 检查当前IP的限频状态
            if ip_hash in rate_limit_storage:
                limit_info = rate_limit_storage[ip_hash]
                window_start = limit_info["window_start"]
                
                # 检查是否在同一时间窗口内
                if now - window_start < timedelta(minutes=window_minutes):
                    if limit_info["count"] >= max_requests:
                        raise HTTPException(
                            status_code=429,
                            detail=f"访问频率过高，请在{window_minutes}分钟后重试"
                        )
                    # 增加计数
                    limit_info["count"] += 1
                else:
                    # 新的时间窗口，重置计数
                    rate_limit_storage[ip_hash] = {
                        "count": 1,
                        "window_start": now
                    }
            else:
                # 第一次访问
                rate_limit_storage[ip_hash] = {
                    "count": 1,
                    "window_start": now
                }
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def cleanup_expired_limits():
    """清理过期的限频记录"""
    now = datetime.now(timezone.utc)
    expired_keys = [
        ip_hash for ip_hash, info in rate_limit_storage.items()
        if now - info["window_start"] > timedelta(minutes=30)  # 30分钟后清理
    ]
    for key in expired_keys:
        del rate_limit_storage[key]

def get_rate_limit_status(request: Request) -> dict:
    """获取当前IP的限频状态（用于调试）"""
    client_ip = get_client_ip(request)
    ip_hash = hash_ip(client_ip)
    
    if ip_hash in rate_limit_storage:
        limit_info = rate_limit_storage[ip_hash]
        return {
            "ip_hash": ip_hash,
            "count": limit_info["count"],
            "window_start": limit_info["window_start"].isoformat(),
            "remaining_time": str(timedelta(minutes=5) - 
                                (datetime.now(timezone.utc) - limit_info["window_start"]))
        }
    else:
        return {
            "ip_hash": ip_hash,
            "status": "no_limits"
        } 