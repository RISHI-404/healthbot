"""NVIDIA AI service for healthcare chatbot responses."""

from openai import OpenAI
from typing import List, Dict
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are HealthBot, a compassionate and knowledgeable AI healthcare assistant. 
Your goal is to provide helpful information without causing stress or anxiety.

**Guidelines for "Stress-Free" Responses:**
1.  **Be Calm & Reassuring**: Start with a warm, empathetic tone. Validating the user's feelings reduces anxiety.
2.  **Bite-Sized Information**: Avoid long walls of text. Break complex information into short, digestive paragraphs.
3.  **Structure is Key**:
    -   Use **bold** for key takeaways.
    -   Use *bullet points* for lists (symptoms, tips, steps).
    -   Use clear headings.
4.  **Positive Framing**: Focus on actionable steps and solutions rather than just problems.
5.  **Medical Disclaimer**: Gently remind users you are an AI and to consult a doctor for serious issues, but do so naturally, not as a scary legal block.

** formatting**:
-   Keep sentences concise.
-   Use emojis sparingly to add warmth (e.g., 🌿, 💙, ✨).
-   Never use alarmist language.

**Scope**: General health, wellness, symptoms, nutrition, mental health. NO diagnosis, NO prescriptions.
"""


class AIService:
    """Wrapper around NVIDIA API for healthcare chat."""

    def __init__(self):
        self._client = None

    def initialize(self):
        """Initialize the NVIDIA OpenAI-compatible client."""
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in environment variables")
        self._client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY,
        )
        logger.info("NVIDIA AI service initialized successfully")

    async def generate_response(
        self, message: str, context: List[Dict[str, str]] = None
    ) -> str:
        """Generate a response using NVIDIA API with conversation context."""
        if not self._client:
            self.initialize()

        # Build messages list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            for msg in context[:-1]:  # Exclude current (already added below)
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})

        messages.append({"role": "user", "content": message})

        # Run in thread to not block event loop
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self._client.chat.completions.create,
                    model="meta/llama-3.1-70b-instruct",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "rate" in error_str.lower()) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"NVIDIA rate limited (attempt {attempt+1}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"NVIDIA API error: {type(e).__name__}: {e}")
                    raise


# Singleton
gemini_service = AIService()
