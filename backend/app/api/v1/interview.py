from fastapi import APIRouter

from app.schemas.interview import (
    InterviewRespondRequest,
    InterviewRespondResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.services.interview_service import InterviewService

router = APIRouter()
_service = InterviewService()


@router.post("/interview/start", response_model=InterviewStartResponse)
def start_interview(
    request: InterviewStartRequest,
) -> InterviewStartResponse:
    return _service.start(request)


@router.post("/interview/respond", response_model=InterviewRespondResponse)
def respond_interview(
    request: InterviewRespondRequest,
) -> InterviewRespondResponse:
    return _service.respond(request)
