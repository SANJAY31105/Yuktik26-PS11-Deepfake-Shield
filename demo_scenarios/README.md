# Team WARRIORS — Live Demo Scenarios & Jury Explanation Pack

This folder contains **3 complete pre-packaged crisis scenarios** with verified REAL and FAKE data.

---

## 📁 Directory Structure & Files

- `scenario1_disaster_hoax/` (Nagarjuna Sagar Dam Collapse Hoax)
  - `1_FAKE_collector_evacuation_voice.wav` -> Cloned voice ordering evacuation (MANIPULATED: 100.0%)
  - `2_REAL_collector_speech.wav` -> Natural human speech from LibriSpeech (AUTHENTIC: 100.0%)
  - `3_FAKE_ai_synthetic_flood.jpg` -> Stable Diffusion AI visual (MANIPULATED: 99.6%)
  - `4_MISLEADING_reused_2018_flood.jpg` -> 2018 Kerala flood photo (REUSED ARCHIVE: 97.1%)
  - `5_REAL_camera_photo.jpg` -> Natural camera photo (AUTHENTIC: 99.9%)
  - `claims.txt` -> English, Hindi, and Telugu claims for copy-pasting

- `scenario2_election_curfew/` (Election / Public Figure Impersonation)
  - `1_FAKE_cloned_curfew_audio.wav` (MANIPULATED: 100.0%)
  - `2_REAL_press_statement_audio.wav` (AUTHENTIC: 100.0%)
  - `3_FAKE_ai_riot_photo.jpg` (MANIPULATED: 99.6%)
  - `4_REAL_press_conference_photo.jpg` (AUTHENTIC: 99.9%)
  - `claims.txt`

- `scenario3_bank_run_panic/` (Financial Panic / Bank Run)
  - `1_FAKE_cloned_bank_freeze_audio.wav` (MANIPULATED: 100.0%)
  - `2_REAL_rbi_governor_briefing_audio.wav` (AUTHENTIC: 100.0%)
  - `3_FAKE_ai_crowd_protest.jpg` (MANIPULATED: 99.6%)
  - `4_REAL_bank_headquarters_photo.jpg` (AUTHENTIC: 99.9%)
  - `claims.txt`

---

## 🧠 Why Pre-trained Models Alone Give False Positives (How to Explain to the Jury)

If the evaluator asks: *"Why did a random image or microphone recording get flagged as manipulated?"*

### 1. The Vision Transformer (`dima806/ai_vs_real_image_detection`)
- **Root Cause**: This model was fine-tuned on the **CIFAKE dataset** ($32\times32$ CIFAR-10 images upscaled to $224\times224$). CIFAR-10 consists of tiny low-resolution objects.
- **Why Google Images fail**: Modern Google Images and phone camera JPEGs have high-resolution edge details, multi-pass web recompression, and HDR tone mapping. Because this distribution deviates heavily from the low-resolution CIFAKE training distribution, the model encounters **Domain Shift (Out-of-Distribution Error)**.
- **Our Engineering Innovation**: We do not rely on ViT alone. We combine it with **64-bit dHash reverse matching** and **JPEG Error Level Analysis (ELA)**. If an image is a genuine camera photo from 2018, ViT cannot detect it, but our dHash engine catches the 2-bit Hamming distance to historical disaster records!

### 2. The Audio Wav2Vec 2.0 Model (`MelodyMachine/Deepfake-audio-detection-V2`)
- **Root Cause**: The model is trained on studio-quality speech (In-the-Wild & ASVspoof benchmarks at 16 kHz).
- **Why Live Mic Recordings fail**: Speaking close to a laptop or phone microphone creates **digital clipping, ambient room reverb, and plosive distortion** (e.g. saying *"Taj"* or *"Destroyed"* into a cheap mic creates high-frequency acoustic spikes). The model misinterprets this microphone noise as neural vocoder phase artifacts.
- **Our Engineering Innovation**: We compute **subband Spectral Flatness (4–8 kHz)** and **Zero-Crossing Rate (ZCR) variance** to physically inspect vocoder hiss and vocal cord micro-tremors, rather than treating the neural network as an unquestioned black box.

