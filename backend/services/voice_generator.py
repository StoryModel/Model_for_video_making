import os
import re
import asyncio
import time
import subprocess
import edge_tts


def clean_text(text):
    text = str(text or "")

    text = text.replace("—", "-")
    text = text.replace("–", "-")
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    text = text.replace("’", "'")
    text = text.replace("‘", "'")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")

    text = text.replace("…", "...")

    # Remove markdown symbols, emoji and other characters the TTS can't speak
    text = re.sub(r"[*_#~`^|<>\\\[\]{}=+@]", " ", text)
    text = re.sub(
        r"[^\w\s.,!?;:'\"()\-/%&$]", " ", text, flags=re.UNICODE
    )

    text = re.sub(r"\s+", " ", text).strip()

    # edge-tts raises "No audio was received" when there is nothing
    # speakable (no letters or digits), so replace such scenes
    if not re.search(r"\w", text, flags=re.UNICODE):
        text = "Silence."

    return text


FALLBACK_VOICE = "en-US-AndrewNeural"
MAX_ATTEMPTS = 6


async def create_voice_async(
    text,
    output_path,
    voice="en-US-AndrewMultilingualNeural"
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    safe_text = clean_text(text)

    # Retry temporary TTS failures up to 3 times
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Alternate voices: the multilingual one often gets throttled
        active_voice = voice if attempt % 2 == 1 else FALLBACK_VOICE

        try:
            communicate = edge_tts.Communicate(safe_text, active_voice)
            await communicate.save(output_path)

            if (
                not os.path.exists(output_path)
                or os.path.getsize(output_path) < 1000
            ):
                raise Exception("Invalid or empty audio generated")

            return output_path

        except Exception as e:

            # Remove incomplete audio before retrying
            if os.path.exists(output_path):
                os.remove(output_path)

            reason = str(e)
            if "503" in reason:
                reason = "Microsoft voice server busy (503)"
            elif len(reason) > 80:
                reason = reason[:80] + "..."

            last_error = reason

            print(
                f"TTS attempt {attempt}/{MAX_ATTEMPTS} failed ({active_voice}): {reason}"
            )

            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(min(attempt * 3, 15))

    raise Exception(
        f"Voice generation failed after {MAX_ATTEMPTS} attempts: {last_error}"
    )


def create_voice(text, output_path, voice="en-US-AndrewMultilingualNeural"):
    return asyncio.run(
        create_voice_async(text, output_path, voice)
    )


def create_silent_audio(text, output_path):
    """Last resort so video generation is never blocked by one scene.
    Makes a silent mp3 whose length matches the estimated speech time."""
    words = max(len(str(text or "").split()), 1)
    duration = max(words / 2.5, 1.5)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=24000:cl=mono",
            "-t", f"{duration:.2f}",
            "-acodec", "libmp3lame",
            "-b:a", "32k",
            output_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    # Marker so the next "Generate Voice" click retries this scene
    with open(output_path + ".silent", "w") as marker:
        marker.write("silent placeholder")


def generate_voice_for_scenes(
    scenes,
    output_folder,
    voice="en-US-AndrewMultilingualNeural"
):
    os.makedirs(output_folder, exist_ok=True)

    def process(scene):
        scene_number = scene["scene_number"]

        audio_path = os.path.join(
            output_folder,
            f"scene_{scene_number:04d}.mp3"
        )

        silent_marker = audio_path + ".silent"

        # A silent placeholder from an earlier run: try real voice again
        if os.path.exists(silent_marker):
            os.remove(silent_marker)
            if os.path.exists(audio_path):
                os.remove(audio_path)

        # Preserve audio that was generated successfully earlier
        if (
            os.path.exists(audio_path)
            and os.path.getsize(audio_path) >= 1000
        ):
            scene["audio_path"] = audio_path.replace("\\", "/")
            print(f"Audio already exists for scene {scene_number}")
            return True

        try:
            create_voice(
                text=scene.get("scene_text", ""),
                output_path=audio_path,
                voice=voice
            )

            scene["audio_path"] = audio_path.replace("\\", "/")

            print(f"Generated audio for scene {scene_number}")

            # Small pause so Microsoft's service doesn't throttle bursts
            time.sleep(1.0)
            return True

        except Exception as e:
            print(f"FAILED scene {scene_number}: {e}")
            scene["audio_path"] = ""
            return False

    failed = [scene for scene in scenes if not process(scene)]

    # Second pass: let the service cool down, then retry failed scenes
    for round_number in range(2):
        if not failed:
            break

        print(
            f"Retrying {len(failed)} failed scene(s) after cooldown "
            f"(round {round_number + 1}/2)..."
        )
        time.sleep(30)
        failed = [scene for scene in failed if not process(scene)]

    # Still failing: use a silent placeholder so the video can be built.
    # Click Generate Voice again later to replace these with real voice.
    for scene in failed:
        scene_number = scene["scene_number"]
        audio_path = os.path.join(
            output_folder,
            f"scene_{scene_number:04d}.mp3"
        )

        try:
            create_silent_audio(scene.get("scene_text", ""), audio_path)
            scene["audio_path"] = audio_path.replace("\\", "/")
            print(
                f"Scene {scene_number}: silent placeholder used "
                f"(click Generate Voice again to retry real voice)"
            )
        except Exception as e:
            print(f"Scene {scene_number}: could not create placeholder: {e}")

    return scenes