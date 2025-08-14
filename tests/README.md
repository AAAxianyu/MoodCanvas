# MoodCanvas 测试文档

## 概述

本项目包含完整的测试套件，覆盖了各个模块的功能测试。测试采用pytest框架，支持单元测试、集成测试和API测试。

## 测试结构

```
tests/
├── conftest.py              # pytest配置文件
├── test_api.py              # API层测试
├── test_services.py         # 服务层测试
├── test_models.py           # 模型层测试
├── test_utils.py            # 工具函数测试
├── test_config.py           # 配置管理测试
├── test_exceptions.py       # 异常处理测试
└── README.md                # 本文件
```

## 测试分类

### 1. 单元测试 (Unit Tests)
- **标记**: `@pytest.mark.unit`
- **范围**: 单个函数、类或模块的独立测试
- **文件**: 所有测试文件

### 2. 模型测试 (Model Tests)
- **标记**: `@pytest.mark.models`
- **范围**: AI模型的加载、推理和输出验证
- **文件**: `test_models.py`

### 3. 服务测试 (Service Tests)
- **标记**: `@pytest.mark.services`
- **范围**: 业务逻辑层的功能测试
- **文件**: `test_services.py`

### 4. API测试 (API Tests)
- **标记**: `@pytest.mark.api`
- **范围**: FastAPI接口的请求响应测试
- **文件**: `test_api.py`

### 5. 工具函数测试 (Utils Tests)
- **标记**: `@pytest.mark.utils`
- **范围**: 辅助函数的正确性测试
- **文件**: `test_utils.py`

## 运行测试

### 前置条件

1. **Python版本**: 3.8+
2. **依赖安装**:
   ```bash
   pip install pytest pytest-asyncio pytest-cov
   ```

### 使用测试运行器脚本

```bash
# 运行所有测试
python scripts/run_tests.py

# 运行特定类型测试
python scripts/run_tests.py --type models
python scripts/run_tests.py --type services
python scripts/run_tests.py --type api

# 运行覆盖率测试
python scripts/run_tests.py --coverage

# 仅检查依赖
python scripts/run_tests.py --check-only

# 运行特定测试文件
python scripts/run_tests.py --test-file tests/test_models.py
```

### 直接使用pytest

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_models.py -v

# 运行特定标记的测试
pytest tests/ -m models -v
pytest tests/ -m services -v

# 运行覆盖率测试
pytest tests/ --cov=src --cov-report=html

# 并行运行测试
pytest tests/ -n auto
```

## 测试数据

### 模拟数据 (Mock Data)

测试使用模拟数据避免对外部服务的依赖：

- **配置数据**: 模拟的配置文件和环境变量
- **模型输出**: 模拟的AI模型推理结果
- **API响应**: 模拟的HTTP响应
- **文件数据**: 模拟的图片和音频文件

### 临时文件

测试过程中会创建临时文件，测试完成后自动清理：

- 临时配置文件
- 临时音频/图片文件
- 临时目录

## 测试覆盖

### 核心功能

- ✅ 配置管理
- ✅ 异常处理
- ✅ 文件验证
- ✅ 音频处理
- ✅ 图片处理
- ✅ 响应格式化

### 模型功能

- ✅ 文本情感分析
- ✅ 音频情感分析
- ✅ 语音识别
- ✅ 图片生成
- ✅ 图片编辑

### 服务功能

- ✅ 情感分析服务
- ✅ 图片处理服务
- ✅ 错误处理
- ✅ 数据验证

### API功能

- ✅ 接口响应
- ✅ 参数验证
- ✅ 错误处理
- ✅ 文件上传

## 测试最佳实践

### 1. 测试命名

```python
def test_function_name_scenario():
    """测试函数名_场景"""
    # 测试代码
    pass
```

### 2. 测试结构

```python
def test_function_name():
    """测试描述"""
    # Arrange - 准备测试数据
    input_data = "test"
    
    # Act - 执行被测试的功能
    result = function_to_test(input_data)
    
    # Assert - 验证结果
    assert result == "expected"
```

### 3. 使用Fixture

```python
@pytest.fixture
def sample_data():
    """示例数据"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """使用fixture的测试"""
    assert sample_data["key"] == "value"
```

### 4. 异常测试

```python
def test_function_raises_exception():
    """测试函数抛出异常"""
    with pytest.raises(ValueError, match="错误信息"):
        function_that_raises_error()
```

### 5. 模拟外部依赖

```python
@patch('module.external_function')
def test_with_mock(mock_external):
    """使用模拟的测试"""
    mock_external.return_value = "mocked_result"
    result = function_under_test()
    assert result == "mocked_result"
```

## 持续集成

### GitHub Actions

项目配置了GitHub Actions自动测试：

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src
```

### 本地开发

开发过程中建议：

1. **频繁运行测试**: 每次修改后运行相关测试
2. **使用覆盖率**: 确保新代码有足够的测试覆盖
3. **测试驱动开发**: 先写测试，再写实现

## 故障排除

### 常见问题

1. **导入错误**
   - 确保项目根目录在Python路径中
   - 检查`conftest.py`中的路径配置

2. **依赖缺失**
   - 安装pytest: `pip install pytest`
   - 安装异步支持: `pip install pytest-asyncio`

3. **测试失败**
   - 检查测试环境配置
   - 验证模拟数据是否正确
   - 查看详细的错误信息

### 调试技巧

1. **详细输出**: 使用`-v`参数获取详细信息
2. **失败时停止**: 使用`--maxfail=1`在第一个失败时停止
3. **显示本地变量**: 使用`--tb=long`显示更多调试信息
4. **交互式调试**: 使用`pytest --pdb`在失败时进入调试器

## 贡献指南

### 添加新测试

1. 为新功能创建测试文件
2. 遵循现有的测试命名规范
3. 使用适当的测试标记
4. 确保测试覆盖率

### 测试代码审查

- 测试是否覆盖了所有边界情况
- 测试是否独立且可重复
- 测试名称是否清晰描述测试目的
- 是否使用了适当的模拟和fixture

## 联系方式

如有测试相关问题，请：

1. 查看测试输出和错误信息
2. 检查项目配置和依赖
3. 提交Issue描述问题
4. 参与项目讨论和改进



