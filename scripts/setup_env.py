#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoodCanvas 环境设置脚本
"""
import os
import sys
from pathlib import Path
import shutil

def setup_environment():
    """设置项目环境"""
    print("🚀 开始设置 MoodCanvas 环境...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建必要的目录
    directories = [
        "src/data/models",
        "data/input", 
        "data/output",
        "data/temp",
        "data/generated_images",
        "logs"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 检查配置文件
    config_file = project_root / "config" / "config.json"
    if not config_file.exists():
        print("❌ 配置文件不存在: config/config.json")
        return False
    
    # 检查环境变量
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 ARK_API_KEY 环境变量")
        print("   请设置: export ARK_API_KEY=your_api_key")
    else:
        print("✅ 环境变量 ARK_API_KEY 已设置")
    
    # 检查Python依赖
    try:
        import fastapi
        print("✅ FastAPI 已安装")
    except ImportError:
        print("❌ FastAPI 未安装，请运行: pip install -r requirements.txt")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn 已安装")
    except ImportError:
        print("❌ Uvicorn 未安装，请运行: pip install -r requirements.txt")
        return False
    
    try:
        import volcenginesdkarkruntime
        print("✅ 豆包SDK 已安装")
    except ImportError:
        print("❌ 豆包SDK 未安装，请运行: pip install -r requirements.txt")
        return False
    
    print("\n🎉 环境设置完成！")
    print("\n📋 下一步:")
    print("1. 设置环境变量: export ARK_API_KEY=your_api_key")
    print("2. 启动服务: python scripts/start_server.py")
    print("3. 访问API文档: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
