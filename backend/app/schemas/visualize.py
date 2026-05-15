from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class VisualizeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=8000)
    stdin: str = Field(default="", max_length=2000)


class TraceStep(BaseModel):
    step: int
    line_number: int
    line_content: str
    variables: Dict[str, str]
    call_stack: List[str]
    event: str


class VisualizeResponse(BaseModel):
    steps: List[TraceStep]
    source_lines: List[str]
    error: Optional[str] = None
    recursion_depth: int = 0
