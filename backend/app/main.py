"""FastAPI application entry point with middleware and router registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, chat, symptom_checker, appointments
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    await init_db()

    # Initialize AI service (lazy — will retry on first request if key missing)
    from app.services.gemini_service import gemini_service
    try:
        gemini_service.initialize()
    except ValueError as e:
        import logging
        logging.warning(f"AI service not ready: {e}. Set NVIDIA_API_KEY in .env and restart.")
    app.state.gemini_service = gemini_service

    yield

    # Shutdown
    pass


app = FastAPI(
    title="Healthcare Chatbot API",
    description="AI-Powered Advanced Healthcare Chatbot System",
    version="2.0.0",
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

# --- Routers ---
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(symptom_checker.router, prefix="/api/symptoms", tags=["Symptom Checker"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
