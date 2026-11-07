import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


def wrap_text(text, max_chars_per_line=52, max_lines=3):
    text = " ".join(text.split())
    lines = textwrap.wrap(text, width=max_chars_per_line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1] + "..."

    return lines


def create_placeholder_image(scene_text, output_path, size=(1280, 720)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    width, height = size

    image = Image.new("RGB", size, color=(18, 18, 18))
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 44)
        subtitle_font = ImageFont.truetype("arialbd.ttf", 42)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    draw.text(
        (40, 35),
        "AI Image Placeholder",
        fill=(220, 220, 220),
        font=title_font
    )

    subtitle_box_height = 170
    box_y = height - subtitle_box_height

    draw.rectangle(
        [(0, box_y), (width, height)],
        fill=(0, 0, 0)
    )

    lines = wrap_text(scene_text, max_chars_per_line=55, max_lines=3)

    line_height = 48
    total_text_height = len(lines) * line_height
    start_y = box_y + (subtitle_box_height - total_text_height) // 2

    for index, line in enumerate(lines):
        text_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        text_width = text_bbox[2] - text_bbox[0]

        x = (width - text_width) // 2
        y = start_y + index * line_height

        outline_range = 3

        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    draw.text(
                        (x + ox, y + oy),
                        line,
                        fill=(0, 0, 0),
                        font=subtitle_font
                    )

        draw.text(
            (x, y),
            line,
            fill=(255, 255, 255),
            font=subtitle_font
        )

    image.save(output_path)
    return output_path


def generate_images_for_scenes(scenes, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for scene in scenes:
        scene_number = scene["scene_number"]
        image_path = os.path.join(output_folder, f"scene_{scene_number:04d}.jpg")

        create_placeholder_image(
            scene_text=scene["scene_text"],
            output_path=image_path
        )

        scene["image_path"] = image_path

    return scenes