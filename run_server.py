"""
Quick launcher for SatyaShield AI Backend Server
=================================================
Usage: python run_server.py
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  SatyaShield AI — Real-Time Deepfake & Disinformation Defense")
    print("  Enterprise Autonomous Threat Intelligence System")
    print("  Starting FastAPI Server on http://localhost:8000 ...")
    print("  Interactive API Documentation at http://localhost:8000/docs")
    print("=" * 65 + "\n")

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

