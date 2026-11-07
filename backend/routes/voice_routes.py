import os
import json
import shutil
from fastapi import APIRouter, Form

from database import get_project
from config import OUTPUTS_DIR, VOICE_NAME
from services.voice_generator import generate_voice_for_scenes

router = APIRouter(prefix="/voice", tags=["Voice"])


def _save_json(path, data):
    tmp_path = path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    os.replace(tmp_path, path)


@router.post("/generate/{project_id}")
def generate_voice(project_id: int):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    project_folder = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}"
    )

    scene_data_path = os.path.join(
        project_folder,
        "scene_data.json"
    )

    audio_folder = os.path.join(
        project_folder,
        "audio"
    )

    if not os.path.exists(scene_data_path):
        return {
            "success": False,
            "message": "Scene data not found. Add story first."
        }

    try:
        with open(
            scene_data_path,
            "r",
            encoding="utf-8"
        ) as file:
            scenes = json.load(file)

        scenes = generate_voice_for_scenes(
            scenes=scenes,
            output_folder=audio_folder,
            voice=VOICE_NAME,
        )

        # Safety pass
        for index, scene in enumerate(scenes, start=1):
            scene_number = scene.get("scene_number") or index

            audio_path = os.path.abspath(
                os.path.join(
                    audio_folder,
                    f"scene_{int(scene_number):04d}.mp3"
                )
            ).replace("\\", "/")

            if os.path.exists(audio_path):
                scene["audio_path"] = audio_path

        _save_json(scene_data_path, scenes)

        audio_count = sum(
            1 for scene in scenes
            if scene.get("audio_path")
            and os.path.exists(scene["audio_path"])
        )

        if audio_count == 0:
            return {
                "success": False,
                "message": "Voice files were generated but could not be linked to scenes.",
            }

        return {
            "success": True,
            "message": "Voice generated successfully.",
            "total_audio_files": audio_count,
            "audio_folder": os.path.abspath(audio_folder).replace("\\", "/"),
            "scenes": scenes,
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Voice generation failed.",
            "error": str(e),
        }


# ==========================================
# UPDATE VOICE / SAVE CHANGES
# ==========================================

@router.post("/update-scene/{project_id}")
def update_voice_scene(
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

    project_folder = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}"
    )

    scene_data_path = os.path.join(
        project_folder,
        "scene_data.json"
    )

    if not os.path.exists(scene_data_path):
        return {
            "success": False,
            "message": "Scene data not found."
        }

    with open(
        scene_data_path,
        "r",
        encoding="utf-8"
    ) as file:
        scenes = json.load(file)

    updated = False

    for scene in scenes:
        if scene["scene_number"] == scene_number:

            scene["scene_text"] = scene_text
            scene["image_prompt"] = image_prompt

            # old audio becomes invalid after text edit
            old_audio = scene.get("audio_path")

            if old_audio and os.path.exists(old_audio):
                try:
                    os.remove(old_audio)
                except:
                    pass

            scene["audio_path"] = ""

            updated = True
            break

    if not updated:
        return {
            "success": False,
            "message": "Scene not found."
        }

    # Remove old final videos
    videos_folder = os.path.join(
        project_folder,
        "videos"
    )

    if os.path.exists(videos_folder):
        shutil.rmtree(videos_folder)

    _save_json(scene_data_path, scenes)

    return {
        "success": True,
        "message": "Voice text saved. Click Generate Voice again to regenerate audio.",
        "scenes": scenes
    }