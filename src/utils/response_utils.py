import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from src.core.exceptions import MoodCanvasError

logger = logging.getLogger(__name__)

def create_success_response(
    data: Any,
    message: str = "操作成功",
    status_code: int = 200
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码
        
    Returns:
        标准化的成功响应字典
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status_code": status_code
    }

def create_error_response(
    error_message: str,
    error_code: str = "UNKNOWN_ERROR",
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    创建错误响应
    
    Args:
        error_message: 错误消息
        error_code: 错误代码
        status_code: HTTP状态码
        details: 错误详情
        
    Returns:
        标准化的错误响应字典
    """
    response = {
        "success": False,
        "error": {
            "message": error_message,
            "code": error_code,
            "status_code": status_code
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response["error"]["details"] = details
    
    return response

def handle_moodcanvas_error(error: MoodCanvasError) -> JSONResponse:
    """
    处理MoodCanvas自定义异常
    
    Args:
        error: MoodCanvas异常对象
        
    Returns:
        FastAPI JSON响应
    """
    error_response = create_error_response(
        error_message=error.message,
        error_code=error.error_code or "MOODCANVAS_ERROR",
        status_code=400,
        details=error.details
    )
    
    logger.error(f"MoodCanvas异常: {error.message}", extra=error.details)
    return JSONResponse(content=error_response, status_code=400)

def handle_generic_error(error: Exception) -> JSONResponse:
    """
    处理通用异常
    
    Args:
        error: 异常对象
        
    Returns:
        FastAPI JSON响应
    """
    error_response = create_error_response(
        error_message=str(error),
        error_code="INTERNAL_SERVER_ERROR",
        status_code=500
    )
    
    logger.error(f"通用异常: {str(error)}", exc_info=True)
    return JSONResponse(content=error_response, status_code=500)

def create_paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """
    创建分页响应
    
    Args:
        data: 当前页数据
        total: 总数据量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
        
    Returns:
        分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size
    
    return create_success_response(
        data={
            "items": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        },
        message=message
    )

def create_file_response(
    file_path: str,
    file_name: str,
    file_size: int,
    mime_type: str = "application/octet-stream"
) -> Dict[str, Any]:
    """
    创建文件响应信息
    
    Args:
        file_path: 文件路径
        file_name: 文件名
        file_size: 文件大小（字节）
        mime_type: MIME类型
        
    Returns:
        文件响应信息字典
    """
    return create_success_response(
        data={
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "mime_type": mime_type,
            "download_url": f"/download/{file_name}"  # 假设有下载端点
        },
        message="文件处理成功"
    )

def create_processing_status_response(
    task_id: str,
    status: str,
    progress: Optional[float] = None,
    estimated_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    创建处理状态响应
    
    Args:
        task_id: 任务ID
        status: 任务状态
        progress: 进度百分比（0-100）
        estimated_time: 预估剩余时间（秒）
        
    Returns:
        状态响应字典
    """
    status_data = {
        "task_id": task_id,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if progress is not None:
        status_data["progress"] = min(100, max(0, progress))
    
    if estimated_time is not None:
        status_data["estimated_time_remaining"] = estimated_time
    
    return create_success_response(
        data=status_data,
        message="状态查询成功"
    )

def validate_response_data(data: Any, required_fields: list) -> bool:
    """
    验证响应数据是否包含必需字段
    
    Args:
        data: 要验证的数据
        required_fields: 必需字段列表
        
    Returns:
        是否验证通过
    """
    if not isinstance(data, dict):
        return False
    
    return all(field in data for field in required_fields)

def sanitize_response_data(data: Any) -> Any:
    """
    清理响应数据，移除敏感信息
    
    Args:
        data: 原始数据
        
    Returns:
        清理后的数据
    """
    if isinstance(data, dict):
        # 移除敏感字段
        sensitive_fields = {'password', 'token', 'secret', 'key', 'api_key'}
        cleaned_data = {}
        
        for key, value in data.items():
            if key.lower() not in sensitive_fields:
                cleaned_data[key] = sanitize_response_data(value)
        
        return cleaned_data
    
    elif isinstance(data, list):
        return [sanitize_response_data(item) for item in data]
    
    else:
        return data

def create_health_check_response(
    service_name: str,
    status: str = "healthy",
    version: str = "1.0.0",
    uptime: Optional[float] = None
) -> Dict[str, Any]:
    """
    创建健康检查响应
    
    Args:
        service_name: 服务名称
        status: 服务状态
        version: 服务版本
        uptime: 运行时间（秒）
        
    Returns:
        健康检查响应字典
    """
    health_data = {
        "service": service_name,
        "status": status,
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if uptime is not None:
        health_data["uptime_seconds"] = uptime
        health_data["uptime_formatted"] = format_uptime(uptime)
    
    return create_success_response(
        data=health_data,
        message="健康检查完成"
    )

def format_uptime(seconds: float) -> str:
    """
    格式化运行时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"
