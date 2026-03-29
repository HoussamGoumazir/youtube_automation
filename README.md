# 🎯 Object Life — Social Media Automation System

![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Version](https://img.shields.io/badge/version-3.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A professional, fully automated pipeline that picks a video from a local folder, uses **Google Gemini AI** to generate viral, platform-specific metadata, then uploads it to **YouTube Shorts**, **Instagram Reels**, **TikTok**, and **Facebook Reels** — all with a single command.

Built for the **Object Life** channel: everyday objects coming to life in funny, relatable animated shorts.

---

## 🏗️ Project Structure

```
youtube_automation/
├── ai/                     # AI & Content Generation
│   ├── generator.py        # Gemini API client (with exponential back-off)
│   └── prompts.py          # All prompt templates (separated from config)
│
├── uploaders/              # Platform-specific upload clients
│   ├── youtube.py          # YouTube Data API v3 (resumable upload)
│   ├── facebook.py         # Facebook Graph API Reels
│   ├── instagram.py        # Instagram (via instagrapi)
│   └── tiktok.py           # TikTok (via Selenium browser automation)
│
├── automation/             # Orchestration & File Management
│   ├── workflow.py         # Main pipeline: file → AI → upload → archive
│   └── files.py            # Video folder management & archiving
│
├── config/
│   └── settings.py         # All settings loaded from .env variables
│
├── utils/
│   ├── logger.py           # Structured logging
│   └── error_handler.py    # @retry, @safe_upload, @log_pipeline_step decorators
│
├── videos/                 # Drop your MP4 files here (not committed)
│   ├── morning/
│   ├── noon/
│   └── evening/
│
├── .env.example            # Template — copy to .env and fill in your keys
├── .gitignore
├── requirements.txt
└── main.py                 # Entry point
```

---

## 🔄 Pipeline Flow

```
videos/morning/*.mp4
        │
        ▼
automation/workflow.py  →  picks oldest video
        │
        ▼
ai/generator.py         →  calls Gemini AI → returns JSON metadata for all platforms
        │
        ▼
uploaders/youtube.py    →  uploads to YouTube Shorts (resumable, with retry)
        │
        ▼
uploaders/instagram.py  →  uploads to Instagram Reels  (if enabled)
uploaders/tiktok.py     →  uploads to TikTok            (if enabled)
uploaders/facebook.py   →  uploads to Facebook Reels    (if enabled)
        │
        ▼
automation/files.py     →  moves video to archive/ with metadata file
```

---

## ⚙️ Setup

### 1. Clone & install
```bash
git clone https://github.com/HoussamGoumazir/youtube_automation.git
cd youtube_automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Open .env and fill in your API keys
```

Key variables in `.env`:
| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com/) |
| `FACEBOOK_ENABLED` | `true` / `false` |
| `FACEBOOK_PAGE_ID` | Your Facebook Page ID |
| `FACEBOOK_ACCESS_TOKEN` | Page Access Token |
| `INSTAGRAM_ENABLED` | `true` / `false` |
| `INSTAGRAM_USERNAME` | Your Instagram username |
| `INSTAGRAM_PASSWORD` | Your Instagram password |
| `TIKTOK_ENABLED` | `true` / `false` |
| `TIKTOK_SESSION_ID` | Your TikTok `sessionid` cookie value |

### 3. YouTube OAuth credentials
- Download your **OAuth 2.0 Client credentials** JSON from [Google Cloud Console](https://console.cloud.google.com/).
- Save it as `youtube_credentials.json` in the project root.
- The first run will open a browser to authorize access. The token is then cached in `config/youtube_token.pickle`.

### 4. Add videos
Place `.mp4` files in:
- `videos/morning/` — for the morning upload
- `videos/noon/` — for the noon upload
- `videos/evening/` — for the evening upload

### 5. Run
```bash
python main.py morning     # or noon / evening

python main.py check       # check video availability
python main.py health      # system health check
python main.py stats       # upload statistics
python main.py setup       # create folder structure
```

---

## 🛡️ Error Handling

`utils/error_handler.py` provides three reusable decorators:

| Decorator | Purpose |
|---|---|
| `@retry(max_attempts, delay, backoff)` | Auto-retry with exponential back-off |
| `@safe_upload("platform")` | Catch all exceptions, log, return `None` |
| `@log_pipeline_step("Step Name")` | Log entry/exit of any pipeline stage |

---

## 📄 License

MIT — see [LICENSE](LICENSE).
