"""Symptom Checker — decision-tree-based symptom triage system."""

import json
import os
from typing import Dict, Any, Optional, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
SYMPTOM_TREE_PATH = os.path.join(DATA_DIR, "symptom_tree.json")

_symptom_tree: Optional[Dict] = None


def _load_tree():
    global _symptom_tree
    if _symptom_tree is None:
        with open(SYMPTOM_TREE_PATH, 'r', encoding='utf-8') as f:
            _symptom_tree = json.load(f)
    return _symptom_tree


class SymptomCheckerSession:
    """Manages a single symptom checker session with branching logic."""

    def __init__(self):
        self.tree = _load_tree()
        self.current_node_id = "root"
        self.answers: List[Dict] = []
        self.scores: Dict[str, float] = {}

    def get_current_question(self) -> Dict[str, Any]:
        """Get the current question and options."""
        node = self.tree["nodes"][self.current_node_id]
        return {
            "node_id": self.current_node_id,
            "question": node["question"],
            "options": node.get("options", []),
            "category": node.get("category", "general"),
            "is_final": node.get("is_final", False),
        }

    def answer(self, option_index: int) -> Dict[str, Any]:
        """Process an answer and advance to the next node."""
        node = self.tree["nodes"][self.current_node_id]
        options = node.get("options", [])

        if option_index < 0 or option_index >= len(options):
            raise ValueError("Invalid option index")

        selected = options[option_index]
        self.answers.append({
            "question": node["question"],
            "answer": selected["text"],
            "node_id": self.current_node_id,
        })

        # Accumulate scores for conditions
        if "scores" in selected:
            for condition, score in selected["scores"].items():
                self.scores[condition] = self.scores.get(condition, 0) + score

        # Move to next node
        next_node_id = selected.get("next")
        if next_node_id is None or next_node_id not in self.tree["nodes"]:
            return self._generate_result()

        self.current_node_id = next_node_id
        next_node = self.tree["nodes"][self.current_node_id]

        if next_node.get("is_final", False):
            return self._generate_result()

        return self.get_current_question()

    def _generate_result(self) -> Dict[str, Any]:
        """Generate final result based on accumulated scores."""
        if not self.scores:
            return {
                "is_final": True,
                "result": {
                    "conditions": [],
                    "recommendation": "Based on your responses, no specific conditions were strongly indicated. If symptoms persist, please consult a healthcare professional.",
                    "urgency": "low",
                    "disclaimer": "⚠️ This assessment is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare provider for proper diagnosis and treatment.",
                },
            }

        # Sort conditions by score
        sorted_conditions = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        total_score = sum(s for _, s in sorted_conditions)

        conditions = []
        for condition, score in sorted_conditions[:3]:
            probability = round((score / total_score) * 100, 1) if total_score > 0 else 0
            condition_info = self.tree.get("conditions", {}).get(condition, {})
            conditions.append({
                "name": condition,
                "probability": probability,
                "description": condition_info.get("description", ""),
                "recommendation": condition_info.get("recommendation", "Consult a healthcare professional."),
            })

        # Determine urgency
        max_score = sorted_conditions[0][1] if sorted_conditions else 0
        urgency = "high" if max_score > 5 else "medium" if max_score > 3 else "low"

        return {
            "is_final": True,
            "result": {
                "conditions": conditions,
                "recommendation": f"Based on your symptoms, the most likely condition may be {sorted_conditions[0][0]}. Please consult a healthcare professional for a proper diagnosis.",
                "urgency": urgency,
                "disclaimer": "⚠️ This assessment is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare provider for proper diagnosis and treatment.",
            },
        }


# In-memory session store (in production, use Redis)
_sessions: Dict[str, SymptomCheckerSession] = {}


def create_session(session_id: str) -> Dict[str, Any]:
    """Start a new symptom checker session."""
    _load_tree()
    session = SymptomCheckerSession()
    _sessions[session_id] = session
    return session.get_current_question()


def answer_question(session_id: str, option_index: int) -> Dict[str, Any]:
    """Answer the current question in an existing session."""
    if session_id not in _sessions:
        raise ValueError("Session not found. Please start a new session.")
    session = _sessions[session_id]
    result = session.answer(option_index)
    if result.get("is_final"):
        del _sessions[session_id]  # Clean up completed session
    return result
