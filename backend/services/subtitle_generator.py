import os


def format_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def create_srt_for_scene(scene_text, start_time, duration, subtitle_path):
    os.makedirs(os.path.dirname(subtitle_path), exist_ok=True)

    end_time = start_time + duration

    content = (
        "1\n"
        f"{format_time(start_time)} --> {format_time(end_time)}\n"
        f"{scene_text}\n"
    )

    with open(subtitle_path, "w", encoding="utf-8") as file:
        file.write(content)

    return subtitle_path


def generate_subtitles_for_scenes(scenes, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for scene in scenes:
        duration = scene.get("duration_seconds", 8)

        if duration <= 0:
            duration = 8

        subtitle_path = os.path.join(
            output_folder,
            f"scene_{scene['scene_number']:04d}.srt"
        )

        create_srt_for_scene(
            scene_text=scene["scene_text"],
            # Each subtitle file is burned into its own scene chunk,
            # so it must start at 0 instead of using the full-video timeline.
            start_time=0,
            duration=duration,
            subtitle_path=subtitle_path
        )

        scene["subtitle_path"] = subtitle_path

    return scenes