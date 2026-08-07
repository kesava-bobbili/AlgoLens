from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.knowledge import (
    KnowledgeIngestResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeStatsResponse,
    SimilarProblemRequest,
    SimilarProblemResponse,
)
from app.services.rag_service import RAGService

router = APIRouter()
_service = RAGService()


@router.post('/knowledge/ingest', response_model=KnowledgeIngestResponse)
async def ingest_knowledge(
    files: list[UploadFile] = File(...),
) -> KnowledgeIngestResponse:
    if not files:
        raise HTTPException(status_code=400, detail='Upload at least one file.')
    try:
        return KnowledgeIngestResponse(**await _service.ingest_files(files))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post('/knowledge/query', response_model=KnowledgeQueryResponse)
def query_knowledge(request: KnowledgeQueryRequest) -> KnowledgeQueryResponse:
    try:
        return KnowledgeQueryResponse(
            **_service.answer_question(request.question, top_k=request.top_k)
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post('/knowledge/similar', response_model=SimilarProblemResponse)
def similar_problem(request: SimilarProblemRequest) -> SimilarProblemResponse:
    try:
        return SimilarProblemResponse(
            **_service.similar_problem(request.problem_text, top_k=request.top_k)
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get('/knowledge/stats', response_model=KnowledgeStatsResponse)
def knowledge_stats() -> KnowledgeStatsResponse:
    try:
        return KnowledgeStatsResponse(**_service.stats())
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
