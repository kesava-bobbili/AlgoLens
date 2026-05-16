import logging

from fastapi import APIRouter, HTTPException

from app.schemas.github import GitHubAnalyzeRequest, GitHubAnalyzeResponse
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)

router = APIRouter()
_service = GitHubService()


@router.post("/github/analyze", response_model=GitHubAnalyzeResponse)
async def analyze_github(
    request: GitHubAnalyzeRequest,
) -> GitHubAnalyzeResponse:
    logger.info(
        "POST /github/analyze url_len=%s",
        len(request.repo_url),
    )
    try:
        result = await _service.analyze(request)
        logger.info(
            "POST /github/analyze OK meta=%s",
            result.meta.full_name,
        )
        return result
    except ValueError as exc:
        logger.warning("GitHub analyze validation/client error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("GitHub analyze unexpected failure")
        raise HTTPException(
            status_code=502,
            detail=f"GitHub analysis failed: {exc}",
        ) from exc
