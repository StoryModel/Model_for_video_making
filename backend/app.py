from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import OUTPUTS_DIR

from database import init_database

from routes.project_routes import router as project_router
from routes.story_routes import router as story_router
from routes.character_routes import router as character_router
from routes.background_routes import router as background_router
from routes.image_routes import router as image_router
from routes.voice_routes import router as voice_router
from routes.video_routes import router as video_router
from routes.download_routes import router as download_router

app = FastAPI(
    title="AI Manhwa Video Generator",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_database()
    print("Database initialized successfully.")


@app.get("/")
def home():
    return {
        "message": "AI Manhwa Video Generator Backend Running"
    }


app.include_router(project_router)
app.include_router(story_router)
app.include_router(character_router)
app.include_router(background_router)
app.include_router(image_router)
app.include_router(voice_router)
app.include_router(video_router)
app.include_router(download_router)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")