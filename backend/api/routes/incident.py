"""
Incident Intelligence & Scenario Simulation Endpoints
======================================================
Provides holistic multimodal incident correlation and handles the
Yuktik-2026 PS11 benchmark scenario:
"At 10:00 AM, a video begins circulating on social media claiming that a major dam near a city has collapsed..."
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
import time

from backend.ai_engine import (
    ImageDetector,
    VideoDetector,
    AudioDetector,
    ReverseImageSearcher,
    ClaimVerifier,
    NetworkAnalyzer,
    MultimodalCorrelator,
)
from backend.api.websocket import manager

router = APIRouter(prefix="/incident", tags=["Incident Intelligence"])

image_detector = ImageDetector()
video_detector = VideoDetector()
audio_detector = AudioDetector()
reverse_image = ReverseImageSearcher()
claim_verifier = ClaimVerifier()
network_analyzer = NetworkAnalyzer()
correlator = MultimodalCorrelator()


@router.get("/scenario-demo")
async def run_scenario_demo(background_tasks: BackgroundTasks):
    """
    Executes the Yuktik-2026 Problem Statement 2 'Tricky Real-World Scenario':
    1. 10:00 AM video claiming major dam collapsed near city
    2. AI-generated audio recording announcing emergency evacuation
    3. Old photograph of flood from another state presented as current evidence
    4. Manipulated video showing public official making false announcement
    5. Authentic government update contradicts circulating claims
    6. Misinformation spreading in English, Hindi, and Telugu
    7. Multi-account coordinated bot distribution
    """
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"

    photo_path = data_dir / "kerala_flood_reused_photo.jpg"
    photo_bytes = photo_path.read_bytes() if photo_path.exists() else (b"DAM_FLOOD_PHOTO_SIMULATION_BYTES_01928374" * 50)

    audio_path = data_dir / "collector_evacuation_voice_clone.wav"
    audio_bytes = audio_path.read_bytes() if audio_path.exists() else (b"VOICE_CLONE_AUDIO_SIMULATION_BYTES_99887766" * 50)

    video_path = data_dir / "official_announcement_fake.mp4"
    video_bytes = video_path.read_bytes() if video_path.exists() else (b"VIDEO_DEEPFAKE_BYTES_12345678" * 50)

    # 1. Run Claim Verification across English, Hindi, and Telugu
    claim_en = await claim_verifier.analyze(
        claim="URGENT: Major dam near Hyderabad collapsed at 10 AM! Emergency evacuation ordered!",
        language="en",
    )
    claim_hi = await claim_verifier.analyze(
        claim="बड़ा बांध टूटा! शहर में जल प्रलय की चेतावनी, तुरंत सुरक्षित स्थान पर पहुंचे!",
        language="hi",
    )
    claim_te = await claim_verifier.analyze(
        claim="డ్యామ్ కొట్టుకుపోయింది! కలెక్టర్ అత్యవసర ఖాళీ ఆదేశాలు జారీ చేశారు!",
        language="te",
    )

    # 2. Run Reused Image Search on Flood Photo
    reverse_res = await reverse_image.analyze(
        image_bytes=photo_bytes,
        filename="flood_evidence_kerala_reused.jpg",
        context_claim="Massive water surge witnessed at downstream bridge! Dam wall collapsed completely!",
    )

    # 3. Run Audio Forensics on Collector Evacuation Audio
    audio_res = await audio_detector.analyze(
        audio_bytes=audio_bytes,
        filename="collector_emergency_evac_ai_voice.wav",
    )

    # 4. Run Video Deepfake Detection on Public Official
    video_res = await video_detector.analyze(
        video_bytes=video_bytes,
        filename="official_announcement_fake.mp4",
    )

    # 5. Run Coordinated Social Network Analysis
    network_res = await network_analyzer.analyze()

    # 6. Holistic Multimodal Cross-Correlation & Contradiction Fusion
    correlated_intelligence = await correlator.correlate(
        video_result=video_res,
        audio_result=audio_res,
        reverse_image_result=reverse_res,
        claim_result=claim_en,
        network_result=network_res,
        incident_title="Yuktik-2026 PS11 Benchmark: Dam Collapse Coordinated Campaign",
    )

    # 7. Broadcast real-time critical alert to all connected dashboard websockets
    background_tasks.add_task(
        manager.broadcast,
        {
            "id": f"alert_{int(time.time())}",
            "type": "critical_coordinated_campaign",
            "severity": "critical",
            "title": "CRITICAL MISINFORMATION INCIDENT: Dam Collapse Hoax",
            "message": "Multimodal analysis detected synthetic audio clone, manipulated official video, and coordinated bot amplification in EN/HI/TE.",
            "data": {
                "verdict": correlated_intelligence["overall_verdict"],
                "confidence": correlated_intelligence["overall_confidence"],
                "incident_id": correlated_intelligence["incident_id"],
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    return {
        "status": "success",
        "benchmark_scenario": "Yuktik '26 PS11 Tricky Scenario: Dam Collapse Disinformation",
        "correlated_intelligence": correlated_intelligence,
        "multilingual_claims": {
            "english": claim_en,
            "hindi": claim_hi,
            "telugu": claim_te,
        },
        "audio_forensics": audio_res,
        "video_forensics": video_res,
        "reused_image_analysis": reverse_res,
        "coordinated_network": network_res,
    }


@router.post("/correlate")
async def correlate_incident(payload: Dict[str, Any]):
    """Correlates arbitrary user-provided incident signals across modalities."""
    result = await correlator.correlate(
        video_result=payload.get("video_result"),
        audio_result=payload.get("audio_result"),
        image_result=payload.get("image_result"),
        reverse_image_result=payload.get("reverse_image_result"),
        claim_result=payload.get("claim_result"),
        network_result=payload.get("network_result"),
        incident_title=payload.get("incident_title", "Custom Misinformation Investigation"),
    )
    return result

