import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal

from backend.app.services.groq_service import ask_cooking_assistant

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AssistantRequest(BaseModel):
    question: str
    history: List[ChatMessage] = Field(default_factory=list)


@router.post("/ask")
def ask_assistant(request: AssistantRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        history = [
            message.model_dump()
            for message in request.history
        ]

        answer = ask_cooking_assistant(
            request.question,
            history
        )

        return {
            "question": request.question,
            "answer": answer["answer"],
            "source": answer["source"]
        }

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )