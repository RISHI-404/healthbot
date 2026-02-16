"""Emergency keyword detection layer."""

import re
from typing import Tuple, Optional

# Emergency keywords and phrases that trigger immediate escalation
EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "suicide",
    "suicidal",
    "kill myself",
    "want to die",
    "end my life",
    "overdose",
    "drug overdose",
    "severe bleeding",
    "heavy bleeding",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "choking",
    "stroke",
    "seizure",
    "unconscious",
    "passed out",
    "anaphylaxis",
    "allergic reaction severe",
    "poisoning",
    "self harm",
    "self-harm",
]

EMERGENCY_RESPONSE = (
    "🚨 **EMERGENCY DETECTED** 🚨\n\n"
    "Based on what you've described, this may be a medical emergency. "
    "Please take the following steps immediately:\n\n"
    "1. **Call Emergency Services**: Dial 911 (US), 999 (UK), or 112 (EU) immediately.\n"
    "2. **If someone is with you**, ask them to help or call for assistance.\n"
    "3. **Do not delay** — seek professional medical help right away.\n\n"
    "**Crisis Helplines:**\n"
    "- Suicide Prevention: 988 (US) / 116 123 (UK)\n"
    "- Poison Control: 1-800-222-1222 (US)\n\n"
    "⚠️ *This chatbot is not a substitute for professional medical care. "
    "In any life-threatening situation, please contact emergency services immediately.*"
)


def detect_emergency(text: str) -> Tuple[bool, Optional[str]]:
    """
    Scan input text for emergency keywords.

    Returns:
        (is_emergency, matched_keyword)
    """
    text_lower = text.lower().strip()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True, keyword
    return False, None
