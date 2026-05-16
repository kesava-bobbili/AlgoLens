from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.classifier import classify_problem, get_complexity_hint
from app.llm.client import LLMClient
from app.schemas.analyze import AnalysisResponse, ProblemRequest


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Ensure app.* loggers emit INFO when uvicorn configures the root logger."""
    logging.getLogger("app").setLevel(logging.INFO)
    yield


settings = get_settings()
llm = LLMClient()

app = FastAPI(
    title="AlgoLens API",
    version=settings.api_version,
    description="AI-powered DSA copilot and developer productivity platform",
    lifespan=lifespan,
)

_cors_origins = (
    ["*"]
    if settings.cors_allow_all
    else settings.cors_origin_list
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=not settings.cors_allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "AlgoLens API is live",
        "version": settings.api_version,
        "docs": "/docs",
    }


# Legacy v1 compatibility (original student project endpoints)
@app.post("/analyze", response_model=AnalysisResponse)
def legacy_analyze(request: ProblemRequest) -> AnalysisResponse:
    classification = classify_problem(request.problem_text)
    pattern = classification["pattern"]
    complexity = get_complexity_hint(pattern)
    explanation = llm.explain_problem(
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


@app.get("/patterns")
def legacy_patterns() -> dict:
    from app.core.classifier import list_patterns

    patterns = list_patterns()
    return {"patterns": patterns, "total": len(patterns)}
