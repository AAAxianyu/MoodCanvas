#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量加载测试脚本
验证.env文件是否正确加载到环境变量中
"""
import os
import sys
from pathlib import Path

def test_env_loading():
    """测试环境变量加载"""
    print("🧪 测试环境变量加载")
    print("=" * 40)
    
    # 检查.env文件是否存在
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env文件不存在")
        print("请确保在项目根目录运行此脚本")
        return False
    
    print(f"✅ 找到.env文件: {env_file}")
    
    # 读取.env文件内容
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    env_vars[key] = value
                    print(f"   📝 第{line_num}行: {key} = {value[:10]}...")
                except Exception as e:
                    print(f"   ❌ 第{line_num}行解析失败: {line} - {e}")
    
    print(f"\n📊 从.env文件读取到 {len(env_vars)} 个环境变量")
    
    # 检查关键环境变量
    required_vars = ["ARK_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if var in env_vars:
            value = env_vars[var]
            if value and value != "your_actual_key_here":
                print(f"   ✅ {var}: 已设置 (长度: {len(value)})")
            else:
                print(f"   ⚠️  {var}: 已设置但值为默认值")
                missing_vars.append(var)
        else:
            print(f"   ❌ {var}: 未设置")
            missing_vars.append(var)
    
    # 尝试加载到环境变量
    print(f"\n🔄 尝试加载环境变量到os.environ...")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   ✅ 设置 {key} = {value[:10]}...")
    
    # 验证环境变量是否设置成功
    print(f"\n🔍 验证环境变量设置...")
    for var in required_vars:
        env_value = os.environ.get(var)
        if env_value:
            print(f"   ✅ {var}: 环境变量已设置 (长度: {len(env_value)})")
        else:
            print(f"   ❌ {var}: 环境变量未设置")
    
    if missing_vars:
        print(f"\n⚠️  警告: 以下环境变量需要设置:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print(f"\n🎉 环境变量加载测试完成！")
    return True

def main():
    """主函数"""
    print("🚀 MoodCanvas 环境变量加载测试")
    print("=" * 50)
    
    success = test_env_loading()
    
    if success:
        print("\n✅ 所有测试通过！")
        print("现在可以运行其他测试了:")
        print("   python tests/run_api_tests.py")
        print("   pytest tests/test_integration_api.py -v")
    else:
        print("\n❌ 测试失败，请检查.env文件配置")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
