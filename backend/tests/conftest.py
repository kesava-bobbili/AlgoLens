"""Shared fixtures for the AlgoLens backend test suite.

Every fixture that touches external services (Groq, HuggingFace, ChromaDB,
GitHub) patches them so that no real network calls or model downloads happen.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Environment — set dummy keys BEFORE any app module is imported
# ---------------------------------------------------------------------------

os.environ.setdefault("GROQ_API_KEY", "test-dummy-key")
os.environ.setdefault("HF_TOKEN", "test-dummy-hf-token")
os.environ.setdefault("CORS_ALLOW_ALL", "true")
os.environ.setdefault("CHROMA_PERSISTENT", "false")


# ---------------------------------------------------------------------------
# Clear the Settings LRU cache so tests pick up the env vars above
# ---------------------------------------------------------------------------

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest.fixture()
def client() -> TestClient:
    """A fresh TestClient wrapping the real FastAPI `app`.

    We patch LLMClient._complete so no Groq calls happen at import time.
    """
    with patch("app.llm.client.Groq"):
        from app.main import app
        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# Mock LLM
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_llm() -> MagicMock:
    """A pre-configured MagicMock replacing LLMClient."""
    llm = MagicMock()
    llm._complete.return_value = "RELEVANT"
    llm.explain_problem.return_value = "Mock AI explanation"
    llm.interview_question.return_value = "Mock follow-up question"
    llm.interview_evaluate.return_value = "SCORE: 8\nFEEDBACK: Good.\nFOLLOW_UP: DONE"
    llm.answer_with_context.return_value = "Mock RAG answer grounded in context"
    llm.analyze_github_repo.return_value = "Mock AI repo analysis"
    return llm


# ---------------------------------------------------------------------------
# Temporary ChromaDB
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_chroma_dir(tmp_path):
    """Provide a unique temp directory for ChromaDB per test."""
    d = tmp_path / "chroma_test"
    d.mkdir()
    return d


@pytest.fixture()
def chroma_collection(tmp_chroma_dir):
    """An in-memory ChromaDB collection for test isolation."""
    import chromadb

    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="test_knowledge",
        metadata={"hnsw:space": "cosine"},
    )
    return collection


# ---------------------------------------------------------------------------
# Mock HuggingFace embedding API
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_embed():
    """Patch RAGService._embed to return deterministic fake vectors."""

    def fake_embed(texts: list[str]) -> list[list[float]]:
        """Return a unique-ish 384-dim vector per text (no network call)."""
        vectors = []
        for text in texts:
            h = hash(text) % (10**9)
            vec = [(h + i) % 1000 / 1000.0 for i in range(384)]
            vectors.append(vec)
        return vectors

    with patch("app.services.rag_service.RAGService._embed", side_effect=fake_embed) as m:
        yield m


# ---------------------------------------------------------------------------
# Mock requests.post (used by RAGService._embed for HF API)
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_hf_requests():
    """Patch requests.post used by RAGService._embed."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        [(i % 1000) / 1000.0 for i in range(384)]
    ]
    with patch("app.services.rag_service.requests.post", return_value=mock_resp) as m:
        yield m
