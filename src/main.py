"""
MoodCanvas API 主应用
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import logging
from src.api.v1.image import router as image_router
from src.api.v1.emotion import router as emotion_router
from src.api.v1.health import router as health_router
from src.api.dependencies import get_config_manager

# 配置日志
def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('moodcanvas.log', encoding='utf-8')
        ]
    )
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

# 加载环境变量
def load_environment():
    """加载环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        print(f"加载环境变量文件: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"设置环境变量: {key.strip()}")
    else:
        print("未找到.env文件，使用系统环境变量")

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
    # 配置日志
    setup_logging()
    
    # 加载环境变量
    load_environment()
    
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