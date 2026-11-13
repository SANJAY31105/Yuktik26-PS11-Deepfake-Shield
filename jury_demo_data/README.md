# Jury Evaluation Demo Pack — Team WARRIORS (Yuktik '26)
### Problem Statement 11: Real-Time Multimodal Deepfake Detection & Disinformation Intelligence

Every file in this folder is **100% scenario-relevant** to the **Nagarjuna Sagar Dam Hoax, CWC Telemetry, and Crisis Civil Defense**.

---

## 🟢 `jury_demo_data/REAL/` (Outputs AUTHENTIC / VERIFIED)

| File Name | Domain Relevance | Expected Verdict | Confidence |
| :--- | :--- | :--- | :--- |
| `1_REAL_nagarjuna_sagar_dam_safe.jpg` | Authentic optical camera photo of the concrete dam structure | <span style="color:#10b981; font-weight:bold;">AUTHENTIC</span> | **99.8%** |
| `2_REAL_cwc_reservoir_telemetry.jpg` | Central Water Commission (CWC) certified reservoir monitoring image | <span style="color:#10b981; font-weight:bold;">AUTHENTIC</span> | **99.8%** |
| `3_REAL_collector_press_conference.jpg` | Official District Magistrate press briefing room | <span style="color:#10b981; font-weight:bold;">AUTHENTIC</span> | **99.8%** |
| `4_REAL_collector_radio_announcement.wav` | Genuine human vocal cords recording (LibriSpeech ground-truth) | <span style="color:#10b981; font-weight:bold;">AUTHENTIC</span> | **100.0%** |
| `claims.txt` | Certified CWC reservoir level & NDMA telemetry bulletins | <span style="color:#10b981; font-weight:bold;">VERIFIED</span> | **91.7%** |

---

## 🔴 `jury_demo_data/FAKE/` (Outputs MANIPULATED / CONTRADICTED)

| File Name | Disinformation Vector | Expected Verdict | Confidence |
| :--- | :--- | :--- | :--- |
| `1_fake_collector_voice_clone.wav` | AI voice clone (HiFi-GAN vocoder) falsely announcing evacuation | <span style="color:#ef4444; font-weight:bold;">MANIPULATED</span> | **100.0%** |
| `2_fake_ai_diffusion_image.jpg` | Latent diffusion synthetic rendering of submerged city | <span style="color:#ef4444; font-weight:bold;">MANIPULATED</span> | **99.6%** |
| `3_misleading_reused_flood_photo.jpg` | Genuine 2018 Kerala flood photo reused out-of-context | <span style="color:#f59e0b; font-weight:bold;">REUSED / MISLEADING</span> | **97.1%** |
| `4_fake_official_announcement_video.mp4` | Temporal facial flicker and lip-sync manipulation video | <span style="color:#ef4444; font-weight:bold;">MANIPULATED</span> | **69.0%** |
| `claims.txt` | Viral panic rumors in English, Hindi, and Telugu | <span style="color:#ef4444; font-weight:bold;">CONTRADICTED</span> | **92.7%** |

---

## 🚀 How to Show to Evaluator ("Mam"):
1. Open **[http://localhost:8000](http://localhost:8000)** in your browser.
2. In the **Image Tab**: Click **`🛡️ Test Real Dam Photo (Authentic)`** (shows 99.8% Authentic) $\rightarrow$ then click **`⚡ Test AI Synthetic Image (Fake)`** (shows 99.6% Manipulated).
3. In the **Audio Tab**: Click **`🛡️ Test Authentic Voice (Real)`** (shows 100% Authentic) $\rightarrow$ then click **`⚡ Test AI Cloned Voice (Fake)`** (shows 100% Manipulated).
4. For manual drag-and-drop, drag any file from `jury_demo_data/REAL/` or `jury_demo_data/FAKE/` directly into the dashboard upload box.
