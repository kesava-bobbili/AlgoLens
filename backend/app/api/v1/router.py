from fastapi import APIRouter

from app.api.v1 import analyze, github, interview, patterns, visualize

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analyze.router, tags=["analyze"])
api_router.include_router(patterns.router, tags=["patterns"])
api_router.include_router(visualize.router, tags=["visualize"])
api_router.include_router(interview.router, tags=["interview"])
api_router.include_router(github.router, tags=["github"])
