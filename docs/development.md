# MoodCanvas 开发指南

## 开发环境设置

### 1. 环境要求
- Python 3.12+
- 推荐使用虚拟环境

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境变量配置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，设置必要的环境变量
ARK_API_KEY=your_doubao_api_key_here
```

## 项目结构说明

### 核心模块
- **`src/core/`**: 核心功能模块，包含配置管理
- **`src/models/`**: AI模型模块，按功能分类
- **`src/services/`**: 业务服务层，协调多个模型
- **`src/api/`**: API接口层，提供RESTful接口
- **`src/utils/`**: 工具函数，通用功能

### 模型架构
每个模型类型都有基类设计：
- **`BaseASRModel`**: 语音识别模型基类
- **`BaseEmotionModel`**: 情感分析模型基类  
- **`BaseImageModel`**: 图像模型基类

### 数据目录
- **`src/data/models/`**: 本地模型文件
- **`data/input/`**: 输入文件
- **`data/output/`**: 输出文件
- **`data/temp/`**: 临时文件
- **`data/generated_images/`**: 生成的图像

## 开发流程

### 1. 添加新模型
```python
# 继承相应的基类
from src.models.asr.base import BaseASRModel

class NewASRModel(BaseASRModel):
    def load_model(self) -> bool:
        # 实现模型加载逻辑
        pass
    
    def transcribe(self, audio_path: str) -> Optional[str]:
        # 实现转录逻辑
        pass
```

### 2. 添加新API接口
```python
# 在src/api/v1/下创建新文件
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/new", tags=["new"])

@router.get("/")
async def new_endpoint():
    return {"message": "new endpoint"}
```

### 3. 添加新服务
```python
# 在src/services/下创建新服务
class NewService:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def process(self, data):
        # 实现业务逻辑
        pass
```

## 代码规范

### 1. 导入规范
- 使用绝对导入：`from src.core.config_manager import ConfigManager`
- 避免循环导入
- 在文件开头添加路径设置

### 2. 错误处理
- 使用统一的异常处理机制
- 返回标准化的错误响应
- 记录详细的错误日志

### 3. 配置管理
- 敏感信息使用环境变量
- 配置文件支持默认值
- 启动时验证配置有效性

## 测试

### 1. 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api/test_health.py
```

### 2. 测试结构
- **`tests/test_models/`**: 模型测试
- **`tests/test_services/`**: 服务测试
- **`tests/test_api/`**: API测试

## 部署

### 1. 开发环境
```bash
python scripts/start_server.py
```

### 2. 生产环境
```bash
# 使用gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 常见问题

### 1. 模块导入错误
- 检查Python路径设置
- 确保__init__.py文件存在
- 验证相对导入路径

### 2. 配置加载失败
- 检查配置文件路径
- 验证JSON格式
- 确认环境变量设置

### 3. 模型加载失败
- 检查模型文件路径
- 验证依赖包版本
- 查看错误日志

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 联系方式

如有问题，请查看：
- API文档：`/docs`
- 项目结构：`struct.md`
- 配置文件：`config/config.json`
