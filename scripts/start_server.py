#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoodCanvas API 服务启动脚本
解决模块导入路径问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入并启动FastAPI应用
from src.main import app

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 MoodCanvas API 服务...")
    print(f"📁 项目根目录: {project_root}")
    print(f"🔧 Python路径: {sys.path[:3]}...")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "src")]
    )
