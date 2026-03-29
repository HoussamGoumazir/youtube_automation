# 🎯 - Social Media Automation System

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A professional, fully automated system for managing and uploading short-form video content across multiple social media platforms (YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels). 

This system was specifically designed for the channel concept (where everyday objects come to life and speak like humans in funny or relatable situations), using **Google Gemini AI** to generate viral, platform-specific metadata.

## ✨ Features

- **🚀 Multi-Platform Uploading**: Simultaneously schedule and publish videos to YouTube, Instagram, TikTok, and Facebook.
- **🤖 AI-Powered Metadata**: Uses Gemini 3.1 Pro to automatically generate viral titles, descriptions, captions, and hashtags tailored for each platform.
- **📅 Smart Scheduling**: Built-in support for different daily session types (`morning`, `noon`, `evening`) with specific tones and engagement hooks.
- **📊 Analytics & Health Checks**: Built-in commands to monitor system health, check video availability, and view upload statistics.
- **🔐 Secure Credential Management**: Encrypted token handling and OAuth 2.0 integration for YouTube API.
- **📁 Automated Archiving**: Automatically moves processed videos to an archive directory to keep your workspace clean.

## 🛠️ Prerequisites

- Python 3.8 or higher
- Google Cloud Console Account (for YouTube Data API v3)
- Google AI Studio Account (for Gemini API Key)
- Chrome Browser (for TikTok automation)

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HoussamGoumazir/youtube_automation.git
   cd youtube_automation
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Directory Structure:**
   ```bash
   python main.py setup
   ```

## ⚙️ Configuration

1. **API Keys & Credentials:**
   - Open `config/settings.py` and replace `YOUR_GEMINI_API_KEY` with your actual Gemini API key.
   - Update your social media credentials (Instagram, Facebook, TikTok) in the `SOCIAL_MEDIA` dictionary in `settings.py`.
   - Update `config/credentials.py` and `youtube_credentials.json` with your real YouTube OAuth 2.0 Client credentials.

2. **Video Folders:**
   Place your ready `.mp4` videos in the respective folders under the `videos/` directory:
   - `videos/morning/`
   - `videos/noon/`
   - `videos/evening/`

## 🚀 Usage

The system is controlled via the `main.py` entry point.

### Running an Upload Session

Run the script and specify the session type to process and upload the videos currently in that folder:

```bash
# Process morning videos
python main.py morning

# Process noon videos
python main.py noon

# Process evening videos
python main.py evening
```

### System Monitoring Commands

```bash
# Check the status and availability of videos in the folders
python main.py check

# Perform a comprehensive system run and API health check
python main.py health

# View historical statistics of successful and failed uploads
python main.py stats
```

## 📝 Logging

All activities, successful uploads, and errors are logged in the `logs/` directory. 
- `youtube_automation.log`: Contains detailed execution logs.
- `successful_uploads.log`: Contains a history of published videos and their generated AI metadata.

## ⚠️ Disclaimer

Automated uploading to social media platforms must comply with their respective Terms of Service. This tool is intended for personal automation and should be used responsibly to avoid account rate-limiting or bans.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
