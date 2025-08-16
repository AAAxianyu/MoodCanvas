# MoodCanvas 项目架构文档

## 项目概述
MoodCanvas是一个智能情感内容生成系统，集成了多个先进AI模型，能够从文字或语音中提取情感信息，并自动生成相应的文案和图片内容。

## 当前项目结构

```
MoodCanvas/
├── README.md                       # 项目说明文档
├── pyproject.toml                 # 项目配置
├── uv.lock                        # 依赖锁定文件
├── .env.example                   # 环境变量模板
├── .gitignore
│
├── config/                         # 配置目录
│   ├── __init__.py
│   ├── settings.py                 # 配置管理
│   └── config.json                # 主配置文件
│
├── src/                           # 源代码根目录
│   ├── __init__.py
│   │
│   ├── core/                      # 核心功能模块
│   │   ├── __init__.py
│   │   ├── config_manager.py      # 配置管理器
│   │   └── exceptions.py          # 自定义异常
│   │
│   ├── models/                    # AI模型模块
│   │   ├── __init__.py
│   ├── asr/                       # 语音识别
│   │   │   ├── __init__.py
│   │   │   ├── paraformer.py      # Paraformer模型
│   │   │   └── base.py            # ASR基类
│   │   ├── emotion/               # 情感分析
│   │   │   ├── __init__.py
│   │   │   ├── text_emotion.py    # 文本情感分析
│   │   │   ├── audio_emotion.py   # 声学情感分析
│   │   │   └── base.py            # 情感分析基类
│   │   └── image/                 # 图像生成/编辑
│   │       ├── __init__.py
│   │       ├── text2image.py      # 文生图
│   │       ├── image2image.py     # 图生图
│   │       └── base.py            # 图像模型基类
│   │
│   ├── services/                  # 业务服务层
│   │   ├── __init__.py
│   │   ├── emotion_analyzer.py    # 三阶段情感分析服务
│   │   ├── image_service.py       # 图像服务
│   │   └── text_generator.py      # 🆕 文案生成服务
│   │
│   ├── api/                       # API接口层
│   │   ├── __init__.py
│   │   ├── v1/                    # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── emotion.py         # 情感分析接口（含纯文字输入）
│   │   │   ├── image.py           # 图像接口（含情感增强编辑）
│   │   │   └── health.py          # 健康检查
│   │   └── dependencies.py        # 依赖注入
│   │
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py          # 文件处理
│   │   ├── audio_utils.py         # 音频处理
│   │   └── response_utils.py      # 响应格式化
│   │
│   └── main.py                    # FastAPI应用入口
│
├── data/                          # 数据目录
│   ├── models/                    # 本地模型文件
│   │   ├── emotion2vec_plus_large/
│   │   ├── paraformer-zh/
│   │   └── distilbert-base-uncased-go-emotions-student/
│   ├── input/                     # 输入文件
│   ├── output/                    # 输出文件
│   ├── temp/                      # 临时文件
│   └── generated_images/          # 生成的图像
│
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── test_models/               # 模型测试
│   ├── test_services/             # 服务测试
│   └── test_api/                  # API测试
│
├── scripts/                       # 脚本目录
│   ├── start_server.py            # 启动脚本
│   ├── test_api.py                # API测试脚本
│   └── setup_env.py               # 环境设置脚本
│
└── docs/                          # 文档目录
    ├── api.md                     # API文档
    ├── deployment.md              # 部署指南
    └── development.md             # 开发指南
```

## 🆕 新增功能模块

### 1. 文案生成服务 (src/services/text_generator.py)
- **功能**: 基于情感标签调用第三方API生成富有感染力的文案
- **支持**: OpenAI GPT-3.5-turbo API
- **备用方案**: 当API不可用时，使用本地模板生成文案
- **特点**: 支持多种文案风格，情感标签驱动的个性化生成

### 2. 纯文字输入接口 (src/api/v1/emotion.py)
- **新增接口**: `POST /api/v1/emotion/analyze_text`
- **功能**: 直接输入文字进行情感分析，无需语音文件
- **流程**: 文字 → 情感分析 → 文案生成 → 图片生成
- **应用场景**: 社交媒体内容创作、营销文案生成等

### 3. 情感增强图片编辑 (src/api/v1/image.py)
- **增强功能**: 在原有图片编辑基础上，支持情感标签和原始文字
- **参数**: `emotion_tags`, `original_text`
- **效果**: 结合情感信息生成更精准的图片编辑结果
- **应用**: 基于情感状态的个性化图片修改

### 4. 图片重新编辑接口 (src/api/v1/image.py)
- **新增接口**: `POST /api/v1/images/reedit`
- **功能**: 纯图片修改，不涉及情感标签
- **场景**: 用户对返回结果不满意时的简单修改
- **特点**: 专注于图片技术参数调整

## 核心模块说明

### 1. 配置管理 (config/)
- **settings.py**: 集中管理所有配置，支持环境变量覆盖
- **config.json**: 默认配置文件，包含模型路径、API密钥、文案生成配置等

### 2. 模型层 (src/models/)
- **基类设计**: 每个模型类型都有基类，统一接口
- **模块化**: ASR、情感分析、图像生成分别独立
- **可扩展**: 易于添加新的模型类型

### 3. 服务层 (src/services/)
- **emotion_analyzer.py**: 三阶段情感分析服务（语音+文字）
- **image_service.py**: 图像生成和编辑服务
- **text_generator.py**: 🆕 文案生成服务，调用第三方API

### 4. API层 (src/api/)
- **版本控制**: 支持API版本管理
- **依赖注入**: 统一的依赖管理
- **响应格式**: 标准化的响应格式
- **新增接口**: 纯文字分析、情感增强编辑、图片重新编辑

### 5. 工具层 (src/utils/)
- **通用功能**: 文件处理、音频处理等
- **响应工具**: 统一的响应格式化
- **验证工具**: 输入验证和清理

## 系统架构流程

### 文字输入流程
```
用户文字 → 文本情感分析 → 情感标签提取 → 文案生成 → 图片生成 → 返回结果
```

### 语音输入流程
```
用户语音 → ASR转录 → 文本情感分析 → 声学情感分析 → 情感融合 → 文案生成 → 图片生成 → 返回结果
```

### 图片编辑流程
```
用户图片 + 提示词 + 情感标签 → 情感增强编辑 → 返回结果
```

### 图片重新编辑流程
```
用户图片 + 提示词 → 纯技术编辑 → 返回结果
```

## 配置说明

### 环境变量
```bash
# 豆包API密钥（图片生成）
export ARK_API_KEY="your_ark_api_key"

# OpenAI API密钥（文案生成）
export OPENAI_API_KEY="your_openai_api_key"
```

### 配置文件结构
```json
{
  "text_generation": {
    "use_api": true,
    "provider": "openai",
    "model_name": "gpt-3.5-turbo"
  },
  "image_models": {
    "t2i": {
      "provider": "doubao",
      "model_name": "doubao-seedream-3-0-t2i-250415"
    },
    "i2i": {
      "provider": "doubao",
      "model_name": "doubao-seededit-3-0-i2i-250628"
    }
  }
}
```

## 启动方式

### 开发环境
```bash
# 从项目根目录启动
python scripts/start_server.py

# 或者直接启动
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产环境
```bash
# 使用gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 优势

1. **完整的业务流程**: 从情感分析到内容生成的完整链路
2. **多模态输入支持**: 文字和语音两种输入方式
3. **智能内容生成**: 基于情感的文案和图片自动生成
4. **灵活的图片编辑**: 支持情感增强和纯技术编辑
5. **清晰的层次结构**: 配置、模型、服务、API分离
6. **模块化设计**: 每个功能模块独立，易于维护
7. **易于扩展**: 新功能可以按模块添加
8. **便于测试**: 每个模块都可以独立测试
9. **部署友好**: 支持不同的部署方式

## 注意事项

1. **环境变量**: 敏感信息使用环境变量，不要硬编码
2. **错误处理**: 统一的异常处理机制
3. **日志记录**: 完善的日志系统
4. **配置验证**: 启动时验证配置有效性
5. **依赖管理**: 清晰的依赖关系，避免循环依赖
6. **API密钥管理**: 确保第三方API密钥的安全性
7. **备用方案**: 当第三方API不可用时的降级处理

## 未来扩展方向

1. **更多文案生成服务**: 支持Claude、Gemini等AI模型
2. **情感标签扩展**: 支持更细粒度的情感分类
3. **内容风格定制**: 支持不同行业和场景的内容风格
4. **批量处理**: 支持批量内容生成
5. **用户反馈学习**: 基于用户反馈优化生成质量

这个架构设计遵循了Python项目的最佳实践，让代码更清晰、更易维护，同时提供了完整的智能情感内容生成能力。
