"""
健康检查API
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import os

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("/")
async def health_check():
    """基础健康检查"""
    return {
        "status": "ok",
        "service": "MoodCanvas API",
        "version": "2.0.0"
    }

@router.get("/system")
async def system_health():
    """系统资源健康检查"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "ok",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/models")
async def models_health():
    """模型健康检查"""
    try:
        # 检查关键目录是否存在
        required_dirs = [
            "data/models",
            "data/input", 
            "data/output",
            "data/temp"
        ]
        
        dir_status = {}
        for dir_path in required_dirs:
            dir_status[dir_path] = os.path.exists(dir_path)
        
        return {
            "status": "ok",
            "directories": dir_status
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
