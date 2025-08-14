# 大模型API测试说明

本文档说明如何运行和配置大模型API测试。

## 测试文件说明

### 1. `test_large_model_api.py` - 单元测试
- **用途**: 测试大模型API调用的核心逻辑
- **特点**: 使用Mock模拟API调用，不消耗真实API配额
- **适用场景**: 开发阶段、CI/CD、快速验证逻辑

### 2. `test_integration_api.py` - 集成测试
- **用途**: 测试真实的大模型API调用
- **特点**: 需要有效的API密钥，会消耗API配额
- **适用场景**: 部署前验证、API功能确认

### 3. `run_api_tests.py` - 快速测试脚本
- **用途**: 快速检查配置和环境变量
- **特点**: 轻量级，适合日常检查

## 运行测试

### 前置条件
1. 确保已安装pytest: `pip install pytest`
2. 设置环境变量（见下文）

### 快速开始
```bash
# 1. 检查环境配置
python tests/run_api_tests.py

# 2. 运行单元测试（推荐）
pytest tests/test_large_model_api.py -v

# 3. 运行集成测试（需要API密钥）
pytest tests/test_integration_api.py -v

# 4. 运行所有测试
pytest tests/ -v
```

## 环境变量配置

### 必需的环境变量
```bash
# 豆包API密钥（用于图片生成和编辑）
export ARK_API_KEY="your_doubao_api_key_here"

# OpenAI API密钥（用于文本生成）
export OPENAI_API_KEY="sk-your_openai_api_key_here"
```

### 创建.env文件
在项目根目录创建`.env`文件：
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，填入真实的API密钥
ARK_API_KEY=your_actual_doubao_api_key
OPENAI_API_KEY=sk-your_actual_openai_api_key
```

## 测试用例说明

### 单元测试用例
1. **豆包图片编辑API测试** - 验证图片编辑功能
2. **豆包文本生成图片API测试** - 验证文本生成图片功能
3. **OpenAI文本生成API测试** - 验证文本生成功能
4. **API密钥验证测试** - 验证密钥配置
5. **API错误处理测试** - 验证异常处理
6. **本地文件处理测试** - 验证文件上传功能

### 集成测试用例
1. **真实API调用测试** - 测试豆包图片编辑
2. **真实API调用测试** - 测试豆包文本生成图片
3. **配置检查测试** - 验证API配置
4. **环境变量测试** - 检查环境设置

## 故障排除

### 常见问题

#### 1. 环境变量未加载
```bash
# 检查.env文件是否存在
ls -la .env

# 手动设置环境变量
export ARK_API_KEY="your_key"
```

#### 2. API调用失败
- 检查API密钥是否有效
- 检查网络连接
- 检查API配额是否充足

#### 3. 导入错误
```bash
# 确保在项目根目录运行
cd /path/to/MoodCanvas
python tests/run_api_tests.py
```

### 调试技巧

#### 1. 启用详细日志
```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 运行测试时显示详细输出
pytest tests/test_integration_api.py -v -s
```

#### 2. 单独测试特定用例
```bash
# 测试特定方法
pytest tests/test_integration_api.py::TestIntegrationAPI::test_doubao_image_edit_real_api -v

# 测试特定类
pytest tests/test_large_model_api.py::TestLargeModelAPI -v
```

## 测试最佳实践

### 1. 开发阶段
- 优先使用单元测试（Mock）
- 快速验证逻辑正确性
- 不消耗API配额

### 2. 部署前
- 运行集成测试
- 验证真实API功能
- 确认配置正确性

### 3. 持续集成
- 自动化运行单元测试
- 定期运行集成测试
- 监控API调用状态

## 扩展测试

### 添加新的API测试
1. 在`test_large_model_api.py`中添加Mock测试
2. 在`test_integration_api.py`中添加真实API测试
3. 更新测试配置和依赖

### 自定义测试配置
```python
# 在测试类中添加自定义配置
@pytest.fixture
def custom_config(self):
    return {
        "custom_model": {
            "api_key": "test_key",
            "endpoint": "https://api.example.com"
        }
    }
```

## 联系支持

如果遇到测试问题：
1. 检查环境变量配置
2. 查看测试日志输出
3. 确认API密钥有效性
4. 检查网络连接状态
