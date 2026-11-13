"""
Video Deepfake Detector
=======================
Detects manipulated video content using:
  1. Per-frame image deepfake analysis (via ImageDetector)
  2. Temporal consistency — face-count jumps, score flicker between frames
  3. Face detection via OpenCV Haar cascades
  4. Aggregated scoring with timeline of suspicious moments

Falls back gracefully when OpenCV or models are unavailable.
Set env DEEPFAKE_MOCK_MODE=true for realistic demo results.
"""

import os
import io
import uuid
import time
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MOCK_MODE = os.environ.get("DEEPFAKE_MOCK_MODE", "false").lower() in ("1", "true", "yes")

DEFAULT_SAMPLE_INTERVAL = 15
MAX_FRAMES_TO_ANALYZE = 60
MIN_FRAMES_FOR_TEMPORAL = 4

FACE_CASCADE_FILE = "haarcascade_frontalface_default.xml"

FACE_COUNT_JUMP_THRESHOLD = 2
SCORE_JUMP_THRESHOLD = 0.35

CONFIDENCE_THRESHOLD_MANIPULATED = 0.60
CONFIDENCE_THRESHOLD_SUSPICIOUS = 0.35


class VideoDetector:
    """Detects deepfake / manipulated videos via per-frame + temporal analysis."""

    def __init__(self):
        self._image_detector = None
        self._face_cascade = None
        self._face_cascade_loaded = False
        self._model_loaded = False

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------
    @property
    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def load_model(self) -> None:
        """Load face cascade + image detector model."""
        # Image detector
        if self._image_detector is None:
            from .image_detector import ImageDetector
            self._image_detector = ImageDetector()

        self._image_detector.load_model()
        img_ok = self._image_detector.is_model_loaded

        # Face cascade
        try:
            import cv2
            cascade_path = cv2.data.haarcascades + FACE_CASCADE_FILE
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            if self._face_cascade.empty():
                logger.warning("Haar cascade loaded but empty.")
                self._face_cascade = None
            else:
                self._face_cascade_loaded = True
        except Exception as exc:
            logger.warning("Failed to load face cascade: %s", exc)
            self._face_cascade = None

        self._model_loaded = img_ok or self._face_cascade_loaded

    # ------------------------------------------------------------------
    # Public API — async to match architect's interface
    # ------------------------------------------------------------------
    async def analyze(
        self,
        video_bytes: bytes,
        filename: Optional[str] = None,
        sample_interval: int = DEFAULT_SAMPLE_INTERVAL,
        max_frames: int = MAX_FRAMES_TO_ANALYZE,
    ) -> dict:
        """
        Analyze a video for signs of deepfake manipulation.

        Args:
            video_bytes: Raw bytes of the video file.
            filename: Original filename.
            sample_interval: Analyze every N-th frame.
            max_frames: Cap on total frames to analyze.

        Returns:
            dict with verdict, confidence, explanation, evidence, frame_analysis,
            suspicious_moments, metadata, processing_time_ms
        """
        start = time.time()

        if MOCK_MODE:
            result = self._mock_result(filename or "unknown")
            result["processing_time_ms"] = round((time.time() - start) * 1000, 2)
            return result

        if not self._model_loaded:
            self.load_model()

        # --- Open video -----------------------------------------------
        try:
            cap, tmp_path = self._open_video(video_bytes)
        except Exception as exc:
            return self._error_result(f"Could not open video: {exc}", filename or "unknown")

        try:
            result = self._analyze_capture(cap, filename or "unknown", sample_interval, max_frames)
            result["processing_time_ms"] = round((time.time() - start) * 1000, 2)
            return result
        finally:
            cap.release()
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    # ------------------------------------------------------------------
    # Internal — core pipeline
    # ------------------------------------------------------------------
    def _analyze_capture(
        self, cap, filename: str, sample_interval: int, max_frames: int
    ) -> dict:
        import cv2
        from PIL import Image as PILImage

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0.0

        if total_frames <= 0:
            return self._error_result("Video has no readable frames.", filename)

        frame_indices = list(range(0, total_frames, sample_interval))[:max_frames]

        frame_results: List[Dict[str, Any]] = []
        face_counts: List[int] = []
        scores: List[float] = []

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            timestamp = idx / fps

            # BGR → RGB → PIL
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = PILImage.fromarray(rgb)

            # Per-frame analysis (sync helper)
            result = self._image_detector.analyze_pil_sync(pil_img, filename=f"frame_{idx}")
            frame_score = result.get("score", result.get("confidence", 0.0))
            scores.append(frame_score)

            # Face detection
            n_faces = self._count_faces(frame)
            face_counts.append(n_faces)

            frame_results.append({
                "frame_index": idx,
                "timestamp": round(timestamp, 2),
                "verdict": result.get("verdict", "unverified"),
                "score": round(frame_score, 4),
                "faces_detected": n_faces,
            })

        if not frame_results:
            return self._error_result("Could not read any frames from video.", filename)

        # --- Temporal analysis ----------------------------------------
        suspicious_moments: List[Dict[str, Any]] = []
        temporal_anomaly_score = 0.0

        if len(frame_results) >= MIN_FRAMES_FOR_TEMPORAL:
            temporal_anomaly_score, suspicious_moments = self._temporal_analysis(
                frame_results, face_counts, scores, fps
            )

        # --- Aggregate ------------------------------------------------
        mean_score = float(np.mean(scores)) if scores else 0.0
        max_score = float(np.max(scores)) if scores else 0.0

        final_score = 0.45 * mean_score + 0.25 * max_score + 0.30 * temporal_anomaly_score
        final_score = float(np.clip(final_score, 0.0, 1.0))

        verdict, explanation = self._interpret(final_score, len(frame_results), suspicious_moments)

        manipulated_frames = sum(1 for r in frame_results if r["verdict"] == "manipulated")
        suspicious_frames = sum(1 for r in frame_results if r["verdict"] == "suspicious")

        return {
            "id": str(uuid.uuid4()),
            "verdict": verdict,
            "confidence": round(
                final_score if verdict != "authentic" else 1.0 - final_score, 4
            ),
            "explanation": explanation,
            "evidence": [
                {
                    "type": "per_frame_analysis",
                    "description": (
                        f"Analyzed {len(frame_results)}/{total_frames} frames. "
                        f"{manipulated_frames} manipulated, {suspicious_frames} suspicious."
                    ),
                    "severity": round(mean_score, 4),
                },
                {
                    "type": "temporal_consistency",
                    "description": (
                        f"Temporal anomaly score: {temporal_anomaly_score:.3f}. "
                        f"{len(suspicious_moments)} suspicious moment(s)."
                    ),
                    "severity": round(temporal_anomaly_score, 4),
                },
            ],
            "frame_analysis": frame_results,
            "suspicious_moments": suspicious_moments,
            "metadata": {
                "filename": filename,
                "duration_seconds": round(duration, 2),
                "fps": round(fps, 2),
                "resolution": f"{width}x{height}",
                "total_frames": total_frames,
                "frames_analyzed": len(frame_results),
                "sample_interval": sample_interval,
            },
        }

    # ------------------------------------------------------------------
    # Internal — temporal analysis
    # ------------------------------------------------------------------
    def _temporal_analysis(
        self,
        frame_results: List[Dict],
        face_counts: List[int],
        scores: List[float],
        fps: float,
    ) -> Tuple[float, List[Dict[str, Any]]]:
        moments: List[Dict[str, Any]] = []
        anomaly_signals: List[float] = []

        for i in range(1, len(frame_results)):
            prev, curr = frame_results[i - 1], frame_results[i]

            fc_diff = abs(face_counts[i] - face_counts[i - 1])
            if fc_diff >= FACE_COUNT_JUMP_THRESHOLD:
                sev = min(fc_diff / 3.0, 1.0)
                moments.append({
                    "type": "face_count_change",
                    "timestamp": curr["timestamp"],
                    "frame_index": curr["frame_index"],
                    "detail": (
                        f"Face count {face_counts[i-1]}→{face_counts[i]} "
                        f"between frames {prev['frame_index']} and {curr['frame_index']}"
                    ),
                    "severity": round(sev, 2),
                })
                anomaly_signals.append(sev)

            score_diff = abs(scores[i] - scores[i - 1])
            if score_diff >= SCORE_JUMP_THRESHOLD:
                sev = min(score_diff, 1.0)
                moments.append({
                    "type": "score_flicker",
                    "timestamp": curr["timestamp"],
                    "frame_index": curr["frame_index"],
                    "detail": (
                        f"Deepfake score jumped by {score_diff:.2f} "
                        f"between frames {prev['frame_index']} and {curr['frame_index']}"
                    ),
                    "severity": round(sev, 2),
                })
                anomaly_signals.append(sev)

        score_std = float(np.std(scores)) if len(scores) > 1 else 0.0
        var_signal = float(np.clip(score_std * 2.0, 0.0, 1.0))

        if anomaly_signals:
            temporal_score = 0.5 * np.mean(anomaly_signals) + 0.5 * var_signal
        else:
            temporal_score = var_signal * 0.3

        return float(np.clip(temporal_score, 0.0, 1.0)), moments

    # ------------------------------------------------------------------
    # Internal — face detection
    # ------------------------------------------------------------------
    def _count_faces(self, frame_bgr) -> int:
        if self._face_cascade is None:
            return 0
        try:
            import cv2
            grey = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(
                grey, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            return len(faces)
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Internal — video I/O
    # ------------------------------------------------------------------
    @staticmethod
    def _open_video(video_input):
        import cv2

        tmp_path = None
        if isinstance(video_input, (str, Path)):
            path = str(video_input)
        elif isinstance(video_input, (bytes, bytearray)):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp.write(video_input)
            tmp.close()
            path = tmp.name
            tmp_path = tmp.name
        else:
            raise ValueError(f"Unsupported video input type: {type(video_input)}")

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"OpenCV could not open video: {path}")
        return cap, tmp_path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _interpret(score: float, frames_analyzed: int, moments: list) -> Tuple[str, str]:
        moment_str = f" {len(moments)} suspicious moment(s) in timeline." if moments else ""
        if score >= CONFIDENCE_THRESHOLD_MANIPULATED:
            return "manipulated", (
                f"High likelihood of video manipulation (score {score:.2f}). "
                f"Analyzed {frames_analyzed} frames.{moment_str} "
                "Per-frame and temporal analysis indicate alteration."
            )
        if score >= CONFIDENCE_THRESHOLD_SUSPICIOUS:
            return "suspicious", (
                f"Some manipulation indicators (score {score:.2f}). "
                f"Analyzed {frames_analyzed} frames.{moment_str} "
                "Partial signs; not conclusive."
            )
        return "authentic", (
            f"No strong manipulation signals (score {score:.2f}). "
            f"Analyzed {frames_analyzed} frames.{moment_str} "
            "The video appears authentic."
        )

    @staticmethod
    def _error_result(message: str, filename: str) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "verdict": "unverified",
            "confidence": 0.0,
            "explanation": message,
            "evidence": [],
            "frame_analysis": [],
            "suspicious_moments": [],
            "processing_time_ms": 0.0,
            "metadata": {"filename": filename, "error": True},
        }

    @staticmethod
    def _mock_result(filename: str) -> dict:
        import random

        n_frames = random.randint(8, 30)
        mock_score = round(random.uniform(0.25, 0.90), 4)

        if mock_score >= CONFIDENCE_THRESHOLD_MANIPULATED:
            verdict = "manipulated"
            explanation = (
                "Temporal inconsistencies and face-boundary artifacts detected "
                "across multiple frames, consistent with face-swap deepfake techniques."
            )
        elif mock_score >= CONFIDENCE_THRESHOLD_SUSPICIOUS:
            verdict = "suspicious"
            explanation = "Minor temporal anomalies detected; may indicate light editing or compression artifacts."
        else:
            verdict = "authentic"
            explanation = "No significant manipulation artifacts detected. Video appears authentic."

        frame_analysis = []
        for i in range(n_frames):
            fs = round(random.uniform(0.1, 0.85), 4)
            fv = "manipulated" if fs > 0.6 else ("suspicious" if fs > 0.35 else "authentic")
            frame_analysis.append({
                "frame_index": i * 15,
                "timestamp": round(i * 0.5, 2),
                "verdict": fv,
                "score": fs,
                "faces_detected": random.randint(0, 3),
            })

        suspicious_moments = []
        if verdict in ("manipulated", "suspicious"):
            for _ in range(random.randint(1, 4)):
                ts = round(random.uniform(0.5, n_frames * 0.5), 2)
                suspicious_moments.append({
                    "type": random.choice(["face_count_change", "score_flicker"]),
                    "timestamp": ts,
                    "frame_index": int(ts * 30),
                    "detail": f"[MOCK] Suspicious activity at {ts}s",
                    "severity": round(random.uniform(0.3, 1.0), 2),
                })

        return {
            "id": str(uuid.uuid4()),
            "verdict": verdict,
            "confidence": mock_score,
            "explanation": f"[MOCK] {explanation}",
            "evidence": [
                {
                    "type": "temporal_inconsistency",
                    "description": f"[MOCK] Analyzed {n_frames} frames",
                    "severity": round(random.uniform(0.3, 0.8), 2),
                },
                {
                    "type": "lip_sync_mismatch",
                    "description": "[MOCK] Audio-visual sync error rate 23%",
                    "severity": round(random.uniform(0.4, 0.8), 2),
                },
            ],
            "frame_analysis": frame_analysis,
            "suspicious_moments": suspicious_moments,
            "processing_time_ms": 0.0,
            "metadata": {
                "filename": filename,
                "mock": True,
                "duration_seconds": round(n_frames * 0.5, 2),
                "fps": 30.0,
                "resolution": "1920x1080",
                "total_frames": n_frames * 15,
                "frames_analyzed": n_frames,
                "sample_interval": 15,
            },
        }
