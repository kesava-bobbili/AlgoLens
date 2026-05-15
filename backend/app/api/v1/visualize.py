from fastapi import APIRouter

from app.schemas.visualize import VisualizeRequest, VisualizeResponse
from app.services.visualize_service import VisualizeService

router = APIRouter()
_service = VisualizeService()


@router.post("/visualize/trace", response_model=VisualizeResponse)
def trace_execution(request: VisualizeRequest) -> VisualizeResponse:
    return _service.trace(request)
