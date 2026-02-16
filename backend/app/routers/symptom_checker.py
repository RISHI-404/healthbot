"""Symptom Checker routes — no auth required."""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.symptom_checker import create_session, answer_question

router = APIRouter()


class SymptomStartResponse(BaseModel):
    session_id: str
    node_id: str
    question: str
    options: list
    category: str
    is_final: bool = False


class SymptomAnswerRequest(BaseModel):
    session_id: str
    option_index: int


@router.post("/start", response_model=SymptomStartResponse)
async def start_symptom_check():
    """Start a new symptom checker session."""
    session_id = uuid.uuid4().hex[:16]
    question_data = create_session(session_id)
    return SymptomStartResponse(session_id=session_id, **question_data)


@router.post("/answer")
async def answer_symptom_question(answer: SymptomAnswerRequest):
    """Answer the current symptom checker question."""
    try:
        result = answer_question(answer.session_id, answer.option_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
