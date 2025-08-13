#backend/api/image.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from moodcanvas.config_manager import ConfigManager
from moodcanvas.image_edit_i2i import ImageEditor

from pydantic import BaseModel
from typing import Optional

from moodcanvas.text2image_t2i import ImageGenerator   

router = APIRouter(prefix="/api/v1/images", tags=["images"])

cfg = ConfigManager("config.json")
editor = ImageEditor(cfg)
t2i_gen = ImageGenerator(cfg)

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
    size: str | None = "1024x1024"      # t2i 推荐具体分辨率
    guidance_scale: float | None = 2.5  # 官方默认 2.5，范围 [1,10]
    seed: int | None = None
    watermark: bool | None = True
    num_images: int | None = 1
    save_local: bool = False
    
@router.post("/edit")
async def edit_image(

    prompt: str = Form(...),
    image: UploadFile = File(None),
    image_url: str | None = Form(None),
    guidance_scale: float | None= Form(None),
    size: str | None = Form(None),
    seed: int | None = Form(None),
    watermark: bool | None = Form(None),    
    save_local: bool = Form(False)
):
    """
    二选一传入：
    - image：上传文件
    - image_url：公网可访问的图像 URL（推荐）
    """
    try:
        src_path_or_url: str

        if image_url:
            src_path_or_url = image_url
        elif image:
            tmp_dir = Path(cfg.config["paths"].get("temp_dir", "temp_outputs"))
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

        payload = {"status": "succeeded", "outputs": [{"remote_url": result["remote_url"], "prompt": prompt}]}

        if save_local and "local_path" in result:
            gen_dir = Path(cfg.get_generated_images_dir())
            static_prefix = cfg.config["paths"].get("static_url_prefix", "/static/generated")
            # 将本地绝对路径转为 /static URL
            rel = Path(result["local_path"]).resolve().relative_to(gen_dir.resolve())
            url = f"{static_prefix}/{str(rel).replace('\\', '/')}"
            payload["outputs"][0]["local_url"] = url

        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/generate")
async def generate_image(req: GenerateReq):
    try:
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

        # 组装返回：remote_urls + 可选 local_urls
        gen_dir = Path(cfg.get_generated_images_dir()).resolve()
        static_prefix = cfg.config["paths"].get("static_url_prefix", "/static/generated")

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