# Twitter (X) → PostgreSQL → Flask Web Dashboard

A Python web application that fetches tweets using the official X (Twitter) API (v2),
stores them in a PostgreSQL database, and provides a searchable web interface built with Flask and TailwindCSS.

---

## 🚀 Overview

**Workflow**
1. **Ingest Tweets** using the X API (`search_recent_tweets`).
2. **Store Data** in normalized PostgreSQL tables (`users`, `tweets`, `hashtags`, `topics`, `tweet_topics`).
3. **Search and Visualize** tweets on a Flask web dashboard with pagination, filters, and dark mode.

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| Language | Python 3.10+ |
| Web Framework | Flask + Jinja2 |
| Database | PostgreSQL 13+ |
| ORM/Driver | psycopg2 (raw SQL) |
| API Client | Tweepy v4 (X API v2) |
| Styling | Tailwind CSS |
| Environment | dotenv-based configuration |

---

## 🔐 Authentication & API Tier

- **Plan:** X (Twitter) Developer **Free Tier**
- **Endpoint:** `GET /2/tweets/search/recent`
- **Auth Method:** Bearer Token (App-Only OAuth2)
- **Permissions:** Read-Only
- **Rate Limit:** ≈ 100 tweets / month on the free plan  
  *(set `wait_on_rate_limit=True` to auto-sleep on 429 responses)*

---

## 📂 Project Structure

twitter_query_app/
├── db/
│   ├── __init__.py
│   └── connect.py
├── ingest/
│   ├── __init__.py
│   └── fetch_and_load.py
├── web/
|    ├── __init__.py
|    ├── app.py
|    └── templates/
|        ├── base.html
|        └── index.html
│
├── utils/
│ └── logging_config.py # Logger setup
│
├── .env.example
├── requirements.txt
└── README.md

## ⚙️ Installation & Setup

### 1️⃣ Clone & Create Virtual Environment
```bash
git clone <repo_url>
cd project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 2️⃣ Configure Environment

Create .env:

X_BEARER_TOKEN=YOUR_TWITTER_BEARER_TOKEN
DATABASE_URL=postgresql://postgres:password@localhost:5432/tweetsdb
FLASK_ENV=development

### 3️⃣ Initialize Database

createdb tweetsdb
psql tweetsdb -f db/create_schema.sql

### 4️⃣ Ingest Tweets

python ingest.fetch_and_load.py --query "generative ai lang:en" --max 20

### 5️⃣ Launch Web App

python web.app.py

### Visit: http://127.0.0.1:5000

## Web Interface Features

Search Filters: Text, Hashtag, Username, Date Range

Pagination: 20 results per page

Flash Notifications: Success / Warning messages

Dark Mode: Toggle persistent via localStorage

Responsive UI: Tailwind-based styling

SQL_Safety Parameterized queries (no string concatenation)