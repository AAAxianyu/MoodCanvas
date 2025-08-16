"""
图像生成和编辑API接口
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os
from src.core.config_manager import ConfigManager
from src.models.image.image2image import ImageEditor
from pydantic import BaseModel
from typing import Optional
from src.models.image.text2image import ImageGenerator
from src.api.dependencies import get_config_manager

router = APIRouter(prefix="/api/v1/images", tags=["images"])

ALLOWED_SUFFIX = {".jpg", ".jpeg", ".png", ".webp"}

def save_upload_temp(upload: UploadFile, tmp_dir: Path) -> Path:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIX:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {suffix}. 仅支持 {ALLOWED_SUFFIX}。")
    tmp_path = tmp_dir / f"upload_{upload.filename}"
    with tmp_path.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return tmp_path

class GenerateReq(BaseModel):
    prompt: str
    size: str | None = "1024x1024"
    guidance_scale: float | None = 2.5
    seed: int | None = None
    watermark: bool | None = True
    num_images: int | None = 1
    save_local: bool = False

@router.post("/edit")
async def edit_image(
    prompt: str = Form(...),
    image: UploadFile = File(None),
    image_url: str | None = Form(None),
    emotion_tags: str | None = Form(None),  # 新增：情感标签
    original_text: str | None = Form(None),  # 新增：原始文字
    guidance_scale: float | None = Form(None),
    size: str | None = Form(None),
    seed: int | None = Form(None),
    watermark: bool | None = Form(None),    
    save_local: bool = Form(False),
    config_manager: ConfigManager = Depends(get_config_manager)
):
    """
    图片编辑接口：
    - image：上传文件
    - image_url：公网可访问的图像 URL（推荐）
    - emotion_tags：情感标签，用于增强编辑效果
    - original_text：原始文字，与情感标签配合使用
    """
    try:
        # 获取图像编辑器实例
        editor = ImageEditor(config_manager)
        
        src_path_or_url: str

        if image_url:
            src_path_or_url = image_url
        elif image:
            # 从配置管理器获取临时目录
            tmp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
            src = save_upload_temp(image, tmp_dir)
            src_path_or_url = str(src)
        else:
            raise HTTPException(status_code=400, detail="请提供 image 或 image_url")

        # 构建增强的提示词
        enhanced_prompt = prompt
        if emotion_tags and original_text:
            try:
                emotion_list = emotion_tags.split(',') if ',' in emotion_tags else [emotion_tags]
                emotion_desc = ", ".join(emotion_list)
                enhanced_prompt = f"基于文字'{original_text}'和情感'{emotion_desc}'，{prompt}"
            except Exception as e:
                # 如果情感标签处理失败，使用原始提示词
                pass

        result = editor.edit_image(
            src_path_or_url,
            prompt=enhanced_prompt,
            guidance_scale=guidance_scale,
            size=size,
            seed=seed,
            watermark=watermark,
            save_local=save_local
        )

        payload = {
            "status": "succeeded", 
            "outputs": [{
                "remote_url": result["remote_url"], 
                "prompt": enhanced_prompt,
                "original_prompt": prompt,
                "emotion_tags": emotion_tags,
                "original_text": original_text
            }]
        }

        if save_local and "local_path" in result:
            gen_dir = Path(editor.out_dir)
            static_prefix = "/static/generated"  # 默认静态文件前缀
            rel = Path(result["local_path"]).resolve().relative_to(gen_dir.resolve())
            url = f"{static_prefix}/{str(rel).replace('\\', '/')}"
            payload["outputs"][0]["local_url"] = url

        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_image(
    req: GenerateReq,
    config_manager: ConfigManager = Depends(get_config_manager)
):
    try:
        # 获取图像生成器实例
        t2i_gen = ImageGenerator(config_manager)
        
        result = t2i_gen.generate(
            prompt=req.prompt,
            guidance_scale=req.guidance_scale,
            size=req.size,
            seed=req.seed,
            num_images=req.num_images,
            watermark=req.watermark,
            save_local=req.save_local
        )
        payload = {"status": "succeeded", "outputs": []}

        gen_dir = Path(t2i_gen.out_dir).resolve()
        static_prefix = "/static/generated"  # 默认静态文件前缀

        local_urls = []
        if req.save_local and "local_paths" in result:
            for lp in result["local_paths"]:
                rel = Path(lp).resolve().relative_to(gen_dir)
                local_urls.append(f"{static_prefix}/{str(rel).replace('\\', '/')}")

        for i, rurl in enumerate(result["remote_urls"]):
            item = {"remote_url": rurl, "prompt": req.prompt}
            if local_urls:
                item["local_url"] = local_urls[i]
            payload["outputs"].append(item)

        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reedit")
async def reedit_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    image_url: str | None = Form(None),
    guidance_scale: float | None = Form(None),
    size: str | None = Form(None),
    seed: int | None = Form(None),
    watermark: bool | None = Form(None),    
    save_local: bool = Form(False),
    config_manager: ConfigManager = Depends(get_config_manager)
):
    """
    图片重新编辑接口（不涉及情感标签）：
    当用户对返回不满意时，可以在原有返回的基础上添加文字提示词，重新修改图片
    
    - image：必须上传的图片文件
    - image_url：可选，公网可访问的图像 URL
    - prompt：用户的文字提示词
    """
    try:
        # 获取图像编辑器实例
        editor = ImageEditor(config_manager)
        
        src_path_or_url: str

        if image_url:
            src_path_or_url = image_url
        elif image:
            # 从配置管理器获取临时目录
            tmp_dir = Path(config_manager.config["paths"].get("temp_dir", "data/temp"))
            src = save_upload_temp(image, tmp_dir)
            src_path_or_url = str(src)
        else:
            raise HTTPException(status_code=400, detail="请提供 image 或 image_url")

        result = editor.edit_image(
            src_path_or_url,
            prompt=prompt,
            guidance_scale=guidance_scale,
            size=size,
            seed=seed,
            watermark=watermark,
            save_local=save_local
        )

        payload = {
            "status": "succeeded", 
            "outputs": [{
                "remote_url": result["remote_url"], 
                "prompt": prompt,
                "type": "reedit"
            }]
        }

        if save_local and "local_path" in result:
            gen_dir = Path(editor.out_dir)
            static_prefix = "/static/generated"  # 默认静态文件前缀
            rel = Path(result["local_path"]).resolve().relative_to(gen_dir.resolve())
            url = f"{static_prefix}/{str(rel).replace('\\', '/')}"
            payload["outputs"][0]["local_url"] = url

        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))