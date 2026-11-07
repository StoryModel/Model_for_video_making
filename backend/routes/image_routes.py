import os
import json
from fastapi import APIRouter

from database import get_project
from config import OUTPUTS_DIR

router = APIRouter(prefix="/images", tags=["Images"])


def load_json(path, default=None):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@router.post("/generate/{project_id}")
def generate_images(project_id: int):
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
            "message": "Scene data not found. Add story first."
        }

    scenes = load_json(scene_data_path, [])

    backgrounds_manifest_path = os.path.join(
        project_folder,
        "backgrounds",
        "backgrounds.json"
    )

    background_data = load_json(backgrounds_manifest_path, {})
    background_images = background_data.get("background_images", [])

    if not background_images:
        return {
            "success": False,
            "message": "Background images missing. Upload background images first."
        }

    missing_backgrounds = [path for path in background_images if not os.path.exists(path)]

    if missing_backgrounds:
        return {
            "success": False,
            "message": "One or more uploaded background images are missing."
        }

    sorted_scenes = sorted(scenes, key=lambda x: x["scene_number"])

    # Assign images in contiguous blocks instead of alternating.
    # Example: 2 images + 4 scenes => 1,1,2,2
    # Example: 2 images + 5 scenes => 1,1,1,2,2
    total_scenes = len(sorted_scenes)
    total_backgrounds = len(background_images)
    base_count = total_scenes // total_backgrounds
    extra_count = total_scenes % total_backgrounds

    assigned_backgrounds = []
    for background_index, background_path in enumerate(background_images):
        repeat_count = base_count + (1 if background_index < extra_count else 0)
        assigned_backgrounds.extend([background_path] * repeat_count)

    assigned_backgrounds = assigned_backgrounds[:total_scenes]

    for index, scene in enumerate(sorted_scenes):
        background_path = assigned_backgrounds[index]
        scene["image_path"] = background_path
        scene["background_image_path"] = background_path
        scene.pop("subtitled_image_path", None)
        scene["image_prompt"] = scene.get("image_prompt", "Uploaded background image")

    with open(scene_data_path, "w", encoding="utf-8") as file:
        json.dump(scenes, file, indent=4)

    return {
        "success": True,
        "message": "Background images assigned evenly to scenes.",
        "total_images": len(scenes),
        "total_backgrounds": len(background_images)
    }