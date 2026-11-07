import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _load_font(size):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.replace("\n", " ").split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font, stroke_width=2)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]


def burn_subtitle_on_image(image_path, subtitle_text, output_path, width=1280, height=720):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img_ratio = img.width / img.height
        target_ratio = width / height

        if img_ratio > target_ratio:
            new_height = height
            new_width = int(height * img_ratio)
        else:
            new_width = width
            new_height = int(width / img_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        img = img.crop((left, top, left + width, top + height))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(30, int(height * 0.055))
    font = _load_font(font_size)
    max_text_width = int(width * 0.86)
    lines = _wrap_text(draw, subtitle_text, font, max_text_width)

    line_heights = []
    max_line_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        line_heights.append(bbox[3] - bbox[1])
        max_line_width = max(max_line_width, bbox[2] - bbox[0])

    line_gap = int(font_size * 0.25)
    text_height = sum(line_heights) + line_gap * max(0, len(lines) - 1)
    padding_x = int(width * 0.035)
    padding_y = int(height * 0.025)
    box_width = max_line_width + padding_x * 2
    box_height = text_height + padding_y * 2
    box_left = (width - box_width) // 2
    box_top = height - box_height - int(height * 0.07)
    box_right = box_left + box_width
    box_bottom = box_top + box_height

    draw.rounded_rectangle(
        (box_left, box_top, box_right, box_bottom),
        radius=18,
        fill=(0, 0, 0, 150),
    )

    y = box_top + padding_y
    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 255),
        )
        y += line_heights[idx] + line_gap

    result = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    result.save(output_path, quality=95)
    return output_path


def burn_subtitles_for_scenes(scenes, output_folder, width=1280, height=720):
    os.makedirs(output_folder, exist_ok=True)
    for scene in sorted(scenes, key=lambda item: item["scene_number"]):
        source_image = scene.get("image_path") or scene.get("background_image_path")
        if not source_image or not os.path.exists(source_image):
            raise FileNotFoundError(f"Missing background image for scene {scene.get('scene_number')}")

        output_path = os.path.join(output_folder, f"scene_{scene['scene_number']:04d}_subtitle.jpg")
        burn_subtitle_on_image(
            image_path=source_image,
            subtitle_text=scene.get("scene_text", ""),
            output_path=output_path,
            width=width,
            height=height,
        )
        scene["subtitled_image_path"] = output_path
        scene["image_path"] = output_path
    return scenes
