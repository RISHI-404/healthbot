#!/bin/bash
# Healthcare Chatbot - Mac/Linux Setup Script
echo "=== Healthcare Chatbot Setup ==="

# --- Backend ---
echo ""
echo "[1/4] Creating Python virtual environment..."
python3 -m venv .venv || { echo "ERROR: Python 3 not found. Install from https://python.org"; exit 1; }

echo "[2/4] Installing Python dependencies..."
.venv/bin/pip install -r backend/requirements.txt

# Copy .env if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "[INFO] Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "[INFO] Edit backend/.env to add your NVIDIA_API_KEY if needed."
fi

# --- Frontend ---
echo "[3/4] Installing frontend Node.js dependencies..."
cd frontend && npm install && cd ..

echo ""
echo "[4/4] Setup complete! ✅"
echo "-----------------------------------------------"
echo "To run the app, open TWO terminals in VS Code:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    source .venv/bin/activate"
echo "    cd backend"
echo "    uvicorn app.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo "-----------------------------------------------"
