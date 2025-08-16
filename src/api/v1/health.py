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
        # CPU使用率
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_percent = float(cpu_percent) if cpu_percent is not None else 0.0
        except:
            cpu_percent = 0.0
        
        # 内存使用率
        try:
            memory = psutil.virtual_memory()
            memory_percent = float(memory.percent) if memory.percent is not None else 0.0
        except:
            memory_percent = 0.0
        
        # 磁盘使用率 - 使用更安全的方法
        disk_percent = 0.0
        disk_free_gb = 0.0
        
        try:
            # 尝试使用当前工作目录
            import os
            current_dir = os.getcwd()
            if current_dir:
                disk = psutil.disk_usage(current_dir)
                disk_percent = float(disk.percent) if disk.percent is not None else 0.0
                disk_free_gb = round(float(disk.free) / (1024**3), 2) if disk.free is not None else 0.0
        except:
            try:
                # 尝试使用根目录
                disk = psutil.disk_usage('/')
                disk_percent = float(disk.percent) if disk.percent is not None else 0.0
                disk_free_gb = round(float(disk.free) / (1024**3), 2) if disk.free is not None else 0.0
            except:
                # 如果都失败，使用默认值
                disk_percent = 0.0
                disk_free_gb = 0.0
        
        return {
            "status": "ok",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "disk_free_gb": disk_free_gb
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
            "src/data/models",
            "data/input", 
            "data/output",
            "data/temp",
            "data/generated_images"
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
