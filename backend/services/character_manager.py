import os
import shutil


def save_character_image(upload_file, output_folder, filename):
    os.makedirs(output_folder, exist_ok=True)

    image_path = os.path.join(output_folder, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return image_path


def create_character_description(main_character_name, extra_description=None):
    description = (
        f"Main character name: {main_character_name}. "
        "Keep the same face, hairstyle, outfit style, body type, and personality "
        "consistent in every scene. Use the uploaded character image as the main visual reference."
    )

    if extra_description:
        description += " " + extra_description

    return description


def build_character_prompt(character_description):
    return (
        character_description
        + " consistent character design, same identity, same hairstyle, same clothes, "
        + "anime manhwa character, detailed face, clean line art"
    )