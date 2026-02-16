"""Intent classification using TF-IDF + Logistic Regression."""

import json
import os
import re
from typing import Tuple, Optional

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Path to intents training data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MODEL_PATH = os.path.join(DATA_DIR, "intent_model.joblib")
INTENTS_PATH = os.path.join(DATA_DIR, "intents.json")

_model: Optional[Pipeline] = None
_intent_responses: dict = {}


def _preprocess(text: str) -> str:
    """Basic text preprocessing."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text


def train_model():
    """Train intent classifier from intents.json."""
    global _model, _intent_responses

    with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
        intents_data = json.load(f)

    texts = []
    labels = []
    _intent_responses = {}

    for intent in intents_data["intents"]:
        tag = intent["tag"]
        _intent_responses[tag] = intent["responses"]
        for pattern in intent["patterns"]:
            texts.append(_preprocess(pattern))
            labels.append(tag)

    _model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ('clf', LogisticRegression(max_iter=1000, C=10, random_state=42)),
    ])
    _model.fit(texts, labels)

    # Save model
    os.makedirs(DATA_DIR, exist_ok=True)
    joblib.dump((_model, _intent_responses), MODEL_PATH)


def load_model():
    """Load a previously trained model."""
    global _model, _intent_responses
    if os.path.exists(MODEL_PATH):
        _model, _intent_responses = joblib.load(MODEL_PATH)
    else:
        train_model()


def classify_intent(text: str) -> Tuple[str, float]:
    """
    Classify the intent of user input.

    Returns:
        (intent_tag, confidence_score)
    """
    global _model
    if _model is None:
        load_model()

    processed = _preprocess(text)
    intent = _model.predict([processed])[0]
    probabilities = _model.predict_proba([processed])[0]
    confidence = max(probabilities)

    return intent, float(confidence)


def get_response_for_intent(intent: str) -> str:
    """Get a random response template for the given intent."""
    import random
    global _intent_responses
    if intent in _intent_responses:
        return random.choice(_intent_responses[intent])
    return "I'm not sure I understand. Could you rephrase your question?"
