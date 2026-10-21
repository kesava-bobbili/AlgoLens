"""Tests for the LangGraph RAG workflow (graph_workflow.py).

These test the actual graph routing decisions — retrieve → grade → generate/fallback —
by mocking only the external calls (LLM, retrieve function) and running the real
compiled LangGraph StateGraph.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call

import pytest

from app.services.graph_workflow import RAGState, build_rag_graph, _build_context_summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sources(
    count: int = 3,
    score: float = 0.85,
    text: str = "Dynamic programming is used for optimal substructure problems.",
) -> list[dict[str, Any]]:
    """Build a list of fake source chunks with the given score."""
    return [
        {
            "source_id": f"src-{i}",
            "filename": f"notes_{i}.md",
            "file_type": "md",
            "chunk_index": i,
            "text": text,
            "score": score,
        }
        for i in range(count)
    ]


# ---------------------------------------------------------------------------
# Graph routing: relevant → generate
# ---------------------------------------------------------------------------

class TestGraphRoutingRelevant:
    """When retrieval returns good sources and the LLM grades them RELEVANT,
    the workflow must reach the 'generate' node, never 'fallback'."""

    def test_relevant_sources_route_to_generate(self, mock_llm: MagicMock):
        """High-score sources + LLM says RELEVANT → generate is called."""
        sources = _make_sources(count=3, score=0.85)
        retrieve_fn = MagicMock(return_value=sources)
        mock_llm._complete.return_value = "RELEVANT"

        graph = build_rag_graph(retrieve_fn=retrieve_fn, llm=mock_llm, top_k=5)
        initial_state: RAGState = {
            "question": "What is dynamic programming?",
            "sources": [],
            "is_relevant": False,
            "answer": "",
        }

        result = graph.invoke(initial_state)

        # Retrieve must have been called with the question
        retrieve_fn.assert_called_once_with("What is dynamic programming?", top_k=5)

        # LLM._complete must have been called for grading (relevance check)
        mock_llm._complete.assert_called_once()
        grading_prompt = mock_llm._complete.call_args[0][0]
        assert "RELEVANT" in grading_prompt or "relevant" in grading_prompt.lower()

        # LLM.answer_with_context must have been called for generation
        mock_llm.answer_with_context.assert_called_once_with(
            "What is dynamic programming?", sources
        )

        # Final state must contain the generated answer
        assert result["is_relevant"] is True
        assert result["answer"] == "Mock RAG answer grounded in context"
        assert len(result["sources"]) == 3

    def test_relevant_high_score_bypasses_llm_grading_threshold(self, mock_llm: MagicMock):
        """Even with moderate score above 0.25 threshold, LLM grading is invoked."""
        sources = _make_sources(count=2, score=0.30)
        retrieve_fn = MagicMock(return_value=sources)
        mock_llm._complete.return_value = "RELEVANT"

        graph = build_rag_graph(retrieve_fn=retrieve_fn, llm=mock_llm, top_k=3)
        result = graph.invoke({
            "question": "Explain sliding window",
            "sources": [],
            "is_relevant": False,
            "answer": "",
        })

        # Score is above 0.25 threshold, so LLM grading IS called
        mock_llm._complete.assert_called_once()
        # Since LLM says RELEVANT, generate node fires
        mock_llm.answer_with_context.assert_called_once()
        assert result["is_relevant"] is True


# ---------------------------------------------------------------------------
# Graph routing: irrelevant → fallback
# ---------------------------------------------------------------------------

class TestGraphRoutingIrrelevant:
    """When sources are low quality or LLM says IRRELEVANT, the fallback node fires."""

    def test_irrelevant_grading_routes_to_fallback(self, mock_llm: MagicMock):
        """LLM explicitly says IRRELEVANT → fallback message, generate never called."""
        sources = _make_sources(count=3, score=0.50)
        retrieve_fn = MagicMock(return_value=sources)
        mock_llm._complete.return_value = "IRRELEVANT"

        graph = build_rag_graph(retrieve_fn=retrieve_fn, llm=mock_llm, top_k=5)
        result = graph.invoke({
            "question": "What is quantum computing?",
            "sources": [],
            "is_relevant": False,
            "answer": "",
        })

        # Retrieve was called
        retrieve_fn.assert_called_once()

        # LLM grading was invoked
        mock_llm._complete.assert_called_once()

        # answer_with_context must NOT be called (fallback, not generate)
        mock_llm.answer_with_context.assert_not_called()

        # Fallback answer is the hardcoded message
        assert result["is_relevant"] is False
        assert "does not appear relevant" in result["answer"]
        assert "rephrasing" in result["answer"]

    def test_very_low_score_skips_llm_grading(self, mock_llm: MagicMock):
        """Average score below 0.25 → grade_node marks irrelevant WITHOUT calling LLM."""
        sources = _make_sources(count=3, score=0.10)
        retrieve_fn = MagicMock(return_value=sources)

        graph = build_rag_graph(retrieve_fn=retrieve_fn, llm=mock_llm, top_k=5)
        result = graph.invoke({
            "question": "irrelevant query",
            "sources": [],
            "is_relevant": False,
            "answer": "",
        })

        # LLM._complete should NOT be called (short-circuited by score threshold)
        mock_llm._complete.assert_not_called()
        # But fallback still fires
        mock_llm.answer_with_context.assert_not_called()
        assert result["is_relevant"] is False
        assert "does not appear relevant" in result["answer"]

    def test_empty_sources_routes_to_fallback(self, mock_llm: MagicMock):
        """No sources from retrieval → grade says irrelevant → fallback."""
        retrieve_fn = MagicMock(return_value=[])

        graph = build_rag_graph(retrieve_fn=retrieve_fn, llm=mock_llm, top_k=5)
        result = graph.invoke({
            "question": "anything",
            "sources": [],
            "is_relevant": False,
            "answer": "",
        })

        retrieve_fn.assert_called_once()
        # No LLM grading or generation should happen
        mock_llm._complete.assert_not_called()
        mock_llm.answer_with_context.assert_not_called()
        assert result["is_relevant"] is False
        assert "does not appear relevant" in result["answer"]


# ---------------------------------------------------------------------------
# Context summary helper
# ---------------------------------------------------------------------------

class TestBuildContextSummary:
    def test_formats_sources_correctly(self):
        sources = _make_sources(count=2, score=0.75)
        summary = _build_context_summary(sources)
        assert "Source 1" in summary
        assert "Source 2" in summary
        assert "score=0.75" in summary
        assert "Dynamic programming" in summary

    def test_empty_sources(self):
        summary = _build_context_summary([])
        assert summary == ""

    def test_truncates_long_text(self):
        sources = [{"score": 0.5, "text": "x" * 500}]
        summary = _build_context_summary(sources)
        # The code truncates text to 200 chars
        assert len(summary.split("): ")[1]) <= 200
