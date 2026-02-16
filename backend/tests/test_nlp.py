"""
Tests for NLP services (emergency detector, entity extractor).
"""
import pytest
from app.services.emergency_detector import detect_emergency, EMERGENCY_RESPONSE
from app.services.entity_extractor import extract_entities


class TestEmergencyDetector:
    def test_detects_suicide_keyword(self):
        is_emergency, keyword = detect_emergency("I want to kill myself")
        assert is_emergency is True

    def test_detects_heart_attack(self):
        is_emergency, keyword = detect_emergency("I think I'm having a heart attack")
        assert is_emergency is True

    def test_no_emergency(self):
        is_emergency, keyword = detect_emergency("I have a mild headache")
        assert is_emergency is False

    def test_empty_input(self):
        is_emergency, keyword = detect_emergency("")
        assert is_emergency is False

    def test_emergency_keyword_returned(self):
        is_emergency, keyword = detect_emergency("chest pain can't breathe")
        assert is_emergency is True
        assert keyword is not None

    def test_emergency_response_exists(self):
        assert EMERGENCY_RESPONSE is not None
        assert "EMERGENCY" in EMERGENCY_RESPONSE


class TestEntityExtractor:
    def test_extracts_symptoms(self):
        entities = extract_entities("I have a headache and fever")
        labels = [e["label"] for e in entities]
        assert any(l in ["SYMPTOMS", "MEDICAL_ENTITY"] for l in labels)

    def test_extracts_body_parts(self):
        entities = extract_entities("My chest and stomach hurt")
        assert len(entities) > 0

    def test_empty_input(self):
        entities = extract_entities("")
        assert isinstance(entities, list)

    def test_returns_list_format(self):
        entities = extract_entities("I feel dizzy and nauseous")
        assert isinstance(entities, list)
        for entity in entities:
            assert "text" in entity
            assert "label" in entity
