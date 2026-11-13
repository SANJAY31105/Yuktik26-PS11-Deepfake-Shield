# Frontend for PS11 Intelligence Platform

There are two ways to view the frontend interface:

### 1. Embedded Mission Control Dashboard (Recommended & Zero-Setup)
The full dashboard is served directly by the FastAPI backend at:
👉 **`http://localhost:8000/`** or **`http://localhost:8000/dashboard`**

Features:
- Live WebSocket alert feed
- Interactive Vis.js Coordinated Network Graph
- Multilingual Claim Verifier (EN / HI / TE)
- 1-Click "Trigger Dam Collapse Demo"
- Forensic Media Inspector (Audio spectral flatness, ELA image forensics)

### 2. Standalone React + Vite Frontend
To run the React development server:
```bash
npm install
npm run dev
```
Runs on `http://localhost:5173`.

