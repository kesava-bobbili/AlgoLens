from fastapi import APIRouter, HTTPException

from app.schemas.github import GitHubAnalyzeRequest, GitHubAnalyzeResponse
from app.services.github_service import GitHubService

router = APIRouter()
_service = GitHubService()


@router.post("/github/analyze", response_model=GitHubAnalyzeResponse)
async def analyze_github(
    request: GitHubAnalyzeRequest,
) -> GitHubAnalyzeResponse:
    try:
        return await _service.analyze(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub analysis failed: {exc}",
        ) from exc
