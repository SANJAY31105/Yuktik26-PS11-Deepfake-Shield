import asyncio, os, sys
from backend.ai_engine.image_detector import ImageDetector
from backend.ai_engine.audio_detector import AudioDetector
from backend.ai_engine.video_detector import VideoDetector

sys.stdout.reconfigure(line_buffering=True)

img_det = ImageDetector()
aud_det = AudioDetector()
vid_det = VideoDetector()

loop = asyncio.new_event_loop()

print("=== TESTING REAL FOLDER ===")
for f in sorted(os.listdir("jury_demo_data/REAL")):
    if not (f.endswith(".jpg") or f.endswith(".wav")):
        continue
    p = os.path.join("jury_demo_data/REAL", f)
    with open(p, "rb") as fp:
        b = fp.read()
    if f.endswith(".jpg"):
        res = loop.run_until_complete(img_det.analyze(b, f))
    elif f.endswith(".wav"):
        res = loop.run_until_complete(aud_det.analyze(b, f))
    v = res["verdict"]
    c = res["confidence"] * 100
    print(f"  {f:32} -> {v.upper():12} ({c:.1f}%)")
    assert v == "authentic", f"FAILED REAL: {f}"

print("\n=== TESTING FAKE FOLDER ===")
for f in sorted(os.listdir("jury_demo_data/FAKE")):
    if not (f.endswith(".jpg") or f.endswith(".wav") or f.endswith(".mp4")):
        continue
    p = os.path.join("jury_demo_data/FAKE", f)
    with open(p, "rb") as fp:
        b = fp.read()
    if f.endswith(".jpg"):
        res = loop.run_until_complete(img_det.analyze(b, f))
    elif f.endswith(".wav"):
        res = loop.run_until_complete(aud_det.analyze(b, f))
    elif f.endswith(".mp4"):
        res = loop.run_until_complete(vid_det.analyze(b, f))
    v = res["verdict"]
    c = res["confidence"] * 100
    print(f"  {f:38} -> {v.upper():12} ({c:.1f}%)")
    assert v in ("manipulated", "misleading"), f"FAILED FAKE: {f}"

print("\n>>> ALL REAL AND FAKE BENCHMARK FILES VERIFIED 100% CORRECT! <<<")
