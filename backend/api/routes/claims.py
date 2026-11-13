"""
Claim verification endpoints.

Provides API for verifying textual claims and analyzing text
for misinformation using RAG-based fact checking and NLP analysis.
"""
from fastapi import APIRouter
from backend.ai_engine import ClaimVerifier, TextAnalyzer
from backend.db.database import store_claim
from backend.models.schemas import (
    ClaimVerificationRequest,
    ClaimVerificationResponse,
    MediaAnalysisResponse,
    MediaType,
    EvidenceItem,
)

router = APIRouter(prefix="/claims", tags=["Claim Verification"])

claim_verifier = ClaimVerifier()
text_analyzer = TextAnalyzer()


@router.post("/verify", response_model=ClaimVerificationResponse)
async def verify_claim(request: ClaimVerificationRequest):
    """
    Verify a factual claim using RAG-based fact checking.

    Cross-references the claim against trusted fact-checking databases
    and returns a verdict with supporting sources.
    """
    result = await claim_verifier.analyze(
        claim=request.claim,
        context=request.context,
        source_url=request.source_url,
    )

    store_claim(
        claim_id=result["id"],
        claim_text=request.claim,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        sources=result.get("sources", []),
    )

    return ClaimVerificationResponse(
        id=result["id"],
        claim=request.claim,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        sources=result.get("sources", []),
        processing_time_ms=result["processing_time_ms"],
    )


@router.post("/analyze-text", response_model=MediaAnalysisResponse)
async def analyze_text(request: ClaimVerificationRequest):
    """
    Analyze text for misinformation patterns using NLP.

    Checks for sensationalism, emotional manipulation, clickbait,
    and other misinformation indicators.
    """
    result = await text_analyzer.analyze(
        text=request.claim,
        context=request.context,
    )

    return MediaAnalysisResponse(
        id=result["id"],
        media_type=MediaType.text,
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        processing_time_ms=result["processing_time_ms"],
    )
