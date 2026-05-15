from typing import Optional

from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    problem_text: str = Field(..., min_length=1, max_length=10000)


class InterviewStartResponse(BaseModel):
    session_id: str
    pattern: str
    question: str


class InterviewRespondRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1, max_length=5000)


class InterviewRespondResponse(BaseModel):
    score: Optional[int] = None
    feedback: str
    follow_up: Optional[str] = None
    done: bool
