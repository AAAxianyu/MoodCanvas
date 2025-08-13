# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from moodcanvas.config_manager import ConfigManager
from backend.api.image import router as image_router

app = FastAPI(title="MoodCanvas API", version="v1")

cfg = ConfigManager("config.json")
gen_dir = Path(cfg.get_generated_images_dir())
gen_dir.mkdir(parents=True, exist_ok=True)



static_prefix = cfg.config["paths"].get("static_url_prefix", "/static/generated")
app.mount(static_prefix, StaticFiles(directory=str(gen_dir)), name="generated_images")

app.include_router(image_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MoodCanvas API!"}

@app.get("/api/v1/health")
def helth():
    return {"status": "ok", "version": app.version}