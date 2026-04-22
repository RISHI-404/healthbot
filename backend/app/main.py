"""FastAPI application entry point with middleware and router registration."""

import sys
import logging

# Fix Windows console encoding for emoji characters (💡🩺⚠️)
# Without this, SQLAlchemy echo logging crashes on cp1252 terminals.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    # Reconfigure all existing stream handlers to use UTF-8
    for handler in logging.root.handlers:
        if isinstance(handler, logging.StreamHandler) and hasattr(handler.stream, "reconfigure"):
            handler.stream.reconfigure(encoding="utf-8", errors="replace")

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

    # Initialize Local AI service (lazy model load on first request)
    from app.services.local_ai_service import local_ai_service
    if settings.LOCAL_AI_ENABLED:
        import logging as _log
        _log.getLogger(__name__).info(
            f"Local AI enabled: {settings.LOCAL_AI_MODEL} "
            f"(adapter: '{settings.LOCAL_AI_ADAPTER_PATH or 'none'}')"
        )
        local_ai_service.configure(
            model_id=settings.LOCAL_AI_MODEL,
            adapter_path=settings.LOCAL_AI_ADAPTER_PATH,
            max_tokens=settings.LOCAL_AI_MAX_TOKENS,
            use_quantize=settings.LOCAL_AI_QUANTIZE,
        )
    app.state.local_ai_service = local_ai_service

    # Pre-warm NLP pipeline so the first chat request doesn't trigger
    # a 30-60 second cold-start (spaCy + scikit-learn model loading).
    import logging as _nlp_log
    _nlp_log.getLogger(__name__).info("Pre-warming NLP pipeline...")
    try:
        from app.routers.chat import _get_nlp_pipeline
        await _get_nlp_pipeline()
        _nlp_log.getLogger(__name__).info("NLP pipeline ready.")
    except Exception as _nlp_exc:
        _nlp_log.getLogger(__name__).warning(f"NLP pre-warm failed (non-fatal): {_nlp_exc}")

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
