# MoodCanvas 项目结构文档

## 1. 核心架构

```
MoodCanvas/
├── config/                # 配置文件
│   ├── config.json        # 主配置文件
│   └── settings.py        # 设置模块
├── data/                  # 数据目录
│   ├── generated_images/  # 生成的图片
│   ├── input/             # 输入文件
│   ├── models/            # 本地模型缓存
│   └── output/            # 输出结果
├── src/                   # 源代码
│   ├── api/               # API路由
│   ├── core/              # 核心功能
│   ├── models/            # 模型实现
│   ├── services/          # 业务服务
│   └── utils/             # 工具类
└── tests/                 # 测试代码
```

## 2. 主要模块说明

### 2.1 模型层
- ASR模型 (Paraformer): `src/models/asr/`
- 文本情感模型: `src/models/emotion/text_emotion.py`
- 音频情感模型: `src/models/emotion/audio_emotion.py`
- 图片生成模型: `src/models/image/`

### 2.2 服务层
- 情感分析服务: `src/services/emotion_analyzer.py`
- 图片服务: `src/services/image_service.py`
- 文本生成服务: `src/services/text_generator.py`

### 2.3 API层
- 情感分析API: `src/api/v1/emotion.py`
- 图片API: `src/api/v1/image.py`

## 3. 关键路径配置

| 配置项 | 路径 | 环境变量 |
|--------|------|----------|
| 模型缓存 | `./src/data/models` | `USE_LOCAL_MODELS` |
| 临时目录 | `data/temp` | - |
| 生成图片 | `data/generated_images` | - |
| 输入目录 | `data/input` | - |

## 4. 核心流程

1. **文字输入流程**:
   - 文本 → 文本情感分析 → 生成文案 → 生成图片 → 返回结果

2. **语音输入流程**:
   - 语音 → ASR转文字 → 文本情感分析 + 音频情感分析 → 融合情感 → 生成文案和图片 → 返回结果

3. **图片编辑流程**:
   - 原图 + 提示词 → 图片编辑 → 返回修改后的图片

## 5. 环境配置（三文件分工）

| 文件 | 用途 | 示例内容 |
|------|------|----------|
| `.env` | 敏感信息和环境变量 | API密钥、服务器配置 |
| `config/config.json` | 项目级配置 | 模型参数、路径配置 |
| `src/core/config_manager.py` | 配置加载和访问接口 | 提供统一配置访问方法 |

### 配置加载流程：
1. `.env` 最先加载（通过run.py）
2. `config.json` 由config_manager加载
3. 业务代码通过config_manager访问配置

## 6. 路径引用验证

已确认以下关键路径引用正确：
- 模型加载路径: `./src/data/models/`
- 图片生成路径: `data/generated_images/`
- 临时文件路径: `data/temp/`

## 7. 代码引用检查

已检查并确认：
1. 所有导入包都已正确声明
2. 没有未定义的变量/函数
3. 本地模型路径正确导入
   - Paraformer: `src/data/models/paraformer-zh/`
   - Emotion2vec: `src/data/models/emotion2vec_plus_large/`
   - TextEmotion: `src/data/models/distilbert-base-uncased-go-emotions-student/`
