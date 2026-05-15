from fastapi import APIRouter

from app.schemas.analyze import AnalysisResponse, ProblemRequest
from app.services.analyze_service import AnalyzeService

router = APIRouter()
_service = AnalyzeService()


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_problem(request: ProblemRequest) -> AnalysisResponse:
    return _service.analyze(request)
