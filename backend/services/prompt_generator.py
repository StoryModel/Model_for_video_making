def generate_prompt_for_scene(scene_text, character_prompt, style_prompt):
    prompt = f"""
{style_prompt},
{character_prompt},
scene description: {scene_text},
cinematic composition,
dramatic lighting,
high detail,
sharp focus,
webtoon panel style,
anime manhwa illustration,
16:9 aspect ratio
"""

    return " ".join(prompt.split())


def generate_negative_prompt():
    return (
        "low quality, blurry, bad anatomy, bad hands, extra fingers, missing fingers, "
        "deformed face, ugly, watermark, logo, text, duplicate character, distorted body"
    )


def add_prompts_to_scenes(scenes, character_prompt, style_prompt):
    for scene in scenes:
        scene["image_prompt"] = generate_prompt_for_scene(
            scene_text=scene["scene_text"],
            character_prompt=character_prompt,
            style_prompt=style_prompt
        )
        scene["negative_prompt"] = generate_negative_prompt()

    return scenes