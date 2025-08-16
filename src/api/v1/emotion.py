"""
情感分析API接口
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body
from typing import Optional
from fastapi.responses import JSONResponse
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.services.emotion_analyzer import MultiModelEmotionAnalyzer
from src.services.emotion_analyzer import ImageEmotionAnalyzerService
from src.utils.file_utils import save_upload_file
from src.api.dependencies import get_config_manager, get_emotion_analyzer, get_image_emotion_analyzer

router = APIRouter(prefix="/api/v1/emotion", tags=["emotion"])


# 新增统一入口，支持 image/text/audio 三者任意组合
@router.post("/analyze_multi")
async def analyze_multi(
    image_file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    config_manager: ConfigManager = Depends(get_config_manager),
    analyzer: MultiModelEmotionAnalyzer = Depends(get_emotion_analyzer),
    image_analyzer: ImageEmotionAnalyzerService = Depends(get_image_emotion_analyzer)
):
    """
    多模态情感分析：图片、文字、语音三者任意组合，自动跳过缺失项，合并结果后生成文案和图片。
    """
    result = {}
    try:
        # 图片处理
        if image_file:
            temp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
            image_path = save_upload_file(image_file, temp_dir, "emotion_analysis")
            image_result = image_analyzer.analyze_image_path(str(image_path))
            result["image_content"] = image_result.get("analysis", {})
            # 清理临时文件
            image_path.unlink()
        # 语音处理
        if audio_file:
            temp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
            audio_path = save_upload_file(audio_file, temp_dir, "emotion_analysis")
            audio_result = await analyzer.run_three_stage_analysis(str(audio_path))
            result["audio"] = audio_result
        # 文字处理
        if text:
            text_result = await analyzer.run_text_emotion_analysis(text)
            result["text"] = text_result
        # 合并情感标签
        emotion_tags = []
        if "image_content" in result and "styles" in result["image_content"]:
            emotion_tags += result["image_content"].get("styles", [])
        if "audio" in result and "emotion_analysis" in result["audio"]:
            emotion_tags += result["audio"]["emotion_analysis"].get("merged_emotion", [])
        if "text" in result and "emotion_analysis" in result["text"]:
            emotion_tags += result["text"]["emotion_analysis"].get("text_emotion", [])
        # 去重
        emotion_tags = list(set(emotion_tags))
        # 构造生成文案和图片的输入
        gen_text = None
        gen_image_url = None
        # 优先用文字，否则用语音转文字，否则用图片caption
        input_text = text or (result.get("audio", {}).get("transcribed_text")) or (result.get("image_content", {}).get("caption")) or ""
        # 生成文案和图片（调用已有生成内容方法）
        if input_text:
            gen_content = await analyzer._generate_content(input_text, emotion_tags)
            gen_text = gen_content.get("text")
            gen_image_url = gen_content.get("image_url")
        # 返回结构
        return JSONResponse(content={
            "image_content": result.get("image_content"),
            "audio": result.get("audio"),
            "text": result.get("text"),
            "emotion_tags": emotion_tags,
            "generated_text": gen_text,
            "generated_image_url": gen_image_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze_text")
async def analyze_text_emotion(
    text: str = Body(..., embed=True),
    config_manager: ConfigManager = Depends(get_config_manager),
    analyzer: MultiModelEmotionAnalyzer = Depends(get_emotion_analyzer)
):
    """
    纯文本情感分析：文本情感 + 文案生成 + 图片生成
    """
    try:
        # 运行文本情感分析
        results = await analyzer.run_text_emotion_analysis(text)
        
        return JSONResponse(content=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze_image")
def analyze_image_emotion(
    image_file: UploadFile = File(...),
    config_manager: ConfigManager = Depends(get_config_manager),
    analyzer: ImageEmotionAnalyzerService = Depends(get_image_emotion_analyzer)

):
    """
    图像情感分析：图像情感 + 文案生成 + 图片编辑
    """
    try:
        # 保存上传的图像文件
        temp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
        image_path = save_upload_file(image_file, temp_dir, "emotion_analysis")
        # 运行图像情感分析
        results = analyzer.analyze_image_path(str(image_path))
        # 清理临时文件
        image_path.unlink()
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/health")
async def emotion_health():
    """情感分析服务健康检查"""
    return {"status": "ok", "service": "emotion_analysis"}
