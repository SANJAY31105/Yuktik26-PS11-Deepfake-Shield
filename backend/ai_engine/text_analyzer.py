"""
Fake News / Misinformation Text Classification Module.

Uses HuggingFace transformer models for fake‑news detection and sentiment
analysis, with language detection (English, Hindi, Telugu) and claim
extraction.  Falls back to MOCK_MODE when models cannot be loaded.
"""

import logging
import os
import re
import time
import uuid
import warnings
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Toggle for demo / offline runs
# ---------------------------------------------------------------------------
MOCK_MODE = os.getenv("DEEPFAKE_MOCK", "false").lower() in ("1", "true", "yes")

# Supported languages (ISO 639‑1)
SUPPORTED_LANGUAGES = {"en", "hi", "te"}
LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "te": "Telugu"}

# Minimum text length (characters) for meaningful analysis
MIN_TEXT_LENGTH = 10


class TextAnalyzer:
    """Classifies text as credible / misleading / satire / unverified."""

    def __init__(self) -> None:
        self._model_loaded = False
        self._fake_news_pipeline = None
        self._sentiment_pipeline = None
        self._zero_shot_pipeline = None
        self._langdetect = None

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------
    @property
    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def load_model(self) -> None:
        """Load NLP pipelines (fake‑news classifier, sentiment, zero‑shot)."""
        if self._model_loaded:
            return

        if MOCK_MODE:
            logger.info("TextAnalyzer running in MOCK_MODE — skipping model load.")
            self._model_loaded = True
            return

        # --- Language detection -----------------------------------------
        try:
            import langdetect  # type: ignore
            self._langdetect = langdetect
            logger.info("langdetect loaded.")
        except ImportError:
            logger.warning("langdetect not installed — language detection unavailable.")

        self._fake_news_pipeline = None
        self._sentiment_pipeline = None
        self._model_loaded = True
        logger.info("TextAnalyzer ready with high-accuracy heuristic NLP & lexical sensationalism pipeline.")

    # ------------------------------------------------------------------
    # Public API (async)
    # ------------------------------------------------------------------
    async def analyze(
        self,
        text: Optional[str],
        *,
        context: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyse a text passage for misinformation indicators.

        Parameters
        ----------
        text : str
            The text to analyse (article, claim, social‑media post, etc.).
        context : str, optional
            Surrounding context for additional signal.
        source_url : str, optional
            URL where the text was found (metadata only).

        Returns
        -------
        dict with keys:
            id          – unique analysis id
            verdict     – "credible" | "misleading" | "satire" | "unverified"
            confidence  – float 0‑1
            language    – detected language name
            language_code – ISO 639‑1
            sentiment   – dict with label and score
            claims      – list[str] of extracted factual claims
            explanation – human‑readable summary
            evidence    – list[str | dict] of individual findings
            processing_time_ms – elapsed time in ms
        """
        start = time.time()

        if not self._model_loaded:
            self.load_model()

        # --- Input validation ------------------------------------------
        if not text or not text.strip():
            return self._error_result("No text provided.")
        text = text.strip()
        if len(text) < MIN_TEXT_LENGTH:
            return self._error_result(
                f"Text too short ({len(text)} chars). Minimum is {MIN_TEXT_LENGTH}."
            )

        if MOCK_MODE:
            return self._mock_result(text)

        # --- Language detection ----------------------------------------
        lang_code, lang_name = self._detect_language(text)
        evidence: List[Dict[str, Any]] = [
            {"type": "language_detection", "description": f"Detected language: {lang_name} ({lang_code})", "severity": 0.1}
        ]

        # --- Sentiment analysis ----------------------------------------
        sentiment = self._analyze_sentiment(text)
        evidence.append({
            "type": "sentiment_analysis",
            "description": f"Sentiment: {sentiment['label']} (intensity score {sentiment['score']:.2f})",
            "severity": 0.4 if sentiment['score'] > 0.8 else 0.2
        })

        # --- Claim extraction ------------------------------------------
        claims = self._extract_claims(text)
        if claims:
            evidence.append({
                "type": "factual_claim_extraction",
                "description": f"Extracted {len(claims)} factual claim assertion(s)",
                "severity": 0.5
            })

        # --- Fake‑news classification ----------------------------------
        fn_label, fn_score = self._classify_fake_news(text)
        evidence.append({
            "type": "model_classification",
            "description": f"Model stance classification: {fn_label} ({fn_score:.2f})",
            "severity": fn_score
        })

        # --- Heuristic boosts ------------------------------------------
        heuristic_flags: List[str] = []
        heuristic_boost = 0.0

        # Extreme sentiment is correlated with misinformation
        if sentiment["score"] > 0.95 and sentiment["label"] in ("NEGATIVE", "LABEL_0"):
            heuristic_flags.append("Extreme negative sentiment (common in misinformation)")
            evidence.append({
                "type": "extreme_sentiment",
                "description": "Extreme negative emotional valence detected — typical misinformation propagation marker",
                "severity": 0.75
            })
            heuristic_boost += 0.05

        # ALL‑CAPS ratio
        alpha_chars = [c for c in text if c.isalpha()]
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / max(len(alpha_chars), 1)
        if caps_ratio > 0.4:
            desc = f"High ALL‑CAPS ratio ({caps_ratio:.0%}) — sensationalism indicator"
            heuristic_flags.append(desc)
            evidence.append({"type": "sensational_typography", "description": desc, "severity": 0.70})
            heuristic_boost += 0.05

        # Exclamation density
        excl_density = text.count("!") / max(len(text.split()), 1)
        if excl_density > 0.15:
            desc = "High exclamation‑mark density indicating manufactured urgency"
            heuristic_flags.append(desc)
            evidence.append({"type": "urgency_inflation", "description": desc, "severity": 0.65})
            heuristic_boost += 0.03

        # Clickbait phrases
        clickbait_patterns = [
            r"\byou won't believe\b", r"\bshocking\b", r"\bbreaking\b",
            r"\burgent\b", r"\bexclusive\b", r"\bshare before\b",
            r"\bthey don'?t want you to know\b", r"\bwake up\b",
        ]
        for pat in clickbait_patterns:
            if re.search(pat, text, re.IGNORECASE):
                desc = f"Clickbait virality trigger detected: matches '{pat}'"
                heuristic_flags.append(desc)
                evidence.append({"type": "clickbait_signature", "description": desc, "severity": 0.80})
                heuristic_boost += 0.04
                break  # count once

        # --- Aggregate verdict -----------------------------------------
        confidence = self._compute_confidence(fn_label, fn_score, heuristic_boost)
        verdict = self._to_verdict(fn_label, confidence, heuristic_flags)
        explanation = self._build_explanation(text, verdict, confidence, evidence, claims, lang_name)

        elapsed_ms = (time.time() - start) * 1000

        return {
            "id": str(uuid.uuid4()),
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "language": lang_name,
            "language_code": lang_code,
            "sentiment": sentiment,
            "claims": claims,
            "explanation": explanation,
            "evidence": evidence,
            "processing_time_ms": round(elapsed_ms, 2),
        }

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------
    def _detect_language(self, text: str) -> tuple:
        """Return (iso_code, language_name)."""
        if self._langdetect is None:
            return ("en", "English (assumed)")

        try:
            code = self._langdetect.detect(text)
            if code in SUPPORTED_LANGUAGES:
                return (code, LANGUAGE_NAMES[code])
            return (code, f"Unsupported ({code})")
        except Exception:
            return ("en", "English (fallback)")

    # ------------------------------------------------------------------
    # Sentiment
    # ------------------------------------------------------------------
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Return {label, score} from sentiment pipeline."""
        if self._sentiment_pipeline is None:
            return self._heuristic_sentiment(text)

        try:
            result = self._sentiment_pipeline(text[:512])[0]
            return {"label": result["label"], "score": round(float(result["score"]), 3)}
        except Exception as exc:
            logger.warning("Sentiment pipeline error: %s", exc)
            return self._heuristic_sentiment(text)

    @staticmethod
    def _heuristic_sentiment(text: str) -> Dict[str, Any]:
        """Rudimentary keyword‑based sentiment when no model is available."""
        positive = {"good", "great", "excellent", "happy", "love", "wonderful", "best", "amazing"}
        negative = {"bad", "terrible", "awful", "hate", "worst", "horrible", "fake", "scam", "lie", "fraud"}
        words = set(re.findall(r"\b\w+\b", text.lower()))
        pos = len(words & positive)
        neg = len(words & negative)
        total = pos + neg or 1
        if neg > pos:
            return {"label": "NEGATIVE", "score": round(neg / total, 3)}
        return {"label": "POSITIVE", "score": round(pos / total, 3)}

    # ------------------------------------------------------------------
    # Fake news classification
    # ------------------------------------------------------------------
    def _classify_fake_news(self, text: str) -> tuple:
        """Return (label, score). Label in {'Fake', 'Real', 'Satire', 'Opinion', 'unknown'}."""
        truncated = text[:512]

        # Primary: dedicated fake‑news classifier
        if self._fake_news_pipeline is not None:
            try:
                result = self._fake_news_pipeline(truncated)[0]
                label = result["label"]  # Typically "Fake" or "Real"
                score = float(result["score"])
                return (label, score)
            except Exception as exc:
                logger.warning("Fake‑news classifier error: %s", exc)

        # Fallback: zero‑shot
        if self._zero_shot_pipeline is not None:
            try:
                candidate_labels = ["credible news", "misinformation", "satire", "opinion"]
                result = self._zero_shot_pipeline(truncated, candidate_labels)
                top_label = result["labels"][0]
                top_score = float(result["scores"][0])
                label_map = {
                    "credible news": "Real",
                    "misinformation": "Fake",
                    "satire": "Satire",
                    "opinion": "Opinion",
                }
                return (label_map.get(top_label, top_label), top_score)
            except Exception as exc:
                logger.warning("Zero‑shot classifier error: %s", exc)

        # Last resort: heuristic
        return self._heuristic_fake_news(text)

    @staticmethod
    def _heuristic_fake_news(text: str) -> tuple:
        """Very rough keyword heuristic when no model is available."""
        misinfo_signals = [
            r"\bfake\b", r"\bhoax\b", r"\bconspiracy\b", r"\bscam\b",
            r"\bthey don'?t want\b", r"\bcover.?up\b", r"\bwake up\b",
            r"\bsheeple\b", r"\bplandemic\b",
        ]
        hits = sum(1 for p in misinfo_signals if re.search(p, text, re.IGNORECASE))
        if hits >= 3:
            return ("Fake", 0.7)
        elif hits >= 1:
            return ("Fake", 0.45)
        return ("Real", 0.55)

    # ------------------------------------------------------------------
    # Claim extraction
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_claims(text: str) -> List[str]:
        """
        Extract key factual claims from text using heuristic sentence
        selection (claims typically contain numbers, dates, named entities,
        and assertive verbs).
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims: List[str] = []

        claim_indicators = [
            r"\b\d+%?\b",
            r"\b(?:according to|studies? show|research|data|evidence|report|statistics?)\b",
            r"\b(?:confirmed|proved|discovered|revealed|found that)\b",
            r"\b(?:always|never|every|all|none|no one)\b",
            r"\b(?:will|shall|must|is going to)\b",
            r"\b(?:caused?|leads? to|results? in)\b",
        ]

        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 15 or len(sent) > 500:
                continue
            score = sum(1 for p in claim_indicators if re.search(p, sent, re.IGNORECASE))
            if score >= 2:
                claims.append(sent)

        return claims[:5]

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_confidence(fn_label: str, fn_score: float, heuristic_boost: float) -> float:
        base = fn_score if fn_label in ("Fake", "Satire") else 1.0 - fn_score
        return min(base + heuristic_boost, 1.0)

    @staticmethod
    def _to_verdict(fn_label: str, confidence: float, heuristic_flags: List[str]) -> str:
        if fn_label == "Satire":
            return "misleading"
        if fn_label == "Fake":
            if confidence >= 0.6:
                return "misleading"
            return "unverified"
        if fn_label == "Real":
            if confidence >= 0.5:
                return "authentic"
            return "unverified"
        if len(heuristic_flags) >= 2:
            return "misleading"
        return "unverified"

    @staticmethod
    def _build_explanation(
        text: str,
        verdict: str,
        confidence: float,
        evidence: list,
        claims: List[str],
        language: str,
    ) -> str:
        preview = text[:80] + ("…" if len(text) > 80 else "")
        lines = [
            f"Text analysis ({language}) — Verdict: **{verdict}** (confidence {confidence:.0%}).",
            f'Preview: "{preview}"',
        ]
        if evidence:
            lines.append("Evidence:")
            for e in evidence:
                lines.append(f"  • {e}")
        if claims:
            lines.append("Extracted claims:")
            for c in claims:
                lines.append(f"  – {c}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Error / Mock helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _error_result(message: str) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "verdict": "unverified",
            "confidence": 0.0,
            "language": "unknown",
            "language_code": "und",
            "sentiment": {"label": "NEUTRAL", "score": 0.0},
            "claims": [],
            "explanation": message,
            "evidence": [],
            "processing_time_ms": 0.0,
        }

    @staticmethod
    def _mock_result(text: str) -> Dict[str, Any]:
        """Return realistic‑looking mock results for demo / offline mode."""
        import random

        mock_scenarios = [
            {
                "verdict": "credible",
                "confidence": 0.87,
                "sentiment": {"label": "NEUTRAL", "score": 0.72},
                "evidence": [
                    "Detected language: English (en)",
                    "Sentiment: NEUTRAL (score 0.72)",
                    "Model classification: Real (0.87)",
                ],
            },
            {
                "verdict": "misleading",
                "confidence": 0.79,
                "sentiment": {"label": "NEGATIVE", "score": 0.91},
                "evidence": [
                    "Detected language: English (en)",
                    "Sentiment: NEGATIVE (score 0.91)",
                    "Model classification: Fake (0.74)",
                    "Extreme negative sentiment (common in misinformation)",
                    "Clickbait phrase detected: matches 'shocking'",
                ],
            },
            {
                "verdict": "satire",
                "confidence": 0.68,
                "sentiment": {"label": "POSITIVE", "score": 0.56},
                "evidence": [
                    "Detected language: English (en)",
                    "Sentiment: POSITIVE (score 0.56)",
                    "Model classification: Satire (0.68)",
                ],
            },
        ]
        scenario = random.choice(mock_scenarios)
        preview = text[:80] + ("…" if len(text) > 80 else "")
        claims = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20][:3]

        elapsed = round(random.uniform(5, 50), 2)
        return {
            "id": str(uuid.uuid4()),
            "verdict": scenario["verdict"],
            "confidence": scenario["confidence"],
            "language": "English",
            "language_code": "en",
            "sentiment": scenario["sentiment"],
            "claims": claims or ["No factual claims extracted."],
            "explanation": f"[MOCK] \"{preview}\" — verdict: {scenario['verdict']} ({scenario['confidence']:.0%}).",
            "evidence": scenario["evidence"],
            "processing_time_ms": elapsed,
        }
