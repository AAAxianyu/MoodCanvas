"""
情感分析API接口
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body
from fastapi.responses import JSONResponse
from pathlib import Path

from src.core.config_manager import ConfigManager
from src.services.emotion_analyzer import MultiModelEmotionAnalyzer
from src.utils.file_utils import save_upload_file
from src.api.dependencies import get_config_manager, get_emotion_analyzer

router = APIRouter(prefix="/api/v1/emotion", tags=["emotion"])

@router.post("/analyze")
async def analyze_emotion(
    audio_file: UploadFile = File(...),
    config_manager: ConfigManager = Depends(get_config_manager),
    analyzer: MultiModelEmotionAnalyzer = Depends(get_emotion_analyzer)
):
    """
    三阶段情感分析：ASR + 文本情感 + 声学情感
    """
    try:
        # 保存上传的音频文件
        temp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
        audio_path = save_upload_file(audio_file, temp_dir, "emotion_analysis")
        
        # 运行三阶段分析
        results = await analyzer.run_three_stage_analysis(str(audio_path))
        
        return JSONResponse(content=results)
        
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

@router.get("/health")
async def emotion_health():
    """情感分析服务健康检查"""
    return {"status": "ok", "service": "emotion_analysis"}
