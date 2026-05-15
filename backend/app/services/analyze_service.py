from app.core.classifier import classify_problem, get_complexity_hint
from app.llm.client import LLMClient
from app.schemas.analyze import AnalysisResponse, ProblemRequest


class AnalyzeService:
    def __init__(self) -> None:
        self._llm = LLMClient()

    def analyze(self, request: ProblemRequest) -> AnalysisResponse:
        classification = classify_problem(request.problem_text)
        pattern = classification["pattern"]
        complexity = get_complexity_hint(pattern)

        explanation = self._llm.explain_problem(
            request.problem_text,
            pattern,
            complexity["time"],
            complexity["space"],
        )

        return AnalysisResponse(
            pattern=pattern,
            confidence=classification["confidence"],
            time_complexity=complexity["time"],
            space_complexity=complexity["space"],
            ai_explanation=explanation,
            all_matches=classification["all_matches"],
        )
