# Yuktik ’26 — Team WARRIORS
## Problem Statement 11: Real-Time Multimodal Deepfake Detection and Coordinated Misinformation Intelligence Platform

Department of CSE (AI&ML), Keshav Memorial Institute of Technology (KMIT), Hyderabad.

---

## 📌 Executive Summary

Modern misinformation campaigns do not rely on a single isolated post. As seen in coordinated digital propaganda, adversaries simultaneously deploy:
1. **AI-generated voice clones** impersonating government officials.
2. **Face-swapped / lip-synced deepfake videos** fabricating disaster announcements.
3. **Outdated photographs** from past disasters misattributed to current events.
4. **Synchronized bot syndicates** distributing content in multiple regional languages (**English, Hindi, Telugu**).

Existing fake-news solutions classify posts in isolation. **PS11 by Team WARRIORS** is an end-to-end intelligence platform that **correlates cross-modal evidence across media, accounts, timelines, and languages** to identify synthetic artifacts, detect coordinated astroturfing rings, and verify claims against authoritative ground truth.

---

## 🏆 Evaluation Criteria Scorecard (100% Coverage)

| Evaluation Parameter | Weight | WARRIORS Solution & Implementation |
|---|---|---|
| **Multimodal AI Detection Performance** | **20%** | Image Error Level Analysis (ELA) + ViT features + Acoustic FFT spectral flatness for voice clone detection + OpenCV frame temporal jitter analysis. |
| **Claim Verification & Contextual Reasoning** | **20%** | RAG-based knowledge retrieval against Central Water Commission (CWC), NDMA, and District Collectorate records with 4 distinct verdict classes (`Verified`, `Contradicted`, `Misleading`, `Unverified`). |
| **Coordinated Network Detection** | **15%** | NetworkX graph analysis: Identifies synchronized temporal bursts (<180s), cross-account media reuse with divergent captions, degree/betweenness centrality, and Louvain bot community detection. |
| **Real-Time Web Integration** | **15%** | High-throughput asynchronous FastAPI backend + WebSocket live alert streaming (`/ws/alerts`) for immediate security operations dispatch. |
| **Multilingual Capability** | **10%** | Automated script and entity analysis supporting **English, Hindi (Devanagari), and Telugu** claims. |
| **Explainability & Evidence Traceability** | **10%** | Every prediction returns a structured `evidence` array with severity scores, technical metrics (spectral flatness index, Hamming distance, centrality), and official citation URLs. |
| **System Architecture & Scalability** | **5%** | Asynchronous non-blocking architecture, SQLite/ChromaDB indexing, and graceful offline fallback heuristics. |
| **UI/UX Readiness** | **5%** | Standardized JSON schemas ready for React/Next.js dashboard, graph visualization (Cytoscape/ForceGraph), and 1-click live demo simulation. |
| **TOTAL** | **100%** | **Fully functional prototype tested and passing all test suites.** |

---

## 🌊 Resolution of the Yuktik '26 Tricky Real-World Scenario

**Scenario Specification:**
> *"At 10:00 AM, a video begins circulating on social media claiming that a major dam near a city has collapsed... an AI-generated audio announces evacuation... multiple accounts share the same video with different captions... an old photograph of a flood from another state is presented... a manipulated video shows an official... an authentic government update contradicts... spreading in English, Hindi, and Telugu."*

### How Our Platform Correlates the Incident:

```
                           [10:00 AM INGESTION FEED]
                                      │
         ┌───────────────────┬────────┴──────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
   [Video Engine]      [Audio Engine]     [Reverse Image]     [NLP Multilingual]
   Face artifact       HiFi-GAN vocoder   dHash / pHash       Script & Entity
   lip-sync jitter     spectral flatness  2018 Kerala Flood   EN, HI, TE claims
   (Score: 0.90)       (Score: 0.86)      Match (97.1% sim)   (Score: 0.88)
         │                   │                   │                   │
         └───────────────────┴────────┬──────────┴───────────────────┘
                                      ▼
                        [NetworkX Graph Intelligence]
                        - Shared Media Hash Across Disjoint Accounts
                        - Synchronized Temporal Burst (<180s)
                        - Louvain Bot Rings & Amplifier Nodes
                                      │
                                      ▼
                        [RAG Claim Verification Engine]
                        - Ground Truth: Central Water Commission Bulletin
                        - Finding: Reservoir Level 44.2% Normal, Spillways Intact
                        - Order: District Magistrate: NO EVACUATION ORDERED
                                      │
                                      ▼
                     [Multimodal Cross-Modal Correlator]
        ┌─────────────────────────────────────────────────────────────┐
        │  • Audio vs Authority: Fake evacuation vs Collector Order   │
        │  • Visual vs Ground Truth: 2018 photo vs Current dry dam    │
        │  • Dissemination: 3 Coordinated Bot Syndicates (EN/HI/TE)   │
        │                                                             │
        │  FINAL VERDICT: CONTRADICTED | THREAT: CRITICAL (0.88 conf) │
        └─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                   [WebSocket Live Dispatch: /ws/alerts]
```

---

## 📁 Repository Structure

```
Deepfake/
├── backend/
│   ├── main.py                  # FastAPI application entry point with CORS & routes
│   ├── config.py                # Platform configurations & thresholds
│   ├── requirements.txt         # Production dependencies
│   ├── test_suite.py            # Automated test suite (9 test suites)
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   ├── image_detector.py    # ELA (Error Level Analysis), noise variance, ViT features
│   │   ├── video_detector.py    # Temporal consistency, frame sampling, Haar face detection
│   │   ├── audio_detector.py    # FFT spectral flatness, neural vocoder detection
│   │   ├── text_analyzer.py     # NLP multilingual classification (EN, HI, TE)
│   │   ├── reverse_image.py     # Perceptual dHash/pHash historical disaster detection
│   │   ├── network_analyzer.py  # NetworkX CIB, Louvain communities, amplifier nodes
│   │   ├── claim_verifier.py    # RAG knowledge base & authority contradiction analysis
│   │   └── multimodal_correlator.py # Cross-modal contradiction fusion & incident intelligence
│   ├── api/
│   │   ├── websocket.py         # Real-time WebSocket connection manager & alerts
│   │   └── routes/
│   │       ├── media.py         # Image, video, audio upload & deepfake analysis
│   │       ├── claims.py        # Text & claim verification endpoints
│   │       ├── network.py       # Social network graph & scenario endpoints
│   │       ├── incident.py      # Scenario 2 benchmark simulation & correlation
│   │       └── dashboard.py     # Real-time stats & health checks
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   └── db/
│       └── database.py          # SQLite persistence engine
├── data/
│   ├── generate_demo_data.py    # Script generating test fixtures
│   ├── collector_evacuation_voice_clone.wav # Synthetic voice demo audio
│   ├── kerala_flood_reused_photo.jpg        # Reused flood photo demo
│   └── scenario2_benchmark_incident.json    # Full scenario incident payload
├── run_server.py                # 1-Click server launcher
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Run the Automated Test Suite
To verify all 9 test suites and the benchmark scenario:
```bash
python backend/test_suite.py
```
*Expected output: All 9 test suites pass with `Exit code 0`.*

### 2. Start the Backend Server
```bash
python run_server.py
```
The server will start on `http://localhost:8000`.
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Trigger 1-Click Benchmark Scenario Demo
Make a GET request in your browser or curl:
```bash
curl http://localhost:8000/api/v1/incident/scenario-demo
```
This executes the entire Dam Collapse multimodal scenario end-to-end and broadcasts a real-time critical alert across WebSocket connections!

---

## 📡 Core API Reference

| Endpoint | Method | Input | Description |
|---|---|---|---|
| `/api/v1/incident/scenario-demo` | `GET` | None | **Live benchmark demo of the Yuktik '26 Dam Collapse scenario**. |
| `/api/v1/media/analyze` | `POST` | Multipart File | Analyzes image, video, or audio for synthetic manipulation. |
| `/api/v1/media/reverse-search` | `POST` | Multipart File | Detects reused historical disaster images using perceptual hashing. |
| `/api/v1/claims/verify` | `POST` | JSON (`claim`, `language`) | Verifies claims in English, Hindi, or Telugu against official sources. |
| `/api/v1/claims/analyze-text` | `POST` | JSON (`claim`) | NLP emotional manipulation and clickbait detection. |
| `/api/v1/network/scenario` | `GET` | None | Returns graph nodes & edges of the coordinated bot network. |
| `/api/v1/network/analyze` | `POST` | JSON (`content_ids`, `accounts`) | Analyzes custom social media network for coordinated behavior. |
| `/api/v1/dashboard/stats` | `GET` | None | Real-time aggregate statistics for the command dashboard. |
| `/ws/alerts` | `WebSocket` | WebSocket Client | Real-time incident alert broadcast stream. |

---

## 🔬 AI Engine Technical Details

### 1. Audio Voice Clone Detection (`audio_detector.py`)
Neural vocoders (such as HiFi-GAN, WaveGlow, MelGAN, and VITS) synthesize speech by reconstructing audio from mel-spectrograms. This process leaves measurable mathematical signatures:
- **Spectral Flatness Measure ($SFM$):**
  $$SFM = \frac{\exp\left(\frac{1}{N}\sum_{k=1}^N \ln |X(k)|\right)}{\frac{1}{N}\sum_{k=1}^N |X(k)|}$$
  Synthetic vocoders exhibit unnaturally elevated flatness in the 4–8 kHz band compared to organic vocal tract acoustic roll-off.
- **Micro-tremor Absence:** Human vocal cords produce natural involuntary frequency and amplitude perturbations (jitter and shimmer). Voice clones display rigid zero-crossing rate variance ($ZCR_{var} < 0.008$).

### 2. Reverse Image & Reused Media Detection (`reverse_image.py`)
To catch outdated photographs presented as current breaking news:
- **dHash (Difference Hash):** Resizes image to $9 \times 8$ grayscale, calculates row-wise gradients, and produces a 64-bit structural fingerprint invariant to JPEG compression and color grading.
- **Hamming Distance Indexing:** Compares hashes against historical archives. A distance $d_H \le 14$ accurately flags reused media from past incidents (e.g., 2018 Kerala floods).

### 3. Coordinated Inauthentic Network Detection (`network_analyzer.py`)
- **Temporal Burst Edge Formulation:** Connects accounts posting about an incident within $\Delta t \le 180\text{ seconds}$.
- **Cross-Account Media Hash Edge:** Connects disjoint accounts that share identical media hashes with divergent captions (e.g. English, Hindi, Telugu variants).
- **Graph Centrality & Community Detection:** Uses Greedy Modularity Maximization (Louvain approximation) to isolate bot syndicates, and Betweenness Centrality to pinpoint coordinating amplifier nodes.

---

## 👥 Team WARRIORS
- **Event**: Yuktik ’26 (13 November 2026)
- **Institution**: Keshav Memorial Institute of Technology (KMIT), Hyderabad
- **Department**: CSE (Artificial Intelligence & Machine Learning)
