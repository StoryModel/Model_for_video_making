import os
import json
import shutil
from fastapi import APIRouter, Form

from database import get_project
from config import OUTPUTS_DIR
from services.subtitle_generator import generate_subtitles_for_scenes
from services.subtitle_image_burner import burn_subtitles_for_scenes
from services.video_builder import create_scene_videos, merge_videos

router = APIRouter(prefix="/video", tags=["Video"])


@router.post("/add-subtitles/{project_id}")
def add_subtitles_to_images(project_id: int):
    project = get_project(project_id)

    if not project:
        return {"success": False, "message": "Project not found."}

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    scene_data_path = os.path.join(project_folder, "scene_data.json")

    if not os.path.exists(scene_data_path):
        return {"success": False, "message": "Scene data not found. Add story first."}

    with open(scene_data_path, "r", encoding="utf-8") as file:
        scenes = json.load(file)

    for scene in scenes:
        if not scene.get("image_path") or not os.path.exists(scene["image_path"]):
            return {"success": False, "message": "Background images missing. Click Use Background Images first."}

    try:
        subtitle_images_folder = os.path.join(project_folder, "subtitle_images")
        scenes = burn_subtitles_for_scenes(
            scenes=scenes,
            output_folder=subtitle_images_folder,
            width=1280,
            height=720,
        )

        with open(scene_data_path, "w", encoding="utf-8") as file:
            json.dump(scenes, file, indent=4)

        return {
            "success": True,
            "message": "Subtitles added directly onto all background images.",
            "total_images": len(scenes),
            "scenes": scenes,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to add subtitles to images.",
            "error": str(e)
        }


@router.post("/update-subtitle/{project_id}")
def update_subtitle_scene(
    project_id: int,
    scene_number: int = Form(...),
    scene_text: str = Form(""),
    image_prompt: str = Form("")
):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    scene_data_path = os.path.join(project_folder, "scene_data.json")

    if not os.path.exists(scene_data_path):
        return {
            "success": False,
            "message": "Scene data not found."
        }

    with open(scene_data_path, "r", encoding="utf-8") as file:
        scenes = json.load(file)

    updated = False

    for scene in scenes:
        if scene["scene_number"] == scene_number:
            scene["scene_text"] = scene_text
            scene["image_prompt"] = image_prompt

            # Subtitle image is now outdated after text edit.
            scene["subtitled_image_path"] = ""

            updated = True
            break

    if not updated:
        return {
            "success": False,
            "message": "Scene not found."
        }

    # Remove old final videos because subtitles changed.
    videos_folder = os.path.join(project_folder, "videos")
    if os.path.exists(videos_folder):
        shutil.rmtree(videos_folder)

    with open(scene_data_path, "w", encoding="utf-8") as file:
        json.dump(scenes, file, indent=4)

    return {
        "success": True,
        "message": "Subtitle text saved. Click Add Subtitle to image again to regenerate subtitle image.",
        "scenes": scenes
    }


@router.post("/build/{project_id}")
def build_video(project_id: int):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    scene_data_path = os.path.join(project_folder, "scene_data.json")

    if not os.path.exists(scene_data_path):
        return {
            "success": False,
            "message": "Scene data not found."
        }

    with open(scene_data_path, "r", encoding="utf-8") as file:
        scenes = json.load(file)

    for scene in scenes:
        preferred_image = scene.get("subtitled_image_path") or scene.get("image_path")

        if not preferred_image or not os.path.exists(preferred_image):
            return {
                "success": False,
                "message": "Images missing. Use Background Images and Add Subtitle to image first."
            }

        scene["image_path"] = preferred_image

        if not scene.get("audio_path") or not os.path.exists(scene["audio_path"]):
            return {
                "success": False,
                "message": "Audio missing. Generate voice first."
            }

    subtitles_folder = os.path.join(project_folder, "subtitles")
    chunks_folder = os.path.join(project_folder, "chunks")
    videos_folder = os.path.join(project_folder, "videos")

    try:
        scenes = generate_subtitles_for_scenes(
            scenes=scenes,
            output_folder=subtitles_folder
        )

        video_paths_720p = create_scene_videos(
            scenes=scenes,
            output_folder=chunks_folder,
            resolution="720p"
        )

        final_720p_path = os.path.join(videos_folder, "final_720p.mp4")

        merge_videos(
            video_paths=video_paths_720p,
            output_path=final_720p_path
        )

        video_paths_360p = create_scene_videos(
            scenes=scenes,
            output_folder=chunks_folder,
            resolution="360p"
        )

        final_360p_path = os.path.join(videos_folder, "final_360p.mp4")

        merge_videos(
            video_paths=video_paths_360p,
            output_path=final_360p_path
        )

        with open(scene_data_path, "w", encoding="utf-8") as file:
            json.dump(scenes, file, indent=4)

        return {
            "success": True,
            "message": "Video created successfully.",
            "final_720p": final_720p_path,
            "final_360p": final_360p_path
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Video building failed.",
            "error": str(e)
        }