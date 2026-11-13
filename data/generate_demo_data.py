"""
Generates synthetic demo media files for PS11 Scenario 2 testing.
"""

import io
import wave
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).resolve().parent

def generate_audio():
    """Generates a synthetic voice-clone test wav with vocoder high-frequency artifacts."""
    sr = 16000
    duration = 3.0  # seconds
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Carrier fundamental frequency (collector voice imitation)
    f0 = 130.0  # typical adult male pitch
    carrier = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * 2 * f0 * t) + 0.3 * np.sin(2 * np.pi * 3 * f0 * t)

    # Add unnatural robotic high-frequency vocoder hiss in 4-8 kHz
    vocoder_artifact = 0.15 * np.sin(2 * np.pi * 5500 * t) * np.sin(2 * np.pi * 20 * t)

    signal = carrier + vocoder_artifact
    signal = signal / np.max(np.abs(signal))  # Normalize
    audio_int16 = (signal * 32767).astype(np.int16)

    out_path = DATA_DIR / "collector_evacuation_voice_clone.wav"
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    print(f"Generated demo audio: {out_path}")

def generate_image():
    """Generates a demo image representing the 2018 flood photograph."""
    img = Image.new("RGB", (640, 480), color=(45, 75, 95))
    draw = ImageDraw.Draw(img)

    # Draw water flood waves
    for y in range(250, 480, 20):
        draw.line([(0, y), (640, y + 10)], fill=(70, 110, 140), width=8)

    # Draw submerged structures
    draw.rectangle([(100, 200), (220, 380)], fill=(120, 100, 80))
    draw.polygon([(100, 200), (160, 140), (220, 200)], fill=(150, 50, 50))

    # Add text banner
    draw.rectangle([(0, 0), (640, 50)], fill=(20, 20, 20))
    draw.text((20, 15), "ARCHIVED INCIDENT: 2018 FLOOD DISASTER RECORD", fill=(240, 240, 240))

    out_path = DATA_DIR / "kerala_flood_reused_photo.jpg"
    img.save(out_path, format="JPEG", quality=85)
    print(f"Generated demo flood photo: {out_path}")

def generate_incident_json():
    """Generates Scenario 2 complete incident json payload."""
    payload = {
        "incident_title": "Yuktik-2026 PS11 Benchmark: Dam Collapse Disinformation Campaign",
        "description": "At 10:00 AM, a video circulated claiming major dam collapse near a city...",
        "posts": [
            {
                "account": "@breaking_hyd_alert",
                "lang": "en",
                "caption": "URGENT: Nagarjuna Sagar Dam collapsed! City under immediate danger! #DamCollapse",
                "timestamp": "10:00 AM",
                "media_type": "video"
            },
            {
                "account": "@telangana_now24",
                "lang": "te",
                "caption": "నిజాంసాగర్ డ్యామ్ గేట్లు కొట్టుకుపోయాయి! వెంటనే ఖాళీ చేయండి!",
                "timestamp": "10:02 AM",
                "media_type": "video"
            },
            {
                "account": "@bharat_samachar_live",
                "lang": "hi",
                "caption": "बड़ा बांध टूटा! शहर में जल प्रलय की चेतावनी, तुरंत सुरक्षित स्थान पर पहुंचे!",
                "timestamp": "10:05 AM",
                "media_type": "video"
            }
        ]
    }
    out_path = DATA_DIR / "scenario2_benchmark_incident.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Generated incident json: {out_path}")

def generate_video():
    """Generates a demo 3-second MP4 video fixture simulating deepfake official announcement."""
    try:
        import cv2
        out_path = DATA_DIR / "official_announcement_fake.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(out_path), fourcc, 30.0, (640, 480))

        for frame_idx in range(90):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (35, 45, 55)  # dark blue-grey studio background

            # Jittering face bounding box (simulating deepfake face-swap boundary artifact)
            jitter_x = int(np.sin(frame_idx * 0.4) * 8)
            jitter_y = int(np.cos(frame_idx * 0.3) * 6)
            cv2.rectangle(frame, (240 + jitter_x, 120 + jitter_y), (400 + jitter_x, 320 + jitter_y), (80, 140, 180), -1)
            cv2.circle(frame, (290 + jitter_x, 190 + jitter_y), 15, (220, 220, 220), -1)
            cv2.circle(frame, (350 + jitter_x, 190 + jitter_y), 15, (220, 220, 220), -1)
            cv2.ellipse(frame, (320 + jitter_x, 260 + jitter_y), (35, 15), 0, 0, 180, (40, 40, 120), -1)

            # Banner
            cv2.rectangle(frame, (0, 420), (640, 480), (10, 10, 10), -1)
            cv2.putText(frame, "LIVE: DISTRICT MAGISTRATE BRIEFING (AI SIMULATED)", (20, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

            out.write(frame)

        out.release()
        print(f"Generated demo video: {out_path}")
    except Exception as exc:
        print(f"Could not generate demo video: {exc}")

if __name__ == "__main__":
    generate_audio()
    generate_image()
    generate_video()
    generate_incident_json()

