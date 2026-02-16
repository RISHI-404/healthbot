"""spaCy-based Named Entity Recognition for medical entities."""

from typing import List, Dict

# Lazy-load spaCy to avoid import-time overhead
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import spacy
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


# Custom medical entity patterns
MEDICAL_KEYWORDS = {
    "symptoms": [
        "headache", "fever", "cough", "fatigue", "nausea", "vomiting",
        "dizziness", "chest pain", "shortness of breath", "sore throat",
        "runny nose", "body aches", "chills", "diarrhea", "constipation",
        "rash", "swelling", "numbness", "tingling", "blurred vision",
        "back pain", "joint pain", "muscle pain", "stomach ache",
        "insomnia", "anxiety", "depression", "weight loss", "weight gain",
        "palpitations", "sweating", "itching", "bruising", "bleeding",
    ],
    "body_parts": [
        "head", "chest", "stomach", "back", "neck", "shoulder",
        "arm", "leg", "knee", "ankle", "wrist", "hand", "foot",
        "throat", "eye", "ear", "nose", "heart", "lung", "liver",
        "kidney", "skin", "spine", "hip", "elbow",
    ],
    "conditions": [
        "diabetes", "hypertension", "asthma", "cold", "flu",
        "allergy", "infection", "migraine", "arthritis", "bronchitis",
        "pneumonia", "covid", "eczema", "sinusitis",
    ],
}


def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract named entities from text using spaCy + custom medical lexicon.

    Returns list of dicts with 'text', 'label', 'start', 'end'.
    """
    nlp = _get_nlp()
    doc = nlp(text)
    entities = []

    # spaCy NER entities
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        })

    # Custom medical entity matching
    text_lower = text.lower()
    for category, keywords in MEDICAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                start = text_lower.index(keyword)
                entities.append({
                    "text": keyword,
                    "label": category.upper(),
                    "start": start,
                    "end": start + len(keyword),
                })

    # Deduplicate
    seen = set()
    unique_entities = []
    for ent in entities:
        key = (ent["text"].lower(), ent["label"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    return unique_entities
