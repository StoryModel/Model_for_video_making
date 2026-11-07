import os
import json
import shutil
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from database import get_project
from config import OUTPUTS_DIR, ALLOWED_IMAGE_EXTENSIONS

router = APIRouter(prefix="/backgrounds", tags=["Backgrounds"])


def safe_filename(filename: str, index: int) -> str:
    name, extension = os.path.splitext(filename)

    safe_name = "".join(
        ch if ch.isalnum() or ch in ("-", "_") else "_"
        for ch in name
    ).strip("_")

    if not safe_name:
        safe_name = "background"

    return f"{index:04d}_{safe_name}{extension.lower()}"


@router.post("/upload/{project_id}")
async def upload_background_images(
    project_id: int,
    files: List[UploadFile] = File(...)
):
    project = get_project(project_id)

    if not project:
        return {"success": False, "message": "Project not found."}

    if not files:
        return {"success": False, "message": "Upload at least one background image."}

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    backgrounds_folder = os.path.join(project_folder, "backgrounds")
    os.makedirs(backgrounds_folder, exist_ok=True)

    saved_backgrounds = []

    for index, upload_file in enumerate(files, start=1):
        extension = os.path.splitext(upload_file.filename)[1].lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return {
                "success": False,
                "message": "Only PNG, JPG, JPEG, and WEBP images are allowed."
            }

        output_path = os.path.join(
            backgrounds_folder,
            safe_filename(upload_file.filename, index)
        )

        with open(output_path, "wb") as file_object:
            shutil.copyfileobj(upload_file.file, file_object)

        saved_backgrounds.append(output_path)

    manifest_path = os.path.join(backgrounds_folder, "backgrounds.json")

    with open(manifest_path, "w", encoding="utf-8") as json_file:
        json.dump({"background_images": saved_backgrounds}, json_file, indent=4)

    return {
        "success": True,
        "message": f"{len(saved_backgrounds)} background image(s) uploaded.",
        "background_images": saved_backgrounds,
        "manifest_path": manifest_path
    }


@router.post("/update-scene/{project_id}")
async def update_scene_background(
    project_id: int,
    scene_number: int = Form(...),
    scene_text: str = Form(""),
    image_prompt: str = Form(""),
    image: UploadFile = File(None)
):
    project = get_project(project_id)

    if not project:
        return {"success": False, "message": "Project not found."}

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    scene_data_path = os.path.join(project_folder, "scene_data.json")

    if not os.path.exists(scene_data_path):
        return {"success": False, "message": "Scene data not found."}

    with open(scene_data_path, "r", encoding="utf-8") as file:
        scenes = json.load(file)

    backgrounds_folder = os.path.join(project_folder, "backgrounds")
    os.makedirs(backgrounds_folder, exist_ok=True)

    updated = False

    for scene in scenes:
        if scene["scene_number"] == scene_number:
            scene["scene_text"] = scene_text
            scene["image_prompt"] = image_prompt

            if image:
                extension = os.path.splitext(image.filename)[1].lower()

                if extension not in ALLOWED_IMAGE_EXTENSIONS:
                    return {"success": False, "message": "Invalid image format."}

                custom_name = f"scene_{scene_number:04d}_custom{extension}"
                image_path = os.path.join(backgrounds_folder, custom_name)

                with open(image_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)

                scene["image_path"] = image_path
                scene["subtitled_image_path"] = ""

            updated = True
            break

    if not updated:
        return {"success": False, "message": "Scene not found."}

    with open(scene_data_path, "w", encoding="utf-8") as file:
        json.dump(scenes, file, indent=4)

    return {
        "success": True,
        "message": "Scene updated successfully.",
        "scenes": scenes
    }


@router.post("/update-many-scenes/{project_id}")
async def update_many_scene_backgrounds(
    project_id: int,
    ranges: str = Form(...),
    images: List[UploadFile] = File(...)
):
    project = get_project(project_id)

    if not project:
        return {"success": False, "message": "Project not found."}

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")
    scene_data_path = os.path.join(project_folder, "scene_data.json")

    if not os.path.exists(scene_data_path):
        return {"success": False, "message": "Scene data not found."}

    try:
        ranges_data = json.loads(ranges)
    except json.JSONDecodeError:
        return {"success": False, "message": "Invalid ranges data."}

    if not isinstance(ranges_data, list) or not ranges_data:
        return {"success": False, "message": "Add at least one picture range."}

    if not images:
        return {"success": False, "message": "Upload at least one picture."}

    with open(scene_data_path, "r", encoding="utf-8") as file:
        scenes = json.load(file)

    backgrounds_folder = os.path.join(project_folder, "backgrounds")
    os.makedirs(backgrounds_folder, exist_ok=True)

    saved_images = {}

    for range_index, range_item in enumerate(ranges_data, start=1):
        try:
            from_scene = int(range_item.get("from_scene"))
            to_scene = int(range_item.get("to_scene"))
            file_index = int(range_item.get("file_index"))
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": f"Invalid scene range for Picture No.{range_index}."
            }

        if from_scene < 1 or to_scene < 1:
            return {
                "success": False,
                "message": f"Scene numbers must start from 1 for Picture No.{range_index}."
            }

        if from_scene > to_scene:
            return {
                "success": False,
                "message": f"From Scene cannot be greater than To Scene for Picture No.{range_index}."
            }

        if to_scene > len(scenes):
            return {
                "success": False,
                "message": f"To Scene for Picture No.{range_index} cannot be greater than total scenes ({len(scenes)})."
            }

        if file_index < 0 or file_index >= len(images):
            return {
                "success": False,
                "message": f"Image file missing for Picture No.{range_index}."
            }

        upload_file = images[file_index]
        extension = os.path.splitext(upload_file.filename)[1].lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return {
                "success": False,
                "message": "Only PNG, JPG, JPEG, and WEBP images are allowed."
            }

        if file_index not in saved_images:
            picture_name = range_item.get("picture_name") or upload_file.filename
            output_filename = safe_filename(
                f"change_all_{range_index}_{picture_name}{extension}",
                range_index
            )

            output_path = os.path.join(backgrounds_folder, output_filename)

            with open(output_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            saved_images[file_index] = output_path

        image_path = saved_images[file_index]

        for scene in scenes:
            scene_number = int(scene.get("scene_number", 0))

            if from_scene <= scene_number <= to_scene:
                scene["image_path"] = image_path
                scene["subtitled_image_path"] = ""

    with open(scene_data_path, "w", encoding="utf-8") as file:
        json.dump(scenes, file, indent=4)

    return {
        "success": True,
        "message": "All selected picture ranges updated successfully. Please add subtitles again.",
        "scenes": scenes
    }