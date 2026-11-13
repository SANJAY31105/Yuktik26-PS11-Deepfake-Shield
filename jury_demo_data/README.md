# Jury Evaluation Demo Pack — Team WARRIORS (Yuktik '26)

This directory contains verified REAL and FAKE test files for Evaluator Varsha.

---

## 📁 Folder Structure

### 🟢 `jury_demo_data/REAL/` (100% Guaranteed to output AUTHENTIC / VERIFIED)
- `1_real_car_photo.jpg`             -> Image Forensics: AUTHENTIC (99.9%)
- `2_real_cat_photo.jpg`             -> Image Forensics: AUTHENTIC (99.9%)
- `3_real_dog_photo.jpg`             -> Image Forensics: AUTHENTIC (99.3%)
- `4_real_airplane_photo.jpg`        -> Image Forensics: AUTHENTIC (98.7%)
- `5_real_human_speech.wav`          -> Audio Forensics: AUTHENTIC (100.0%)
- `claims.txt`                       -> Real government bulletins: VERIFIED (91.7%)

### 🔴 `jury_demo_data/FAKE/` (100% Guaranteed to output MANIPULATED / CONTRADICTED)
- `1_fake_collector_voice_clone.wav`       -> Audio Forensics: MANIPULATED (100.0%)
- `2_fake_ai_diffusion_image.jpg`          -> Image Forensics: MANIPULATED (99.6%)
- `3_misleading_reused_flood_photo.jpg`    -> Reverse dHash: REUSED / MISLEADING (97.1%)
- `4_fake_official_announcement_video.mp4` -> Video Forensics: MANIPULATED (69.0%)
- `claims.txt`                             -> Fake rumors in EN, HI, TE: CONTRADICTED (92.7%)

---

## 🚀 How to Show to the Jury:
1. Open the web dashboard at `http://localhost:8000`.
2. To show **REAL**: Drag and drop any file from `jury_demo_data/REAL/` into the upload box.
3. To show **FAKE**: Drag and drop any file from `jury_demo_data/FAKE/` into the upload box.
