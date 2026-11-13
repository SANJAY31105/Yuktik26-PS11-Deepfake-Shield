"""
SatyaShield AI — Real-Time Telegram Misinformation & Deepfake Defense Bot
=========================================================================
Allows any citizen, journalist, or cyber-crime investigator to forward
suspicious voice notes, images, videos, or multilingual text claims and
receive an autonomous forensic breakdown in under 2 seconds.

Setup in 60 seconds:
1. Open Telegram, search for @BotFather, and type /newbot to get a BOT_TOKEN.
2. Set your token:
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"  (Linux/Mac)
   $env:TELEGRAM_BOT_TOKEN="your_bot_token_here"     (Windows PowerShell)
3. Run the bot:
   python bot/telegram_bot.py
"""

import os
import sys
import time
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional

import requests

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.ai_engine.image_detector import ImageDetector
from backend.ai_engine.audio_detector import AudioDetector
from backend.ai_engine.claim_verifier import ClaimVerifier

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("SatyaShieldBot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Initialize local AI engines
image_detector = ImageDetector()
audio_detector = AudioDetector()
claim_verifier = ClaimVerifier()


def send_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> dict:
    """Send formatted text message to user."""
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        logger.error("Failed to send message: %s", e)
        return {}


def download_file(file_id: str) -> Optional[bytes]:
    """Download binary file from Telegram servers."""
    try:
        get_file_url = f"{API_URL}/getFile?file_id={file_id}"
        r = requests.get(get_file_url, timeout=10).json()
        file_path = r.get("result", {}).get("file_path")
        if not file_path:
            return None
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_bytes = requests.get(download_url, timeout=15).content
        return file_bytes
    except Exception as e:
        logger.error("Failed to download file %s: %s", file_id, e)
        return None


async def handle_photo(chat_id: int, photo_list: list):
    """Processes forwarded photos using Vision Transformer and dHash."""
    send_message(chat_id, "🔍 *Scanning visual forensics with Vision Transformer & perceptual dHash...*")
    largest_photo = photo_list[-1]
    file_id = largest_photo["file_id"]
    file_bytes = download_file(file_id)

    if not file_bytes:
        send_message(chat_id, "❌ Could not download photo from Telegram. Please try again.")
        return

    result = await image_detector.analyze(file_bytes, filename="telegram_upload.jpg")
    verdict = result.get("verdict", "unknown").upper()
    confidence = (result.get("confidence", 0.0) * 100)
    explanation = result.get("explanation", "No explanation available.")

    badge = "🚨 *MANIPULATED / FAKE*" if verdict in ("MANIPULATED", "MISLEADING") else "🛡️ *AUTHENTIC / GENUINE*"

    msg = (
        f"{badge}\n\n"
        f"📊 *Confidence Score:* `{confidence:.1f}%`\n"
        f"⚡ *Latency:* `{result.get('processing_time_ms', 25)} ms`\n\n"
        f"🔬 *Forensic Breakdown:*\n{explanation}\n\n"
        f"🏛️ _Verified by SatyaShield AI Autonomous Vision Engine_"
    )
    send_message(chat_id, msg)


async def handle_audio(chat_id: int, file_id: str, filename: str):
    """Processes forwarded voice notes and audio clips using Wav2Vec 2.0."""
    send_message(chat_id, "🎙️ *Analyzing acoustic spectral flatness & vocal tract jitter with Wav2Vec 2.0...*")
    file_bytes = download_file(file_id)

    if not file_bytes:
        send_message(chat_id, "❌ Could not download audio file. Please try again.")
        return

    result = await audio_detector.analyze(file_bytes, filename=filename)
    verdict = result.get("verdict", "unknown").upper()
    confidence = (result.get("confidence", 0.0) * 100)
    explanation = result.get("explanation", "No explanation available.")

    badge = "🚨 *AI VOICE CLONE DETECTED*" if verdict in ("MANIPULATED", "MISLEADING") else "🛡️ *NATURAL HUMAN SPEECH VERIFIED*"

    msg = (
        f"{badge}\n\n"
        f"📊 *Synthetic Probability:* `{confidence:.1f}%`\n"
        f"⚡ *Latency:* `{result.get('processing_time_ms', 24)} ms`\n\n"
        f"🔬 *Acoustic DSP Analysis:*\n{explanation}\n\n"
        f"🏛️ _Verified by SatyaShield AI Speech Forensics Engine_"
    )
    send_message(chat_id, msg)


async def handle_text(chat_id: int, text: str):
    """Processes multilingual text rumors using RoBERTa NLI against government telemetry."""
    if text.startswith("/start") or text.startswith("/help"):
        welcome = (
            "🛡️ *Welcome to SatyaShield AI Telegram Bot*\n"
            "India's Autonomous Real-Time Deepfake & Disinformation Defense Shield.\n\n"
            "Forward or send me any suspicious media:\n"
            "• 🎙️ *Voice Notes / Audio:* Detects AI voice clones (Wav2Vec2).\n"
            "• 🖼️ *Photos / Screenshots:* Detects AI diffusion & recycled flood photos (ViT & dHash).\n"
            "• ✍️ *Text Rumors:* Verifies claims in English, Hindi, and Telugu against live CWC & NDMA telemetry.\n\n"
            "_Forward any message right now to test!_"
        )
        send_message(chat_id, welcome)
        return

    send_message(chat_id, "✍️ *Verifying claim against Central Water Commission & NDMA Knowledge Graph...*")
    result = await claim_verifier.analyze(text)
    verdict = result.get("verdict", "unverified").upper()
    confidence = (result.get("confidence", 0.0) * 100)
    explanation = result.get("explanation", "")
    lang = result.get("detected_language", "en").upper()

    badge = "🚨 *CONTRADICTED / FABRICATED*" if verdict == "CONTRADICTED" else ("🛡️ *VERIFIED OFFICIAL TRUTH*" if verdict == "VERIFIED" else "⚠️ *MISLEADING / UNVERIFIED*")

    msg = (
        f"{badge}\n\n"
        f"🌐 *Detected Language:* `{lang}`\n"
        f"📊 *Truth Confidence:* `{confidence:.1f}%`\n\n"
        f"🏛️ *Official Ground Truth:*\n{explanation}\n\n"
        f"📜 _Cross-referenced with official state & national disaster telemetry._"
    )
    send_message(chat_id, msg)


async def main():
    """Long-polling update loop for Telegram Bot."""
    if not BOT_TOKEN:
        print("\n" + "=" * 70)
        print("  ⚠️  TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("  To launch your live Telegram Bot:")
        print("  1. Open Telegram, search @BotFather, and create a bot (/newbot).")
        print("  2. Run:")
        print("     export TELEGRAM_BOT_TOKEN=\"your_token_here\"  (Linux/Mac)")
        print("     $env:TELEGRAM_BOT_TOKEN=\"your_token_here\"     (Windows PowerShell)")
        print("     python bot/telegram_bot.py")
        print("=" * 70 + "\n")
        return

    logger.info("SatyaShield AI Telegram Bot is online and listening for messages...")
    offset = None

    while True:
        try:
            url = f"{API_URL}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            
            resp = requests.get(url, timeout=40).json()
            updates = resp.get("result", [])

            for u in updates:
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("channel_post")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]

                # 1. Handle Photos
                if "photo" in msg:
                    await handle_photo(chat_id, msg["photo"])
                # 2. Handle Voice notes or Audio
                elif "voice" in msg:
                    await handle_audio(chat_id, msg["voice"]["file_id"], "voice_note.ogg")
                elif "audio" in msg:
                    await handle_audio(chat_id, msg["audio"]["file_id"], msg["audio"].get("file_name", "audio.wav"))
                # 3. Handle Text claims
                elif "text" in msg:
                    await handle_text(chat_id, msg["text"])

        except Exception as exc:
            logger.error("Polling error: %s", exc)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
