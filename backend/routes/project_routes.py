import os
import shutil
from fastapi import APIRouter

from database import (
    create_project,
    get_all_projects,
    get_project,
    delete_project
)

from config import OUTPUTS_DIR

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/create")
def create_new_project(data: dict):
    story_title = data.get("story_title")
    main_character_name = data.get("main_character_name")

    if not story_title:
        return {
            "success": False,
            "message": "Story title is required."
        }

    project_id = create_project(
        story_title=story_title,
        main_character_name=main_character_name
    )

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")

    folders = [
        "character_refs",
        "story",
        "images",
        "audio",
        "subtitles",
        "chunks",
        "videos"
    ]

    for folder in folders:
        os.makedirs(os.path.join(project_folder, folder), exist_ok=True)

    return {
        "success": True,
        "message": "Project created successfully.",
        "project_id": project_id,
        "project_folder": project_folder
    }


@router.get("/")
def fetch_all_projects():
    projects = get_all_projects()

    return {
        "success": True,
        "projects": projects
    }


@router.get("/{project_id}")
def fetch_single_project(project_id: int):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    return {
        "success": True,
        "project": project
    }


@router.delete("/{project_id}")
def delete_single_project(project_id: int):
    project = get_project(project_id)

    if not project:
        return {
            "success": False,
            "message": "Project not found."
        }

    delete_project(project_id)

    project_folder = os.path.join(OUTPUTS_DIR, f"project_{project_id}")

    if os.path.exists(project_folder):
        shutil.rmtree(project_folder)

    return {
        "success": True,
        "message": f"Project {project_id} deleted successfully."
    }