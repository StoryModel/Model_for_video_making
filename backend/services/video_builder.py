import os
import subprocess


SYNC_PADDING = -0.05


def run_ffmpeg(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout


def get_audio_duration(audio_path):
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return float(result.stdout.strip())


def create_video_from_image_and_audio(image_path, audio_path, output_path, resolution="720p", subtitle_path=None):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    audio_duration = get_audio_duration(audio_path)
    final_duration = max(0.5, audio_duration + SYNC_PADDING)

    if resolution == "360p":
        width, height = 640, 360
    else:
        width, height = 1280, 720

    # Static image only. No zoom/pan movement, because subtitles are burned into the image itself.
    video_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-t", str(final_duration),
        "-i", image_path,
        "-i", audio_path,
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "stillimage",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        output_path
    ]

    run_ffmpeg(command)

    return output_path, final_duration


def create_scene_videos(scenes, output_folder, resolution="720p"):
    os.makedirs(output_folder, exist_ok=True)

    video_paths = []

    scenes = sorted(scenes, key=lambda x: x["scene_number"])

    for scene in scenes:
        scene_number = scene["scene_number"]

        output_path = os.path.join(
            output_folder,
            f"scene_{scene_number:04d}_{resolution}.mp4"
        )

        scene_image = scene.get("subtitled_image_path") or scene.get("image_path")

        video_path, duration = create_video_from_image_and_audio(
            image_path=scene_image,
            audio_path=scene["audio_path"],
            output_path=output_path,
            resolution=resolution,
            subtitle_path=None
        )

        scene["video_path"] = video_path
        scene["duration_seconds"] = duration
        video_paths.append(video_path)

    return video_paths


def merge_videos(video_paths, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    list_file = os.path.join(os.path.dirname(output_path), "video_list.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for video_path in video_paths:
            safe_path = os.path.abspath(video_path).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-movflags", "+faststart",
        output_path
    ]

    run_ffmpeg(command)

    return output_path
