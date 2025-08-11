# 🎭 三阶段多模型情感分析系统

这是一个集成了三个先进AI模型的情感分析系统，能够从音频中提取多种情感信息，实现语音转文字、文本情感分析和声学情感分析的三阶段处理流程。

## 🚀 系统架构

### 三阶段处理流程

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

## 📋 功能特性

- **三阶段分析**: ASR转录 → 文本情感 → 声学情感
- **完全本地化**: 所有模型都从本地加载，无网络依赖
- **配置驱动**: 通过 `config.json` 统一管理所有设置
- **结果对比**: 可以比较文本与声学情感分析结果
- **详细输出**: 生成包含时间戳的JSON格式分析报告
- **错误处理**: 单个阶段失败不影响其他阶段运行
- **中文优化**: 专门针对中文语音和文本优化

## 🛠️ 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者手动安装核心依赖
pip install torch torchaudio transformers funasr modelscope
```

## 🎯 使用方法

### 基本使用

```bash
python app.py
```

### 自定义音频文件

修改 `config.json` 中的音频文件设置：

```json
{
  "audio_files": {
    "default": "your_audio.wav",
    "available": ["your_audio.wav", "other_audio.wav"]
  }
}
```

### 切换模型模式

在 `config.json` 中修改模型设置：

```json
{
  "settings": {
    "use_local_models": true,  // true: 使用本地模型, false: 使用在线模型
    "download_to_project": true
  }
}
```

## 📁 项目结构

```
MoodCanvas/
├── app.py                          # 主程序文件
├── config.json                     # 配置文件
├── requirements.txt                # 依赖列表
├── README.md                       # 项目说明
├── input/                          # 音频输入目录
│   ├── asr_example.wav            # Paraformer-zh示例音频
│   ├── 111.wav                    # 测试音频
│   ├── hive-0001.wav              # 测试音频
│   └── test.wav                   # 测试音频
├── outputs/                        # 分析结果输出目录
├── temp_outputs/                   # 临时输出目录
├── models_cache/                   # 模型缓存目录
├── paraformer-zh/                  # Paraformer-zh本地模型
│   ├── model.pt                    # 模型权重文件
│   ├── tokens.json                 # 词汇表
│   ├── config.yaml                 # 模型配置
│   └── am.mvn                      # 声学模型统计
├── emotion2vec_plus_large/         # emotion2vec本地模型
└── distilbert-base-uncased-go-emotions-student/  # DistilBERT本地模型
```

## 📊 输出格式

系统会在 `outputs/` 目录下生成JSON格式的分析报告：

```
outputs/
└── emotion_analysis_20250811_222347.json
```

### 报告内容结构

```json
{
  "audio_file": "input/asr_example.wav",
  "timestamp": "2025-08-11T22:23:47",
  "stages": {
    "asr": {
      "status": "success",
      "transcription": "欢迎大家来体验达摩院推出的语音识别模型"
    },
    "text_emotion": {
      "status": "success",
      "emotions": [
        {"label": "caring", "confidence": 0.05494700372219086}
      ]
    },
    "audio_emotion": {
      "status": "success",
      "emotions": [
        {"label": "开心/happy", "confidence": 0.21698470413684845},
        {"label": "<unk>", "confidence": 0.1683637946844101}
      ]
    }
  },
  "summary": {
    "overall_status": "success",
    "key_findings": [
      "语音内容: 欢迎大家来体验达摩院推出的语音识别模型",
      "文本与声学情感分析结果对比"
    ],
    "recommendations": [
      "建议结合两种分析结果进行综合判断"
    ]
  }
}
```

## 🔧 技术细节

### 音频要求
- **采样率**: 16kHz (Paraformer-zh要求)
- **格式**: WAV, MP3, FLAC等常见格式
- **时长**: 建议1秒-30秒
- **语言**: 主要支持中文语音

### 情感类别

#### emotion2vec (9类)
- 生气/angry, 厌恶/disgusted, 恐惧/fearful
- 开心/happy, 中立/neutral, 其他/other
- 难过/sad, 吃惊/surprised, <unk>

#### DistilBERT (GoEmotions数据集)
- 包含27种情感类别
- 如: joy, sadness, anger, fear, surprise, caring等

## 🚨 故障排除

### 常见问题

1. **模型加载失败**
   - 检查本地模型文件是否完整
   - 确认 `config.json` 中的路径设置正确
   - 确保 `use_local_models: true`

2. **ASR 转录结果为空**
   - 检查音频文件质量
   - 确认音频格式和采样率
   - 尝试使用 `asr_example.wav` 测试

3. **音频处理错误**
   - 确认音频文件格式支持
   - 检查音频文件是否损坏
   - 验证采样率要求

### 错误日志示例

系统会显示详细的错误信息，帮助诊断问题：

```
❌ 阶段1: Paraformer-zh ASR 模型加载失败: [错误详情]
❌ 阶段2: 中文文本情感分类模型加载失败: [错误详情]
❌ 阶段3: emotion2vec 声学情感分析模型加载失败: [错误详情]
```

## 🔄 扩展功能

### 添加新模型

在 `MultiModelEmotionAnalyzer` 类中添加新模型：

```python
def setup_models(self):
    # 现有模型...
    
    # 新模型
    try:
        self.new_model = load_new_model()
        print("✅ 新模型加载成功")
    except Exception as e:
        print(f"❌ 新模型加载失败: {e}")
        self.new_model = None
```

### 自定义输出格式

修改 `save_results` 方法来自定义输出格式。

## 📊 性能优化

### GPU加速

如果有NVIDIA GPU，可以安装CUDA版本：

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 批处理

支持批量处理多个音频文件，提高效率。

## 🎯 使用场景

- **语音助手情感分析**: 分析用户语音中的情感状态
- **客服质量评估**: 评估客服人员的情感表达
- **教育应用**: 分析学生语音中的学习情绪
- **心理健康**: 通过语音分析情绪状态
- **市场研究**: 分析用户对产品的语音反馈情感

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
