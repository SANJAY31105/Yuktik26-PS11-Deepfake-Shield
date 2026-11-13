"""
Quick launcher for PS11 Backend Server
======================================
Usage: python run_server.py
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  PS11 — Real-Time Multimodal Deepfake Detection Platform")
    print("  Team: WARRIORS | Yuktik '26")
    print("  Starting FastAPI Server on http://localhost:8000 ...")
    print("  Interactive Docs available at http://localhost:8000/docs")
    print("=" * 65 + "\n")

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

