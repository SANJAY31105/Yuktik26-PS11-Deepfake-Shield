# SatyaShield AI — Real-World Cloud Deployment Guide 🚀

This document outlines how to deploy SatyaShield AI to production cloud infrastructure and connect it to real users.

---

## 1. Free Cloud GPU Deployment (Hugging Face Spaces)

Hugging Face Spaces offers **free community Docker and GPU hosting** with direct public HTTPS URLs.

### Steps:
1. Go to **[huggingface.co/new-space](https://huggingface.co/new-space)**.
2. Set Space Name: `satyashield-ai`.
3. Select **Space SDK**: **Docker** (Blank template).
4. Clone the space repository locally or push your existing Git repo to it:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/satyashield-ai
   git push hf main
   ```
5. Hugging Face will automatically build the `Dockerfile`, spin up the server, and give you a permanent live public URL (e.g. `https://your-username-satyashield-ai.hf.space`) with full GPU support!

---

## 2. Docker Deployment (DigitalOcean / AWS / GCP / RunPod)

On any Ubuntu or Debian Linux VPS with or without GPU:

```bash
# 1. Clone repository
git clone https://github.com/SANJAY31105/Yuktik26-PS11-Deepfake-Shield.git
cd Yuktik26-PS11-Deepfake-Shield

# 2. Run with Docker Compose
docker-compose up -d --build

# 3. View live logs
docker-compose logs -f
```

Your system is now live on `http://YOUR_SERVER_IP:8000`.

---

## 3. Launching the Telegram Viral Bot (Zero Server Cost)

1. Open Telegram on your phone and search for **`@BotFather`**.
2. Send `/newbot`, name it (e.g. `SatyaShield_Bot`), and copy the HTTP API Token.
3. Start the bot:
   ```bash
   # Linux / Mac:
   export TELEGRAM_BOT_TOKEN="your_token_here"
   python bot/telegram_bot.py

   # Windows PowerShell:
   $env:TELEGRAM_BOT_TOKEN="your_token_here"
   python bot/telegram_bot.py
   ```
4. Now, share your `@SatyaShield_Bot` username with anyone! Users can forward any voice note, image, or text rumor and receive real-time forensic verifications directly on their phones.

---

## 4. Setting up a Custom Domain & SSL (Nginx Reverse Proxy)

```nginx
server {
    listen 80;
    server_name satyashield.ai api.satyashield.ai;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
Run `sudo certbot --nginx -d satyashield.ai` to issue free Let's Encrypt SSL certificates.
