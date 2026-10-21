"""Tests for FastAPI API endpoints.

Covers: health check, analyze validation, patterns listing, visualize/trace
validation, and GitHub URL validation. All LLM calls are mocked.
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "AlgoLens API is live"
        assert "version" in data
        assert "docs" in data

    def test_docs_url_in_response(self, client):
        resp = client.get("/")
        assert resp.json()["docs"] == "/docs"


# ---------------------------------------------------------------------------
# Analyze endpoint
# ---------------------------------------------------------------------------

class TestAnalyzeEndpoint:
    def test_analyze_valid_input(self, client):
        """POST /api/v1/analyze with valid input returns classification."""
        with patch("app.api.v1.analyze._service._llm.explain_problem", return_value="Mock explanation"):
            resp = client.post(
                "/api/v1/analyze",
                json={"problem_text": "Find the maximum sum subsequence with optimal structure"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "pattern" in data
        assert "confidence" in data
        assert "time_complexity" in data
        assert "space_complexity" in data
        assert "ai_explanation" in data
        assert "all_matches" in data

    def test_analyze_empty_input_rejected(self, client):
        """Empty problem_text should be rejected by Pydantic validation."""
        resp = client.post("/api/v1/analyze", json={"problem_text": ""})
        assert resp.status_code == 422  # Pydantic validation error

    def test_analyze_missing_field_rejected(self, client):
        resp = client.post("/api/v1/analyze", json={})
        assert resp.status_code == 422

    def test_analyze_too_long_input_rejected(self, client):
        """problem_text exceeding max_length=10000 should be rejected."""
        resp = client.post(
            "/api/v1/analyze",
            json={"problem_text": "x" * 10001},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Patterns endpoint
# ---------------------------------------------------------------------------

class TestPatternsEndpoint:
    def test_patterns_returns_list(self, client):
        resp = client.get("/api/v1/patterns")
        assert resp.status_code == 200
        data = resp.json()
        assert "patterns" in data
        assert "total" in data
        assert isinstance(data["patterns"], list)
        assert data["total"] > 0
        assert "Dynamic Programming" in data["patterns"]


# ---------------------------------------------------------------------------
# Visualize endpoint validation
# ---------------------------------------------------------------------------

class TestVisualizeEndpoint:
    def test_visualize_valid_code(self, client):
        resp = client.post(
            "/api/v1/visualize/trace",
            json={"code": "x = 42\ny = x + 1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data
        assert "source_lines" in data
        assert data["error"] is None
        assert len(data["steps"]) > 0

    def test_visualize_empty_code_rejected(self, client):
        resp = client.post(
            "/api/v1/visualize/trace",
            json={"code": ""},
        )
        assert resp.status_code == 422

    def test_visualize_missing_code_rejected(self, client):
        resp = client.post(
            "/api/v1/visualize/trace",
            json={},
        )
        assert resp.status_code == 422

    def test_visualize_import_returns_error(self, client):
        resp = client.post(
            "/api/v1/visualize/trace",
            json={"code": "import os"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is not None
        assert data["steps"] == []

    def test_visualize_syntax_error_returns_error(self, client):
        resp = client.post(
            "/api/v1/visualize/trace",
            json={"code": "if True"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is not None


# ---------------------------------------------------------------------------
# GitHub endpoint validation
# ---------------------------------------------------------------------------

class TestGitHubEndpointValidation:
    def test_github_empty_url_rejected(self, client):
        resp = client.post(
            "/api/v1/github/analyze",
            json={"repo_url": ""},
        )
        assert resp.status_code == 422

    def test_github_missing_url_rejected(self, client):
        resp = client.post(
            "/api/v1/github/analyze",
            json={},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Knowledge endpoint validation
# ---------------------------------------------------------------------------

class TestKnowledgeEndpointValidation:
    def test_query_empty_question_rejected(self, client):
        resp = client.post(
            "/api/v1/knowledge/query",
            json={"question": ""},
        )
        assert resp.status_code == 422

    def test_query_missing_question_rejected(self, client):
        resp = client.post(
            "/api/v1/knowledge/query",
            json={},
        )
        assert resp.status_code == 422

    def test_similar_empty_text_rejected(self, client):
        resp = client.post(
            "/api/v1/knowledge/similar",
            json={"problem_text": ""},
        )
        assert resp.status_code == 422

    def test_top_k_out_of_range_rejected(self, client):
        resp = client.post(
            "/api/v1/knowledge/query",
            json={"question": "valid question", "top_k": 99},
        )
        assert resp.status_code == 422
