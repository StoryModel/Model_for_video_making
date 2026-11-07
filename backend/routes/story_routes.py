import os
import json
from fastapi import APIRouter, UploadFile, File

from database import get_project
from config import OUTPUTS_DIR, ALLOWED_STORY_EXTENSIONS
from services.story_reader import extract_story_text, save_extracted_story
from services.scene_splitter import create_scenes_from_story

router = APIRouter(prefix="/story", tags=["Story"])


def repair_scene_media_paths(project_id: int, scenes: list):
    """Repair missing audio_path values from files already generated on disk."""
    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    audio_folder = os.path.join(project_folder, "audio")

    changed = False
    for index, scene in enumerate(scenes, start=1):
        scene_number = scene.get("scene_number") or index
        expected_audio = os.path.abspath(
            os.path.join(audio_folder, f"scene_{int(scene_number):04d}.mp3")
        ).replace("\\", "/")

        if (not scene.get("audio_path")) and os.path.exists(expected_audio):
            scene["audio_path"] = expected_audio
            changed = True

    return scenes, changed


def save_scene_data(path: str, scenes: list):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=4)
    os.replace(tmp_path, path)


@router.post("/upload/{project_id}")
async def upload_story_file(project_id: int, file: UploadFile = File(...)):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_STORY_EXTENSIONS:
        return {
            "success": False,
            "message": "Only PDF, TXT, and DOCX files are allowed."
        }

    story_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}", "story")
    os.makedirs(story_folder, exist_ok=True)

    uploaded_path = os.path.join(story_folder, file.filename)

    with open(uploaded_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        extracted_text = extract_story_text(uploaded_path)

        extracted_story_path = os.path.join(story_folder, "extracted_story.txt")
        save_extracted_story(extracted_text, extracted_story_path)

        scenes = create_scenes_from_story(
            story_text=extracted_text,
            max_words_per_scene=80
        )

        scene_data_path = os.path.join(
            OUTPUTS_DIR,
            f"project_{project_id}",
            "scene_data.json"
        )

        with open(scene_data_path, "w", encoding="utf-8") as f:
            json.dump(scenes, f, indent=4)

        return {
            "success": True,
            "message": "Story uploaded, extracted, and split into scenes.",
            "uploaded_path": uploaded_path,
            "extracted_story_path": extracted_story_path,
            "scene_data_path": scene_data_path,
            "total_scenes": len(scenes)
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to read story file.",
            "error": str(e)
        }


@router.post("/write/{project_id}")
def write_story_text(project_id: int, data: dict):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    story_text = data.get("story_text")

    if not story_text:
        return {
            "success": False,
            "message": "Story text is required."
        }

    story_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}", "story")
    os.makedirs(story_folder, exist_ok=True)

    story_path = os.path.join(story_folder, "original_script.txt")

    with open(story_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    scenes = create_scenes_from_story(
        story_text=story_text,
        max_words_per_scene=80
    )

    scene_data_path = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "scene_data.json"
    )

    with open(scene_data_path, "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=4)

    return {
        "success": True,
        "message": "Story saved and split into scenes.",
        "story_path": story_path,
        "scene_data_path": scene_data_path,
        "total_scenes": len(scenes)
    }


@router.get("/scenes/{project_id}")
def get_story_scenes(project_id: int):
    scene_data_path = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "scene_data.json"
    )

    if not os.path.exists(scene_data_path):
        return {
            "success": False,
            "message": "Scene data not found. Upload or write story first."
        }

    with open(scene_data_path, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    scenes, changed = repair_scene_media_paths(project_id, scenes)
    if changed:
        save_scene_data(scene_data_path, scenes)

    return {
        "success": True,
        "total_scenes": len(scenes),
        "scenes": scenes
    }
    
    
@router.put("/scenes/{project_id}")
def update_story_scenes(project_id: int, data: dict):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    scenes = data.get("scenes")

    if scenes is None:
        return {
            "success": False,
            "message": "Scenes data is required."
        }

    scene_data_path = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "scene_data.json"
    )

    existing_scenes = []
    if os.path.exists(scene_data_path):
        with open(scene_data_path, "r", encoding="utf-8") as f:
            existing_scenes = json.load(f)

    existing_by_number = {scene.get("scene_number"): scene for scene in existing_scenes}

    # Do not allow a stale frontend save to erase generated image/audio paths.
    for scene in scenes:
        old_scene = existing_by_number.get(scene.get("scene_number"), {})
        for key in ["image_path", "subtitled_image_path", "audio_path", "subtitle_path"]:
            if not scene.get(key) and old_scene.get(key):
                scene[key] = old_scene[key]

    scenes, _ = repair_scene_media_paths(project_id, scenes)
    save_scene_data(scene_data_path, scenes)

    return {
        "success": True,
        "message": "Scenes updated successfully.",
        "total_scenes": len(scenes),
        "scenes": scenes
    }