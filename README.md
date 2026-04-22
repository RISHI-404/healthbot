# 🏥 Healthcare Chatbot — Final Year Project

An AI-powered healthcare chatbot built with **FastAPI** (Python) + **React** (TypeScript).  
No Docker required — runs with SQLite out of the box.

---

## ✅ Prerequisites

Install these once on any laptop:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10 or higher | https://python.org/downloads |
| Node.js | 18 or higher | https://nodejs.org |
| Git | any | https://git-scm.com |

> ⚠️ During Python install on Windows, **tick "Add Python to PATH"**.

---

## 🚀 Quick Start (First Time)

### 1. Clone the project
```bash
git clone <your-repo-url>
cd chatbot-2
```

### 2. Run the setup script

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Mac / Linux:**
```bash
chmod +x setup.sh && ./setup.sh
```

This installs all dependencies automatically.

---

## ▶️ Running the App (After Setup)

Open **two terminals** in VS Code (`Ctrl+`` ` `` → split terminal):

### Terminal 1 — Backend
**Windows:**
```powershell
.\.venv\Scripts\activate
cd backend
uvicorn app.main:app --reload --port 8000
```
**Mac/Linux:**
```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser 🎉

---

## 🔑 Environment Variables

The `backend/.env` file is pre-configured with SQLite and a working NVIDIA API key.  
On a **new laptop**, copy it from the example:

```bash
cp backend/.env.example backend/.env   # Mac/Linux
copy backend\.env.example backend\.env  # Windows
```

Then edit `backend/.env` and set your own key if needed:
```
NVIDIA_API_KEY=your-key-here
```

---

## 📁 Project Structure

```
chatbot-2/
├── backend/            # FastAPI Python backend
│   ├── app/
│   │   ├── main.py         # App entry point
│   │   ├── models/         # Database models
│   │   ├── routers/        # API routes (auth, chat, appointments…)
│   │   ├── services/       # AI & business logic
│   │   └── schemas/        # Pydantic schemas
│   ├── data/               # symptom_tree.json etc.
│   ├── requirements.txt
│   └── .env                # ← config lives here
├── frontend/           # React + Vite + TypeScript frontend
│   ├── src/
│   └── package.json
├── setup.ps1           # One-click Windows setup
├── setup.sh            # One-click Mac/Linux setup
└── README.md
```

---

## 🐛 Common Issues

| Problem | Fix |
|---------|-----|
| `python not found` | Re-install Python and tick "Add to PATH" |
| `uvicorn not found` | Make sure you activated the venv first |
| `npm not found` | Install Node.js from nodejs.org |
| Port 8000 already in use | Kill the old process or use `--port 8001` |
| AI not responding | Check `NVIDIA_API_KEY` in `backend/.env` |

---

## 🧪 Running Tests

```bash
# activate venv first, then:
cd backend
pytest
```

---

## 🎓 Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite (aiosqlite), JWT auth
- **AI:** NVIDIA NIM API (meta/llama-3.1-8b-instruct)
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Framer Motion
- **Auth:** JWT tokens + bcrypt password hashing
- **Security:** AES encryption, security headers middleware
