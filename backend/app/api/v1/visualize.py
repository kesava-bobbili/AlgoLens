import logging

from fastapi import APIRouter, HTTPException

from app.schemas.visualize import VisualizeRequest, VisualizeResponse
from app.services.visualize_service import VisualizeService

logger = logging.getLogger(__name__)

router = APIRouter()
_service = VisualizeService()


@router.post("/visualize/trace", response_model=VisualizeResponse)
def trace_execution(request: VisualizeRequest) -> VisualizeResponse:
    try:
        return _service.trace(request)
    except Exception as exc:
        logger.exception("visualize/trace failed")
        raise HTTPException(
            status_code=500,
            detail=f"Visualization failed: {exc}",
        ) from exc
