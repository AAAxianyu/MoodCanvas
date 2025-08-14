# MoodCanvas API 文档

## 概述
MoodCanvas 是一个三阶段多模型情感分析系统，提供语音情感分析、图像生成和编辑等功能。

## 基础信息
- **Base URL**: `http://localhost:8000`
- **API版本**: v1
- **认证**: 需要设置环境变量 `ARK_API_KEY`

## 接口列表

### 1. 健康检查
- **路由**: `GET /api/v1/health`
- **描述**: 检查API服务状态
- **响应示例**:
```json
{
  "status": "ok",
  "service": "MoodCanvas API",
  "version": "v1"
}
```

### 2. 系统健康检查
- **路由**: `GET /api/v1/health/system`
- **描述**: 检查系统资源状态
- **响应示例**:
```json
{
  "status": "ok",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 65.8,
    "disk_percent": 45.2,
    "disk_free_gb": 125.6
  }
}
```

### 3. 模型健康检查
- **路由**: `GET /api/v1/health/models`
- **描述**: 检查模型目录状态
- **响应示例**:
```json
{
  "status": "ok",
  "directories": {
    "src/data/models": true,
    "data/input": true,
    "data/output": true,
    "data/temp": true
  }
}
```

### 4. 图像编辑 (Image-to-Image)
- **路由**: `POST /api/v1/images/edit`
- **描述**: 基于原图进行AI编辑
- **Content-Type**: `multipart/form-data`

**请求参数**:
```form-data
prompt: string (必填) - 编辑指令，如"把背景改成蓝色"
image: file (可选) - 上传的图片文件
image_url: string (可选) - 图片URL地址
guidance_scale: float (可选) - 引导强度，默认5.5，范围[1,10]
size: string (可选) - 输出尺寸，默认"adaptive"
seed: int (可选) - 随机种子
watermark: boolean (可选) - 是否添加水印，默认true
save_local: boolean (可选) - 是否保存到本地，默认false
```

**响应示例**:
```json
{
  "status": "succeeded",
  "outputs": [
    {
      "remote_url": "https://example.com/edited_image.png",
      "prompt": "把背景改成蓝色",
      "local_url": "/static/generated/edit_abc123.png"
    }
  ]
}
```

### 5. 图像生成 (Text-to-Image)
- **路由**: `POST /api/v1/images/generate`
- **描述**: 根据文本描述生成图像
- **Content-Type**: `application/json`

**请求体**:
```json
{
  "prompt": "一只可爱的小猫坐在花园里",
  "size": "1024x1024",
  "guidance_scale": 7.5,
  "seed": 12345,
  "watermark": true,
  "num_images": 1,
  "save_local": false
}
```

**响应示例**:
```json
{
  "status": "succeeded",
  "outputs": [
    {
      "remote_url": "https://example.com/generated_image.png",
      "prompt": "一只可爱的小猫坐在花园里",
      "local_url": "/static/generated/t2i_def456_0.png"
    }
  ]
}
```

### 6. 情感分析
- **路由**: `POST /api/v1/emotion/analyze`
- **描述**: 三阶段情感分析（ASR + 文本情感 + 声学情感）
- **Content-Type**: `multipart/form-data`

**请求参数**:
```form-data
audio_file: file (必填) - 音频文件
```

**响应示例**:
```json
{
  "audio_file": "path/to/audio.wav",
  "timestamp": "2024-01-01T12:00:00",
  "stages": {
    "asr": {
      "status": "success",
      "transcription": "今天天气真好"
    },
    "text_emotion": {
      "status": "success",
      "emotions": [
        {
          "label": "positive",
          "confidence": 0.85
        }
      ]
    },
    "audio_emotion": {
      "status": "success",
      "result": {...}
    }
  },
  "summary": {
    "overall_status": "success",
    "key_findings": [...],
    "recommendations": [...]
  }
}
```

## 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

## 常见HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

## 使用说明

### 1. 环境设置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，设置API密钥
ARK_API_KEY=your_actual_api_key
```

### 2. 启动服务
```bash
# 开发环境
python scripts/start_server.py

# 生产环境
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 3. 访问文档
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 注意事项

1. 项目依赖豆包API，需要有效的API密钥
2. 图片文件支持格式：jpg, jpeg, png, webp
3. 音频文件支持格式：wav, mp3, m4a, flac
4. 生成的图片会保存在 `data/generated_images` 目录
5. 可以通过 `/static/generated/` 路径访问本地保存的图片
