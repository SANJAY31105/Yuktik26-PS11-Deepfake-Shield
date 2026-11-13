"""
Pydantic models for all API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class VerdictEnum(str, Enum):
    authentic = "authentic"
    manipulated = "manipulated"
    suspicious = "suspicious"
    unverified = "unverified"
    verified = "verified"
    contradicted = "contradicted"
    misleading = "misleading"


class MediaType(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    text = "text"


# ── Evidence ──────────────────────────────────────────────────────────────────

class EvidenceItem(BaseModel):
    """A single piece of evidence from analysis."""
    type: str = Field(..., description="Type of evidence (e.g., 'frequency_anomaly', 'face_swap')")
    description: str = Field(..., description="Human-readable description")
    severity: float = Field(0.5, ge=0.0, le=1.0, description="Severity score 0-1")
    metadata: Optional[dict] = Field(None, description="Additional structured data")


# ── Media Analysis ────────────────────────────────────────────────────────────

class MediaAnalysisRequest(BaseModel):
    """Request for media analysis (used with JSON body, file sent separately)."""
    media_type: Optional[MediaType] = Field(None, description="Type of media (auto-detected if omitted)")
    url: Optional[str] = Field(None, description="URL of media to analyze (alternative to file upload)")
    options: Optional[dict] = Field(None, description="Additional analysis options")


class MediaAnalysisResponse(BaseModel):
    """Response from media analysis."""
    id: str = Field(..., description="Unique analysis ID")
    media_type: MediaType
    verdict: VerdictEnum
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    explanation: str = Field(..., description="Human-readable explanation")
    evidence: List[EvidenceItem] = Field(default_factory=list)
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Claim Verification ───────────────────────────────────────────────────────

class ClaimVerificationRequest(BaseModel):
    """Request to verify a textual claim."""
    claim: str = Field(..., description="The claim text to verify")
    context: Optional[str] = Field(None, description="Additional context around the claim")
    source_url: Optional[str] = Field(None, description="Source URL where the claim was found")
    language: Optional[str] = Field("en", description="Language code")


class ClaimVerificationResponse(BaseModel):
    """Response from claim verification."""
    id: str = Field(..., description="Unique verification ID")
    claim: str
    verdict: VerdictEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list, description="Supporting source URLs")
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Network Analysis ─────────────────────────────────────────────────────────

class NetworkNode(BaseModel):
    """A node in the coordination network."""
    id: str
    label: str
    type: str = Field("account", description="Node type: account, post, domain")
    degree: Optional[int] = 0
    centrality: Optional[float] = 0.0
    followers: Optional[int] = 100
    cluster: Optional[str] = "none"
    metadata: Optional[dict] = None


class NetworkEdge(BaseModel):
    """An edge in the coordination network."""
    source: str
    target: str
    weight: float = 1.0
    relationship: str = Field("unknown", description="Type of relationship")


class NetworkAnalysisRequest(BaseModel):
    """Request for coordinated network detection."""
    content_ids: List[str] = Field(..., description="List of content/post IDs to analyze")
    accounts: Optional[List[str]] = Field(None, description="List of account identifiers")
    time_window_hours: Optional[int] = Field(24, description="Time window for coordination detection")


class NetworkAnalysisResponse(BaseModel):
    """Response from network analysis."""
    id: str = Field(..., description="Unique analysis ID")
    verdict: VerdictEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    nodes: List[NetworkNode] = Field(default_factory=list)
    edges: List[NetworkEdge] = Field(default_factory=list)
    cluster_count: int = Field(0, description="Number of coordinated clusters found")
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── WebSocket / Alerts ────────────────────────────────────────────────────────

class AlertMessage(BaseModel):
    """Real-time alert message sent via WebSocket."""
    id: str
    type: str = Field(..., description="Alert type: new_detection, network_alert, claim_flagged")
    severity: str = Field("info", description="info, warning, critical")
    title: str
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    """Aggregate stats for the dashboard."""
    total_analyses: int = 0
    total_manipulated: int = 0
    total_authentic: int = 0
    total_suspicious: int = 0
    average_confidence: float = 0.0
    analyses_by_type: dict = Field(default_factory=lambda: {
        "image": 0, "video": 0, "audio": 0, "text": 0
    })
    recent_alerts: List[AlertMessage] = Field(default_factory=list)
    network_clusters_detected: int = 0
    claims_verified: int = 0
    uptime_seconds: float = 0.0
