import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUTS_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"
SKILLS_DIR = BASE_DIR / "skills"

# Ensure directories exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# TTS Voice Settings (Microsoft edge-tts - 100% Free)
# Selected voice: en-US-GuyNeural (Energetic, natural tech narrator)
VOICE_NAME = os.getenv("VOICE_NAME", "en-US-GuyNeural")
VOICE_RATE = os.getenv("VOICE_RATE", "+0%")
VOICE_PITCH = os.getenv("VOICE_PITCH", "+0Hz")

# Video Settings (YouTube Shorts 9:16)
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))

# Font resolution
FONT_MONO = Path("/System/Library/Fonts/SFNSMono.ttf")
FONT_SANS = Path("/System/Library/Fonts/Supplemental/Helvetica.ttc")

if not FONT_MONO.exists():
    fallback_mono = [
        Path("/System/Library/Fonts/SFCompact.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Courier New.ttf")
    ]
    for fb in fallback_mono:
        if fb.exists():
            FONT_MONO = fb
            break

if not FONT_SANS.exists():
    fallback_sans = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        FONTS_DIR / "Impact.ttf"
    ]
    for fb in fallback_sans:
        if fb.exists():
            FONT_SANS = fb
            break

PRIMARY_FONT = FONT_SANS

# Theme Colors (User's Slate Black & Neon Green Aesthetic)
COLORS = {
    "bg_dark": (15, 23, 42),        # Slate black #0f172a
    "bg_gradient": (30, 41, 59),    # Slate 800 #1e293b
    "text_main": (255, 255, 255),   # Crisp White
    "highlight": (34, 197, 94),     # Neon Green #22c55e
    "accent_cyan": (56, 189, 248),  # Sky blue #38bdf8
    "accent_green": (34, 197, 94),  # Neon Green #22c55e
    "badge_bg": (30, 41, 59),       # Pill badge background
    "stroke": (0, 0, 0),            # Black text outline
    "progress_bar": (34, 197, 94)   # Neon Green progress indicator
}

# YouTube Data API v3 Settings
YOUTUBE_PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY_STATUS", "private")  # private, unlisted, public
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", str(BASE_DIR / "token.json"))
YOUTUBE_CATEGORY_ID = "28"  # 28 = Science & Technology

# VPS Storage Lifecycle & Retention Settings
# Keeps videos for N days, then purges heavy .mp4/.mp3 while keeping script.json metadata
STORAGE_RETENTION_DAYS = int(os.getenv("STORAGE_RETENTION_DAYS", "3"))  # Default 3 days for lean VPS
AUTO_CLEANUP_AFTER_UPLOAD = os.getenv("AUTO_CLEANUP_AFTER_UPLOAD", "true").lower() == "true"

# Curated High-RPM Viral Tech & AI Topic Pool
CURATED_TOPICS = [
    "Why China's DeepSeek V3 Shook Silicon Valley in 48 Hours",
    "How Nvidia's Blackwell GPUs Actually Draw 1200 Watts Each",
    "The Real Reason Big Tech is Buying Decommissioned Nuclear Plants",
    "Why Quantum Computing Could Break Bitcoin Faster Than You Think",
    "How Humanoid Robots Actually Balance Without Falling Over",
    "The Dark Secret Behind Free AI Tools You Use Everyday",
    "Why Apple is Secretly Developing Their Own Data Center Chips",
    "How Autonomous Drone Swarms Communicate Without GPS",
    "The Shocking Amount of Water It Takes to Train One AI Model",
    "Why Solid-State Batteries Will Kill Traditional Electric Cars",
    "How AI Brain-Computer Interfaces Read Thoughts Into Text",
    "The 100-Billion-Dollar Space Mining Race Starting Right Now",
    "Why Starlink Satellites Burn Up in the Atmosphere on Purpose",
    "How Modern Subsea Internet Cables Actually Survive the Ocean",
    "The Real Reason Sam Altman Wants 7 Trillion Dollars for Chips"
]
