"""
MoodCanvas API 主应用
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.api.v1.image import router as image_router
from src.api.v1.emotion import router as emotion_router
from src.api.v1.health import router as health_router
from src.api.dependencies import get_config_manager

app = FastAPI(
    title="MoodCanvas API", 
    version="v1",
    description="三阶段多模型情感分析系统",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    # 初始化配置和目录
    config_manager = get_config_manager()
    gen_dir = Path(config_manager.get_generated_images_dir())
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    # 挂载静态文件
    static_prefix = config_manager.config["paths"].get("static_url_prefix", "/static/generated")
    app.mount(static_prefix, StaticFiles(directory=str(gen_dir)), name="generated_images")

# 注册API路由
app.include_router(health_router)
app.include_router(image_router)
app.include_router(emotion_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to MoodCanvas API!",
        "version": "v1",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": app.version}