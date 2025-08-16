#!/usr/bin/env python3
"""
MoodCanvas 启动脚本
在项目根目录运行此脚本即可启动应用
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 先加载环境变量
def load_environment():
    """加载环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        print(f"加载环境变量文件: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"设置环境变量: {key.strip()}")
    else:
        print("未找到.env文件，使用系统环境变量")

# 加载环境变量
load_environment()

# 导入并运行应用
from src.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
