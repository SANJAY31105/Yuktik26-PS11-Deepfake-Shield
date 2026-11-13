"""
Common utility functions for the Deepfake Detection Platform.
"""
import uuid
import hashlib
import time
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """Generate a unique identifier for analyses and alerts."""
    return str(uuid.uuid4())


def file_hash(data: bytes) -> str:
    """Compute SHA-256 hash of file bytes for deduplication."""
    return hashlib.sha256(data).hexdigest()


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class Timer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.elapsed_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.time() - self.start_time) * 1000
