"""NLP Pipeline — orchestrates preprocessing, NER, intent classification."""

import asyncio
import json
from typing import Dict, Any, List

from app.services.emergency_detector import detect_emergency, EMERGENCY_RESPONSE
from app.services.entity_extractor import extract_entities, _get_nlp
from app.services.intent_classifier import classify_intent, get_response_for_intent, load_model


class NLPPipeline:
    """Full NLP pipeline: preprocessing → emergency check → NER → intent → response."""

    def __init__(self):
        self._initialized = False

    async def initialize(self):
        """Load models and resources (runs CPU-bound work in thread pool)."""
        if self._initialized:
            return
        # Run synchronous model loading in thread pool to avoid blocking event loop
        await asyncio.to_thread(load_model)
        await asyncio.to_thread(_get_nlp)  # Pre-load spaCy model
        self._initialized = True

    async def process(self, text: str, context: List[Dict] = None) -> Dict[str, Any]:
        """
        Process user input through the full NLP pipeline.

        Returns dict with: response, intent, confidence, entities, is_emergency
        """
        # Step 1: Emergency detection (BEFORE anything else)
        is_emergency, matched_keyword = detect_emergency(text)
        if is_emergency:
            return {
                "response": EMERGENCY_RESPONSE,
                "intent": "emergency",
                "confidence": 1.0,
                "entities": [{"text": matched_keyword, "label": "EMERGENCY"}],
                "is_emergency": True,
            }

        # Step 2: Entity extraction
        entities = extract_entities(text)

        # Step 3: Intent classification
        intent, confidence = classify_intent(text)

        # Step 4: Generate response
        response = get_response_for_intent(intent)

        # Step 5: Enhance response with context and entities
        if entities and intent == "symptom_query":
            symptom_names = [e["text"] for e in entities if e["label"] in ("SYMPTOMS", "CONDITIONS")]
            if symptom_names:
                response += f"\n\n📋 **Detected symptoms/conditions**: {', '.join(symptom_names)}"

        return {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "is_emergency": False,
        }

