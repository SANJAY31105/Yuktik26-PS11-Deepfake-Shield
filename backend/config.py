"""
Configuration constants for the Deepfake Detection Platform.
"""
import os

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./deepfake_detection.db")

# File uploads
MAX_UPLOAD_SIZE_MB = 100
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/mov", "video/webm", "video/mkv"}
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/flac"}
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# AI Engine
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./model_cache")
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence to flag as manipulated

# Verdicts
VERDICT_AUTHENTIC = "authentic"
VERDICT_MANIPULATED = "manipulated"
VERDICT_SUSPICIOUS = "suspicious"
VERDICT_UNVERIFIED = "unverified"

# WebSocket
WS_HEARTBEAT_INTERVAL = 30  # seconds

# CORS
CORS_ORIGINS = ["*"]
