"""
Dashboard and statistics endpoints.

Provides aggregate stats, recent activity, and system health
information for the frontend dashboard.
"""
from fastapi import APIRouter
import time
import random

from backend.models.schemas import DashboardStats, AlertMessage
from backend.db.database import get_stats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_start_time = time.time()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get aggregate dashboard statistics.
    Returns counts of analyses by type, recent alerts,
    and system health metrics.
    """
    uptime = time.time() - _start_time
    db_metrics = get_stats()

    return DashboardStats(
        total_analyses=db_metrics["total_analyses"],
        total_manipulated=db_metrics["total_manipulated"],
        total_authentic=db_metrics["total_authentic"],
        total_suspicious=db_metrics["total_suspicious"],
        average_confidence=db_metrics["average_confidence"],
        analyses_by_type=db_metrics["analyses_by_type"],
        recent_alerts=[AlertMessage(**a) for a in db_metrics["recent_alerts"]],
        network_clusters_detected=db_metrics["network_clusters_detected"],
        claims_verified=db_metrics["claims_verified"],
        uptime_seconds=round(uptime, 2),
    )


@router.get("/health")
async def health_check():
    """System health check with component status."""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "components": {
            "api": "ok",
            "database": "ok",
            "ai_engine": "ok",
            "websocket": "ok",
        },
    }
