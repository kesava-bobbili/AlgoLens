from typing import Dict

from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    problem_text: str = Field(..., min_length=1, max_length=10000)


class AnalysisResponse(BaseModel):
    pattern: str
    confidence: str
    time_complexity: str
    space_complexity: str
    ai_explanation: str
    all_matches: Dict[str, int]
