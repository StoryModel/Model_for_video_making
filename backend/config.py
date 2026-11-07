import os

# =========================
# PROJECT SETTINGS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, "data", "projects.db")

# Outputs
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Upload folders
UPLOAD_CHARACTER_DIR = "character_refs"
UPLOAD_STORY_DIR = "story"

# Video
DEFAULT_VIDEO_FORMAT = "mp4"

# Video resolutions
VIDEO_RESOLUTIONS = {
    "360p": (640, 360),
    "720p": (1280, 720)
}

# Allowed story file types
ALLOWED_STORY_EXTENSIONS = [
    ".pdf",
    ".txt",
    ".docx"
]

# Allowed image file types
ALLOWED_IMAGE_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
]

# FFmpeg path
FFMPEG_PATH = "ffmpeg"

# Edge TTS
VOICE_NAME = "en-US-AndrewMultilingualNeural"

# Create folders automatically
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
