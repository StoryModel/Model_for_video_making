import os
import json
from fastapi import APIRouter, UploadFile, File, Form

from database import get_project, update_character_description
from config import OUTPUTS_DIR, ALLOWED_IMAGE_EXTENSIONS
from services.character_manager import (
    save_character_image,
    create_character_description,
    build_character_prompt
)

router = APIRouter(prefix="/character", tags=["Character"])


@router.post("/upload/{project_id}")
async def upload_character_image(
    project_id: int,
    main_character_name: str = Form(...),
    file: UploadFile = File(...),
    extra_description: str = Form("")
):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return {
            "success": False,
            "message": "Only PNG, JPG, JPEG, and WEBP images are allowed."
        }

    character_folder = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "character_refs"
    )

    image_path = save_character_image(
        upload_file=file,
        output_folder=character_folder,
        filename=file.filename
    )

    character_description = create_character_description(
        main_character_name=main_character_name,
        extra_description=extra_description
    )

    character_prompt = build_character_prompt(character_description)

    character_json_path = os.path.join(character_folder, "character_data.json")

    character_data = {
        "main_character_name": main_character_name,
        "character_image_path": image_path,
        "character_description": character_description,
        "character_prompt": character_prompt
    }

    with open(character_json_path, "w", encoding="utf-8") as json_file:
        json.dump(character_data, json_file, indent=4)

    update_character_description(project_id, character_description)

    return {
        "success": True,
        "message": "Character image uploaded and description created.",
        "character_data": character_data,
        "character_json_path": character_json_path
    }


@router.post("/description/{project_id}")
def save_manual_character_description(project_id: int, data: dict):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    main_character_name = data.get("main_character_name", "Main Character")
    description = data.get("character_description")

    if not description:
        return {
            "success": False,
            "message": "Character description is required."
        }

    character_prompt = build_character_prompt(description)

    character_folder = os.path.join(
        OUTPUTS_DIR,
        f"project_{project_id}",
        "character_refs"
    )

    os.makedirs(character_folder, exist_ok=True)

    character_json_path = os.path.join(character_folder, "character_data.json")

    character_data = {
        "main_character_name": main_character_name,
        "character_image_path": "",
        "character_description": description,
        "character_prompt": character_prompt
    }

    with open(character_json_path, "w", encoding="utf-8") as json_file:
        json.dump(character_data, json_file, indent=4)

    update_character_description(project_id, description)

    return {
        "success": True,
        "message": "Character description saved.",
        "character_data": character_data
    }