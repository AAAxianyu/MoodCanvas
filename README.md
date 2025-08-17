# 🎭 MoodCanvas - 智能情感内容生成系统

这是一个集成了多个先进AI模型的情感分析和内容生成系统，能够从文字、语音或图片中提取情感信息，并自动生成相应的文案和图片内容。

## 🚀 系统架构

### 核心功能模块

1. **📝 文字情感分析** - 纯文字输入，情感分析 + 文案生成 + 图片生成
2. **🎵 语音情感分析** - 三阶段处理：ASR + 文本情感 + 声学情感 + 内容生成
3. **🖼️ 图片情感分析** - 基于图片内容的情感识别和风格分析
4. **🔄 多模态融合分析** - 支持图片、文字、语音三者任意组合的情感分析
5. **✍️ 智能内容生成** - 基于情感标签的文案和图片生成

### 技术架构

1. **📝 阶段1: ASR 语音转文字 (Paraformer-zh)**
   - 使用 FunASR 框架的 Paraformer-zh 模型
   - 专门针对中文语音识别优化
   - 支持16kHz采样率的音频输入
   - 本地模型，无需网络连接

2. **💭 阶段2: 文本情感分类 (中文情感分类)**
   - 使用 DistilBERT 模型进行文本情感分析
   - 支持多种情感类别识别
   - 本地模型，无需网络连接
   - 对转录文本进行情感分析

3. **🎵 阶段3: 声学情感分析 (emotion2vec)**
   - 直接从音频波形中识别情感
   - 支持9种情感类别
   - 跨语言通用，不受语言限制
   - 本地模型，无需网络连接

4. **🖼️ 图片情感分析**
   - 基于图片内容的视觉情感识别
   - 支持多种视觉风格分析
   - 与文本和语音情感结果融合

## 📋 功能特性

### 🆕 新增功能

- **多模态融合分析** - 支持图片、文字、语音三者任意组合的情感分析
- **统一分析接口** - `/analyze_multi` 接口支持灵活的多模态输入
- **智能内容生成** - 基于融合情感标签自动生成文案和匹配图片
- **情感增强图片编辑** - 结合情感标签和原始文字进行图片编辑
- **图片重新编辑** - 用户不满意时的纯图片修改（不涉及情感标签）

### ✅ 核心功能

- **多模态输入** - 支持文字、语音和图片三种输入方式
- **三阶段分析** - ASR转录 → 文本情感 → 声学情感
- **情感融合** - 智能融合多种情感分析结果
- **内容生成** - 自动生成文案和匹配的图片
- **完全本地化** - 核心模型本地运行，无网络依赖
- **配置驱动** - 通过配置文件统一管理所有设置
- **前端界面** - 提供抖音小程序前端界面

## 🛠️ 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 手动安装核心依赖
pip install torch torchaudio transformers funasr modelscope fastapi uvicorn pillow numpy scipy
```

## 🎯 使用方法

### API路由概览

| 路由 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/v1/emotion/analyze_multi` | POST | 多模态情感分析 | `image_file`, `text`, `audio_file` |
| `/api/v1/emotion/analyze_text` | POST | 文本情感分析 | `text` |
| `/api/v1/emotion/analyze` | POST | 语音情感分析 | `audio_file` |
| `/api/v1/images/generate` | POST | 文本生成图片 | `prompt`, `size`, `save_local` |
| `/api/v1/images/edit` | POST | 情感增强图片编辑 | `image`, `prompt`, `emotion_tags`, `original_text` |
| `/api/v1/images/reedit` | POST | 图片重新编辑 | `image`, `prompt` |
| `/api/v1/health` | GET | 服务健康检查 | - |

### 启动服务

```bash
# 启动FastAPI服务
python run.py
```

### API接口使用

#### 1. 多模态情感分析

```bash
curl -X POST "http://localhost:8000/api/v1/emotion/analyze_multi" \
  -F "text=今天天气真好，心情很愉快" \
  -F "audio_file=@your_audio.wav" \
  -F "image_file=@your_image.jpg"
```

**返回结果：**
```json
{
  "image_content": {
    "styles": ["warm", "bright"],
    "caption": "阳光明媚的户外场景"
  },
  "audio": {
    "transcribed_text": "今天天气真好，心情很愉快",
    "emotion_analysis": {
      "merged_emotion": ["joy", "optimism"]
    }
  },
  "text": {
    "emotion_analysis": {
      "text_emotion": ["joy", "optimism"]
    }
  },
  "emotion_tags": ["warm", "bright", "joy", "optimism"],
  "generated_text": "在温暖明亮的氛围中，今天天气真好，心情很愉快...",
  "generated_image_url": "/static/generated/xxx.png"
}
```

#### 2. 纯文本情感分析

```bash
curl -X POST "http://localhost:8000/api/v1/emotion/analyze_text" \
  -H "Content-Type: application/json" \
  -d '{"text": "今天天气真好，心情很愉快"}'
```

#### 3. 语音情感分析

```bash
curl -X POST "http://localhost:8000/api/v1/emotion/analyze" \
  -F "audio_file=@your_audio.wav"
```

#### 4. 图片生成

```bash
curl -X POST "http://localhost:8000/api/v1/images/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "一只可爱的小猫在花园里玩耍",
    "size": "1024x1024",
    "save_local": true
  }'
```

#### 5. 情感增强图片编辑

```bash
curl -X POST "http://localhost:8000/api/v1/images/edit" \
  -F "image=@input_image.jpg" \
  -F "prompt=让图片更加温暖明亮" \
  -F "emotion_tags=happy,warm" \
  -F "original_text=今天心情很好"
```

#### 6. 图片重新编辑（不涉及情感）

```bash
curl -X POST "http://localhost:8000/api/v1/images/reedit" \
  -F "image=@input_image.jpg" \
  -F "prompt=调整图片的色调和对比度"
```

## 🎨 前端界面

项目包含完整的字节跳动小程序前端界面，支持：

- **聊天界面** - 文字输入和语音录制
- **图片发送** - 相机拍照和相册选择
- **实时预览** - 生成内容的即时展示
- **响应式设计** - 适配不同设备尺寸


## ⚙️ 配置说明

### 环境变量

```bash
# 豆包API密钥（图片生成）
export ARK_API_KEY="your_ark_api_key"

# OpenAI API密钥（文案生成）
export OPENAI_API_KEY="your_openai_api_key"
```

### 配置文件 (config/config.json)

```json
{
  "text_generation": {
    "use_api": true,
    "provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "api": {
      "base_url": "https://api.openai.com/v1",
      "api_key_env": "OPENAI_API_KEY"
    }
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
  },
  "paths": {
    "temp_dir": "data/temp",
    "generated_images_dir": "data/generated_images",
    "static_url_prefix": "/static/generated"
  }
}
```

## 🔧 技术细节

### 情感分析模型

#### emotion2vec (9类情感)
- angry, disgusted, fearful, happy, neutral, other, sad, surprised, unknown

#### DistilBERT (28类情感)
- admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral

### 内容生成流程

1. **多模态输入** → 支持图片、文字、语音任意组合
2. **情感分析** → 提取并融合多种情感标签
3. **文案生成** → 调用第三方API生成文案
4. **图片生成** → 基于情感标签和文案生成匹配图片
5. **结果融合** → 返回完整的文案+图片内容

### 项目结构

```
MoodCanvasV1/
├── src/                    # 核心源代码
│   ├── api/               # API接口层
│   ├── core/              # 核心配置和异常处理
│   ├── models/            # AI模型实现
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   └── frontend/          # 字节跳动小程序前端
├── config/                # 配置文件
├── data/                  # 数据目录
├── scripts/               # 运行脚本
└── tests/                 # 测试代码
```

## 🚨 故障排除

### 常见问题

1. **API密钥未设置**
   - 检查环境变量是否正确设置
   - 确认配置文件中的API配置

2. **模型加载失败**
   - 检查本地模型文件是否完整
   - 确认配置文件中的路径设置

3. **图片生成失败**
   - 检查豆包API密钥是否有效
   - 确认网络连接正常

4. **前端界面问题**
   - 确认字节跳动开发者工具版本
   - 检查小程序配置是否正确

## 🔄 扩展功能

### 添加新的文案生成服务

```python
# 在 src/services/text_generator.py 中添加新服务
class NewTextGenerator(TextGenerator):
    async def _call_custom_api(self, prompt: str) -> str:
        # 实现自定义API调用
        pass
```

### 自定义情感标签映射

```python
# 在配置文件中添加新的情感标签
"custom_emotions": {
    "custom_label": "自定义情感描述"
}
```

### 添加新的图片模型

```python
# 在 src/models/image/ 中添加新模型
class NewImageModel(BaseImageModel):
    async def generate(self, prompt: str, **kwargs) -> str:
        # 实现图片生成逻辑
        pass
```

## 🎯 使用场景

- **内容创作** - 基于情感自动生成文案和配图
- **社交媒体** - 智能生成符合情感状态的内容
- **营销推广** - 根据用户情感生成个性化营销内容
- **教育应用** - 分析学习者的情感状态并生成相应内容
- **心理健康** - 通过内容生成帮助用户调节情绪

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个系统！

## 📄 许可证

本项目基于MIT许可证开源。

## 🙏 致谢

- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 语音识别框架
- [emotion2vec](https://github.com/ddlBoJack/emotion2vec) - 音频情感识别
- [Hugging Face](https://huggingface.co/) - 模型库和工具
- [ModelScope](https://www.modelscope.cn/) - 模型托管平台
- [达摩院](https://damo.alibaba.com/) - Paraformer模型
- [豆包](https://www.doubao.com/) - 图片生成服务
- [OpenAI](https://openai.com/) - 文案生成服务
- [字节跳动](https://developer.toutiao.com/) - 小程序开发平台
