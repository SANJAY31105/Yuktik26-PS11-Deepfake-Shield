"""
AI Engine package — multimodal deepfake detection modules.

Each module provides a detector/analyzer class with a standardized interface:
- analyze() -> dict with verdict, confidence, explanation, evidence
- load_model() -> None
- is_model_loaded -> bool
"""
from .image_detector import ImageDetector
from .video_detector import VideoDetector
from .audio_detector import AudioDetector
from .text_analyzer import TextAnalyzer
from .claim_verifier import ClaimVerifier
from .network_analyzer import NetworkAnalyzer
from .reverse_image import ReverseImageSearcher
from .multimodal_correlator import MultimodalCorrelator

__all__ = [
    "ImageDetector",
    "VideoDetector",
    "AudioDetector",
    "TextAnalyzer",
    "ClaimVerifier",
    "NetworkAnalyzer",
    "ReverseImageSearcher",
    "MultimodalCorrelator",
]
