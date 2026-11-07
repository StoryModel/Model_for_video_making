import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

from config import OUTPUTS_DIR

router = APIRouter(prefix="/download", tags=["Download"])


@router.get("/{project_id}/{quality}")
def download_video(project_id: int, quality: str):
    if quality not in ["360p", "720p"]:
        return {
            "success": False,
            "message": "Quality must be 360p or 720p."
        }

    video_path = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "videos",
        f"final_{quality}.mp4"
    )

    if not os.path.exists(video_path):
        return {
            "success": False,
            "message": f"{quality} video not found."
        }

    return FileResponse(
        path=video_path,
        filename=f"final_{quality}.mp4",
        media_type="video/mp4"
    )