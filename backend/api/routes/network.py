"""
Coordinated network detection endpoints.

Provides API for detecting coordinated inauthentic behavior
across social media accounts and content.
"""
from fastapi import APIRouter
from backend.ai_engine import NetworkAnalyzer
from backend.models.schemas import (
    NetworkAnalysisRequest,
    NetworkAnalysisResponse,
    EvidenceItem,
    NetworkNode,
    NetworkEdge,
)

router = APIRouter(prefix="/network", tags=["Network Analysis"])

network_analyzer = NetworkAnalyzer()


@router.post("/analyze", response_model=NetworkAnalysisResponse)
async def analyze_network(request: NetworkAnalysisRequest):
    """
    Detect coordinated inauthentic behavior in a network of content/accounts.

    Uses graph-based analysis to identify bot networks, coordinated posting
    patterns, and content amplification campaigns.
    """
    result = await network_analyzer.analyze(
        content_ids=request.content_ids,
        accounts=request.accounts,
        time_window_hours=request.time_window_hours,
    )

    return NetworkAnalysisResponse(
        id=result["id"],
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        nodes=[NetworkNode(**n) for n in result.get("nodes", [])],
        edges=[NetworkEdge(**e) for e in result.get("edges", [])],
        cluster_count=result.get("cluster_count", 0),
        processing_time_ms=result["processing_time_ms"],
    )


@router.get("/scenario", response_model=NetworkAnalysisResponse)
async def get_scenario_network():
    """Returns the benchmark Scenario 2 coordinated network graph."""
    result = await network_analyzer.analyze()
    return NetworkAnalysisResponse(
        id=result["id"],
        verdict=result["verdict"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        evidence=[EvidenceItem(**e) for e in result.get("evidence", [])],
        nodes=[NetworkNode(**n) for n in result.get("nodes", [])],
        edges=[NetworkEdge(**e) for e in result.get("edges", [])],
        cluster_count=result.get("cluster_count", 0),
        processing_time_ms=result["processing_time_ms"],
    )
