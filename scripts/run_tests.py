#!/usr/bin/env python3
"""
测试运行脚本
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ 成功")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False

def check_dependencies():
    """检查依赖"""
    print("🔍 检查项目依赖...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查pytest
    try:
        import pytest
        print(f"✅ pytest版本: {pytest.__version__}")
    except ImportError:
        print("❌ pytest未安装")
        print("请运行: pip install pytest pytest-asyncio")
        return False
    
    # 检查项目结构
    project_root = Path(__file__).parent.parent
    required_dirs = ["src", "tests", "config"]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"❌ 缺少目录: {dir_name}")
            return False
    
    print("✅ 项目结构完整")
    return True

def run_unit_tests():
    """运行单元测试"""
    print("\n🧪 运行单元测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "-m", "unit",
        "--tb=short",
        "--maxfail=10"
    ]
    
    return run_command(cmd, "单元测试")

def run_model_tests():
    """运行模型测试"""
    print("\n🤖 运行模型测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_models.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "模型测试")

def run_service_tests():
    """运行服务测试"""
    print("\n🔧 运行服务测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_services.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "服务测试")

def run_api_tests():
    """运行API测试"""
    print("\n🌐 运行API测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_api.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "API测试")

def run_utils_tests():
    """运行工具函数测试"""
    print("\n🛠️ 运行工具函数测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_utils.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "工具函数测试")

def run_config_tests():
    """运行配置测试"""
    print("\n⚙️ 运行配置测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_config.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "配置测试")

def run_exception_tests():
    """运行异常处理测试"""
    print("\n🚨 运行异常处理测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_exceptions.py",
        "-v",
        "--tb=short",
        "--maxfail=5"
    ]
    
    return run_command(cmd, "异常处理测试")

def run_all_tests():
    """运行所有测试"""
    print("\n🚀 运行所有测试...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--maxfail=20",
        "--durations=10"
    ]
    
    return run_command(cmd, "所有测试")

def run_coverage():
    """运行覆盖率测试"""
    print("\n📊 运行覆盖率测试...")
    
    # 检查coverage是否安装
    try:
        import coverage
    except ImportError:
        print("❌ coverage未安装")
        print("请运行: pip install coverage")
        return False
    
    # 运行覆盖率测试
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    return run_command(cmd, "覆盖率测试")

def run_specific_test(test_path):
    """运行特定测试"""
    print(f"\n🎯 运行特定测试: {test_path}")
    
    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return False
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short"
    ]
    
    return run_command(cmd, f"特定测试: {test_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MoodCanvas测试运行器")
    parser.add_argument(
        "--type", 
        choices=["unit", "models", "services", "api", "utils", "config", "exceptions", "all"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="运行覆盖率测试"
    )
    parser.add_argument(
        "--test-file",
        help="运行特定测试文件"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="仅检查依赖，不运行测试"
    )
    
    args = parser.parse_args()
    
    print("🎨 MoodCanvas 测试运行器")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请解决上述问题后重试")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ 依赖检查完成")
        return
    
    # 运行测试
    success = True
    
    if args.test_file:
        success = run_specific_test(args.test_file)
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "models":
        success = run_model_tests()
    elif args.type == "services":
        success = run_service_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "utils":
        success = run_utils_tests()
    elif args.type == "config":
        success = run_config_tests()
    elif args.type == "exceptions":
        success = run_exception_tests()
    elif args.type == "all":
        success = run_all_tests()
    
    # 运行覆盖率测试
    if args.coverage and success:
        coverage_success = run_coverage()
        success = success and coverage_success
    
    # 输出结果
    print("\n" + "="*60)
    if success:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败，请检查上述错误")
        sys.exit(1)

if __name__ == "__main__":
    main()

