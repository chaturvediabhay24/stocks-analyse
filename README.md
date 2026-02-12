# Stock Analyzer

Technical & fundamental analysis for NSE-listed Indian stocks.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Web UI

```bash
source venv/bin/activate
python -m uvicorn web.app:app --reload
```

Open http://127.0.0.1:8000

## Run Telegram Bot

```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
source venv/bin/activate
python bot.py
```
