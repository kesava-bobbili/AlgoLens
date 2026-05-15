from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from app.core.classifier import classify_problem
from app.llm.client import LLMClient
from app.schemas.interview import (
    InterviewRespondRequest,
    InterviewRespondResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)


@dataclass
class InterviewSession:
    problem_text: str
    pattern: str
    current_question: str
    turn_count: int = 0
    history: list[dict[str, str]] = field(default_factory=list)


class InterviewService:
    MAX_TURNS = 5

    def __init__(self) -> None:
        self._llm = LLMClient()
        self._sessions: dict[str, InterviewSession] = {}

    def start(self, request: InterviewStartRequest) -> InterviewStartResponse:
        classification = classify_problem(request.problem_text)
        pattern = classification["pattern"]
        question = self._llm.interview_question(
            request.problem_text, pattern
        )

        session_id = str(uuid.uuid4())
        self._sessions[session_id] = InterviewSession(
            problem_text=request.problem_text,
            pattern=pattern,
            current_question=question.strip(),
        )

        return InterviewStartResponse(
            session_id=session_id,
            pattern=pattern,
            question=question.strip(),
        )

    def respond(
        self, request: InterviewRespondRequest
    ) -> InterviewRespondResponse:
        session = self._sessions.get(request.session_id)
        if not session:
            return InterviewRespondResponse(
                score=None,
                feedback="Session expired. Please start a new interview.",
                follow_up=None,
                done=True,
            )

        session.turn_count += 1
        raw = self._llm.interview_evaluate(
            session.problem_text,
            session.current_question,
            request.answer,
        )

        score = self._parse_score(raw)
        feedback = self._parse_section(raw, "FEEDBACK")
        follow_up = self._parse_section(raw, "FOLLOW_UP")

        session.history.append(
            {
                "question": session.current_question,
                "answer": request.answer,
                "feedback": feedback,
            }
        )

        done = (
            session.turn_count >= self.MAX_TURNS
            or (follow_up and follow_up.upper().strip() == "DONE")
            or not follow_up
        )

        if not done and follow_up:
            session.current_question = follow_up

        if done:
            self._sessions.pop(request.session_id, None)

        return InterviewRespondResponse(
            score=score,
            feedback=feedback or raw,
            follow_up=None if done else follow_up,
            done=done,
        )

    @staticmethod
    def _parse_score(text: str) -> int | None:
        match = re.search(r"SCORE:\s*(\d+)", text, re.IGNORECASE)
        if match:
            return min(10, max(1, int(match.group(1))))
        return None

    @staticmethod
    def _parse_section(text: str, label: str) -> str:
        pattern = rf"{label}:\s*(.*?)(?=\n[A-Z_]+:|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
