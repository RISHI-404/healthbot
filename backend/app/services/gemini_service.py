"""NVIDIA AI service for healthcare chatbot responses."""

from openai import OpenAI
from typing import List, Dict, Tuple
import asyncio
import re
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# ── Healthcare-only keyword set (for hybrid detection) ─────────────────── #
_HEALTH_KEYWORDS = {
    "symptom", "pain", "ache", "fever", "cough", "cold", "sore", "throat",
    "headache", "migraine", "nausea", "vomit", "diarrhea", "fatigue",
    "dizzy", "dizziness", "rash", "itch", "swelling", "bleeding",
    "cramp", "burn", "injury", "fracture", "wound", "infection",
    "head", "chest", "stomach", "heart", "lung", "liver", "kidney",
    "skin", "eye", "ear", "nose", "back", "knee", "joint", "muscle",
    "bone", "blood", "brain", "abdomen",
    "diabetes", "asthma", "allergy", "cancer", "hypertension", "arthritis",
    "anxiety", "depression", "insomnia", "obesity", "anemia", "thyroid",
    "cholesterol", "stroke", "pneumonia", "bronchitis", "flu", "influenza",
    "covid", "tuberculosis", "malaria", "dengue", "hiv", "aids",
    "health", "healthy", "wellness", "nutrition", "diet", "exercise",
    "fitness", "sleep", "stress", "meditation", "yoga", "weight",
    "calorie", "vitamin", "protein", "hydration", "bmi",
    "doctor", "hospital", "medicine", "medication", "drug", "tablet",
    "prescription", "vaccine", "surgery", "therapy", "treatment",
    "diagnosis", "medical", "clinic", "nurse", "pharmacy", "dosage",
    "antibiotic", "painkiller", "supplement", "checkup", "test",
    "x-ray", "xray", "scan", "mri", "ultrasound", "bp", "ecg",
    "mental", "counseling", "therapist", "psychiatrist", "panic",
    "trauma", "ptsd", "ocd", "adhd", "bipolar", "schizophrenia",
    "first aid", "cpr", "choking", "poison", "overdose",
    "sprain", "bandage", "emergency",
    "sick", "ill", "disease", "condition", "disorder", "syndrome",
    "pregnant", "pregnancy", "period", "menstrual", "fertility",
    "baby", "infant", "child health", "pediatric",
}

# Intents from the NLP classifier that are health-related
_HEALTH_INTENTS = {
    "symptom_query", "greeting", "goodbye", "thanks",
    "medication_query", "diet_query", "exercise_query",
    "mental_health", "first_aid", "emergency",
    "appointment", "wellness", "prevention",
}

NON_HEALTH_RESPONSE = (
    "I'm here to help only with health-related questions. "
    "Please ask about symptoms, health, or wellness."
)

SAFETY_DISCLAIMER = (
    "\n\n⚕️ *This is general health information only — not a diagnosis or prescription. "
    "Always consult a qualified healthcare professional for personalised advice.*"
)


def validate_health_query(
    text: str,
    nlp_intent: str = "",
    nlp_confidence: float = 0.0,
) -> Tuple[bool, str]:
    """
    Hybrid health-topic gate combining keyword matching + NLP intent.

    Returns:
        (is_health_related: bool, reason: str)
    """
    lower = text.lower()

    # 1. NLP intent check (if available and confident)
    if nlp_intent and nlp_confidence >= 0.45:
        if nlp_intent in _HEALTH_INTENTS:
            return True, f"nlp_intent={nlp_intent}"

    # 2. Keyword scan
    for kw in _HEALTH_KEYWORDS:
        if kw in lower:
            return True, f"keyword={kw}"

    # 3. Short greetings are okay (hi, hello, hey)
    if lower.strip() in {"hi", "hello", "hey", "good morning", "good evening"}:
        return True, "greeting"

    return False, "no_health_signal"


SYSTEM_PROMPT = """You are a healthcare assistant.

STRICT RULES:
1. ONLY answer health-related questions.
2. If the user asks about ANYTHING unrelated to health — coding, jokes, maths, recipes, politics, sports, entertainment, history, travel, finance, tech, creative writing, or ANY other non-medical topic — respond ONLY with:
   "I'm here to help only with health-related questions. Please ask about symptoms, health, or wellness."
3. Do NOT answer non-medical questions under any circumstances, even if the user insists.
4. Do NOT write long paragraphs. NEVER exceed 3 short sentences per bullet.
5. Do NOT diagnose conditions — say "this could indicate" instead of "you have".
6. Do NOT prescribe specific medicines or dosages.
7. Always include a gentle reminder to consult a doctor for serious concerns.

ALWAYS structure your health responses EXACTLY like this:

💡 What might be happening:
• (one short sentence about a possible cause)
• (one short sentence about another cause)

🩺 What you can do:
• (one actionable self-care tip)
• (one actionable self-care tip)

⚠️ When to see a doctor:
• (one warning sign that needs professional attention)

Keep each bullet point to ONE short sentence. Maximum 2-3 bullets per section.
Be warm, empathetic, and reassuring.
"""


def _truncate_bullet(line: str, max_len: int = 120) -> str:
    """Shorten a bullet point to its first sentence if too long."""
    stripped = line.strip()
    if not stripped.startswith(("•", "-", "*", "·")) or len(stripped) <= max_len:
        return line
    first_sentence = re.split(r'[.!?]', stripped[2:].strip())[0].strip()
    return f"• {first_sentence}"


def format_health_response(text: str) -> str:
    """
    Post-process AI response to enforce structured bullet-point format.
    Ensures output always follows the 💡/🩺/⚠️ layout with short bullets,
    and appends a safety disclaimer.
    """
    # If it's the non-health refusal, return as-is (no formatting needed)
    if text.strip() == NON_HEALTH_RESPONSE.strip():
        return text

    # Check if the response already has the structured format
    has_structure = (
        "💡" in text or "🩺" in text or "⚠️" in text
        or "What might be happening" in text
        or "What you can do" in text
        or "When to see a doctor" in text
    )

    if has_structure:
        # Clean up: ensure bullets are short
        lines = text.split("\n")
        cleaned = [_truncate_bullet(line) for line in lines]
        result = "\n".join(cleaned)
    else:
        # ── Response lacks structure — reformat it ─────────────────────── #
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return text + SAFETY_DISCLAIMER

        # Categorize sentences into sections
        causes, actions, warnings = [], [], []

        doctor_kw = {"doctor", "hospital", "emergency", "seek medical", "professional",
                     "urgent", "immediately", "worsen", "persist", "severe"}
        action_kw = {"try", "take", "drink", "rest", "apply", "avoid", "eat",
                     "exercise", "sleep", "use", "can", "should", "help",
                     "recommend", "consider", "ensure", "make sure", "keep"}

        for sentence in sentences:
            lower = sentence.lower()
            if any(kw in lower for kw in doctor_kw):
                warnings.append(sentence)
            elif any(kw in lower for kw in action_kw):
                actions.append(sentence)
            else:
                causes.append(sentence)

        # Ensure each section has at least one item
        if not causes and actions:
            causes.append(actions.pop(0))
        if not actions and causes:
            actions.append(causes.pop())
        if not warnings:
            warnings.append("If symptoms persist or worsen, consult a doctor")

        # Limit to 3 bullets per section for readability
        causes = causes[:3]
        actions = actions[:3]
        warnings = warnings[:2]

        # Build formatted output
        parts = []
        parts.append("💡 What might be happening:")
        for item in causes:
            parts.append(f"• {item.rstrip('.')}")

        parts.append("")
        parts.append("🩺 What you can do:")
        for item in actions:
            parts.append(f"• {item.rstrip('.')}")

        parts.append("")
        parts.append("⚠️ When to see a doctor:")
        for item in warnings:
            parts.append(f"• {item.rstrip('.')}")

        result = "\n".join(parts)

    # Append safety disclaimer if not already present
    if "general health information" not in result.lower() and "not a diagnosis" not in result.lower():
        result += SAFETY_DISCLAIMER

    return result


def parse_response_to_json(text: str) -> Dict:
    """
    Parse a formatted health response into structured JSON.

    Returns:
        {
            "summary": "...",    # from 💡 What might be happening
            "tips": ["..."],     # from 🩺 What you can do
            "warning": "..."     # from ⚠️ When to see a doctor
        }
    """
    # Handle the non-health refusal specially
    if NON_HEALTH_RESPONSE.strip() in text.strip():
        return {
            "summary": NON_HEALTH_RESPONSE,
            "tips": [],
            "warning": "",
        }

    summary_items = []
    tips_items = []
    warning_items = []

    current_section = None
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if "💡" in stripped or "What might be happening" in stripped:
            current_section = "summary"
            continue
        elif "🩺" in stripped or "What you can do" in stripped:
            current_section = "tips"
            continue
        elif "⚠️" in stripped or "When to see a doctor" in stripped:
            current_section = "warning"
            continue

        # Skip empty lines and disclaimer lines
        if not stripped or "general health information" in stripped.lower():
            continue
        if stripped.startswith("⚕️"):
            continue

        # Extract bullet content (remove bullet markers)
        content = re.sub(r'^[•\-\*·]\s*', '', stripped).strip()
        if not content:
            continue

        if current_section == "summary":
            summary_items.append(content)
        elif current_section == "tips":
            tips_items.append(content)
        elif current_section == "warning":
            warning_items.append(content)
        else:
            # Text before any section header → treat as summary
            summary_items.append(content)

    return {
        "summary": "; ".join(summary_items) if summary_items else text.strip(),
        "tips": tips_items if tips_items else ["Consult a healthcare professional for personalized advice"],
        "warning": "; ".join(warning_items) if warning_items else "If symptoms persist or worsen, see a doctor",
    }


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
