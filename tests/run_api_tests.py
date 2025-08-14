#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API测试运行脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_environment():
    """加载环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        print(f"📁 找到.env文件: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"   ✅ 设置环境变量: {key.strip()}")
        print()
    else:
        print("❌ 未找到.env文件")
        print("请确保在项目根目录运行此脚本，并且.env文件存在")
        print()

def main():
    """主函数"""
    print("🚀 MoodCanvas 大模型API测试")
    print("=" * 50)
    
    # 首先加载.env文件
    print("📋 加载环境变量...")
    load_environment()
    
    # 检查环境变量
    print("📋 环境变量检查:")
    ark_key = os.environ.get("ARK_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if ark_key:
        print(f"   ✅ ARK_API_KEY: {ark_key[:10]}... (长度: {len(ark_key)})")
    else:
        print("   ❌ ARK_API_KEY: 未设置")
    
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY: {openai_key[:10]}... (长度: {len(openai_key)})")
    else:
        print("   ❌ OPENAI_API_KEY: 未设置")
    
    print()
    
    # 运行快速测试
    print("🧪 运行快速测试...")
    try:
        from tests.test_integration_api import run_quick_test
        if run_quick_test():
            print("\n🎉 快速测试通过！")
            print("\n📝 下一步:")
            print("   1. 运行单元测试: pytest tests/test_large_model_api.py -v")
            print("   2. 运行集成测试: pytest tests/test_integration_api.py -v")
            print("   3. 运行所有测试: pytest tests/ -v")
        else:
            print("\n💥 快速测试失败，请检查配置")
    except ImportError as e:
        print(f"❌ 导入测试模块失败: {e}")
        print("请确保在项目根目录运行此脚本")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")


if __name__ == "__main__":
    main()
