"""
Media upload and analysis endpoints.

Handles image, video, and audio file uploads and routes them
to the appropriate AI engine detector for deepfake analysis.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid

from backend.ai_engine import ImageDetector, VideoDetector, AudioDetector, ReverseImageSearcher, MultimodalCorrelator
from backend.models.schemas import MediaAnalysisResponse, MediaType, EvidenceItem
from backend.config import ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES, ALLOWED_AUDIO_TYPES
from backend.db.database import store_analysis

router = APIRouter(prefix="/media", tags=["Media Analysis"])

# Singleton detector instances
image_detector = ImageDetector()
video_detector = VideoDetector()
audio_detector = AudioDetector()
reverse_image = ReverseImageSearcher()
correlator = MultimodalCorrelator()


def _detect_media_type(content_type: str) -> Optional[MediaType]:
    """Detect media type from MIME content type."""
    if content_type in ALLOWED_IMAGE_TYPES:
        return MediaType.image
    elif content_type in ALLOWED_VIDEO_TYPES:
        return MediaType.video
    elif content_type in ALLOWED_AUDIO_TYPES:
        return MediaType.audio
    return None


@router.post("/analyze", response_model=MediaAnalysisResponse)
async def analyze_media(
    file: UploadFile = File(...),
    media_type: Optional[str] = Form(None),
):
    """
    Upload and analyze a media file for deepfake/manipulation detection.

    Accepts image, video, or audio files. Auto-detects media type from
    content type if not specified.
    """
    file_bytes = await file.read()

    # Determine media type
    if media_type:
        try:
            detected_type = MediaType(media_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid media_type: {media_type}")
    else:
        detected_type = _detect_media_type(file.content_type or "")
        if detected_type is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Provide media_type explicitly.",
            )

    # Route to appropriate detector
    if detected_type == MediaType.image:
        result = await image_detector.analyze(file_bytes, filename=file.filename)
    elif detected_type == MediaType.video:
        result = await video_detector.analyze(file_bytes, filename=file.filename)
    elif detected_type == MediaType.audio:
        result = await audio_detector.analyze(file_bytes, filename=file.filename)
    else:
        raise HTTPException(status_code=400, detail="Unsupported media type for file analysis.")

    store_analysis(
        analysis_id=result["id"],
        media_type=detected_type.value,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=result.get("evidence", []),
        filename=file.filename,
    )

    return MediaAnalysisResponse(
        id=result["id"],
        media_type=detected_type,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        processing_time_ms=result["processing_time_ms"],
    )


@router.post("/analyze/multimodal", response_model=MediaAnalysisResponse)
async def analyze_multimodal(
    files: list[UploadFile] = File(...),
):
    """
    Analyze multiple media files together using cross-modal correlation.

    Uploads several files (image + audio, video + text, etc.) and produces
    a unified deepfake assessment.
    """
    modality_results = []

    for file in files:
        file_bytes = await file.read()
        detected_type = _detect_media_type(file.content_type or "")

        if detected_type == MediaType.image:
            result = await image_detector.analyze(file_bytes, filename=file.filename)
        elif detected_type == MediaType.video:
            result = await video_detector.analyze(file_bytes, filename=file.filename)
        elif detected_type == MediaType.audio:
            result = await audio_detector.analyze(file_bytes, filename=file.filename)
        else:
            continue
        modality_results.append(result)

    if not modality_results:
        raise HTTPException(status_code=400, detail="No supported media files provided.")

    unified = await correlator.analyze(modality_results)

    store_analysis(
        analysis_id=unified["id"],
        media_type="image",
        verdict=unified["verdict"],
        confidence=unified["confidence"],
        explanation=unified["explanation"],
        evidence=unified.get("evidence", []),
        filename="multimodal_batch",
    )

    return MediaAnalysisResponse(
        id=unified["id"],
        media_type=MediaType.image,  # primary
        verdict=unified["verdict"],
        confidence=unified["confidence"],
        explanation=unified["explanation"],
        evidence=[EvidenceItem(**e) for e in unified.get("evidence", [])],
        processing_time_ms=unified["processing_time_ms"],
    )


@router.post("/reverse-search", response_model=MediaAnalysisResponse)
async def reverse_image_search(file: UploadFile = File(...)):
    """Search for prior occurrences of an uploaded image."""
    file_bytes = await file.read()
    result = await reverse_image.analyze(file_bytes, filename=file.filename)

    store_analysis(
        analysis_id=result["id"],
        media_type="image",
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=result.get("evidence", []),
        filename=file.filename,
    )

    return MediaAnalysisResponse(
        id=result["id"],
        media_type=MediaType.image,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        processing_time_ms=result["processing_time_ms"],
    )
