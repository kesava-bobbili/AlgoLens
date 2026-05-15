from fastapi import APIRouter

from app.core.classifier import list_patterns

router = APIRouter()


@router.get("/patterns")
def get_patterns() -> dict:
    patterns = list_patterns()
    return {"patterns": patterns, "total": len(patterns)}
