# QAce _InnoScream_

**Anonymous stress‑relief bot + REST API**  
Semester project for the _SQRS – Software Quality, Reliability & Security_ course  
Team **QAce** • Innopolis University

---

## 🚀 Quick start (dev)

```bash
# 1. clone
git clone https://github.com/raydenoir/QAce_InnoScream.git
cd QAce_InnoScream

# 2. make sure you’re on Python 3.11
python --version        # → 3.11.x

# 3. install Poetry (if you don’t have it)
pip install --upgrade poetry   # or follow https://python-poetry.org/docs/#installation

# 4. install deps (runtime + QA tools)
poetry install --with dev

# 5. create .env with your secrets
cp .env.example .env        # then edit!

# 6. run in hot‑reload mode
poetry run uvicorn innoscream.main:app --reload
```

FastAPI at http://localhost:8000
OpenAPI docs at http://localhost:8000/docs
The aiogram bot starts polling in the same process.

## 🔑 Environment variables (.env)
| Key            | Example               | Purpose                       |
| -------------- | --------------------- | ----------------------------- |
| `BOT_TOKEN`    | `123456:ABC‑DEF`      | Telegram bot token            |
| `CHANNEL_ID`   | `-1002322575648`      | Read‑only channel for screams |
| `ADMINS`       | `123456789,987654321` | Comma‑separated admin IDs     |
| `HASH_SALT`    | `change‑me‑pls`       | Salt for hashing user IDs     |
| `IMGFLIP_USER` | `username`            | Imgflip username              |
| `IMGFLIP_PASS` | `password`            | Imgflip password              |
