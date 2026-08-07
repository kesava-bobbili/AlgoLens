from __future__ import annotations

from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    source_id: str
    filename: str
    file_type: str
    chunk_index: int
    text: str
    score: float


class KnowledgeIngestResponse(BaseModel):
    files_processed: int
    chunks_indexed: int
    skipped_files: list[str] = Field(default_factory=list)
    message: str


class KnowledgeQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=12)


class KnowledgeQueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    retrieval_count: int


class SimilarProblemRequest(BaseModel):
    problem_text: str = Field(..., min_length=1, max_length=8000)
    top_k: int = Field(default=5, ge=1, le=12)


class SimilarProblemResponse(BaseModel):
    matches: list[SourceChunk]


class KnowledgeStatsResponse(BaseModel):
    chunks: int
    embedding_model: str
    vector_store: str
