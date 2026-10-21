"""Tests for the RAG service (rag_service.py).

Covers: ChromaDB usage, text splitting, file extraction, answer_question
routing through LangGraph, and the empty-KB fallback path.
All external calls (HuggingFace embeddings, Groq LLM) are mocked.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import UploadFile

from app.services.rag_service import RAGService, TEXT_EXTENSIONS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def rag_service(mock_embed, mock_llm):
    """A RAGService wired to an in-memory ChromaDB and mocked LLM."""
    with patch("app.services.rag_service.LLMClient", return_value=mock_llm):
        service = RAGService()
    # Force in-memory ChromaDB
    import chromadb
    client = chromadb.Client()
    service._collection = client.get_or_create_collection(
        name="test_rag",
        metadata={"hnsw:space": "cosine"},
    )
    return service


@pytest.fixture()
def seeded_rag_service(rag_service, mock_embed):
    """RAG service with pre-seeded documents in the collection."""
    docs = [
        "Dynamic programming breaks problems into overlapping subproblems.",
        "The sliding window technique processes subarrays in O(n) time.",
        "Binary search works on sorted arrays in O(log n) time.",
    ]
    ids = [f"seed-{i}" for i in range(len(docs))]
    metadatas = [
        {"source_id": f"seed-src-{i}", "filename": f"notes_{i}.md",
         "file_type": "md", "chunk_index": 0}
        for i in range(len(docs))
    ]
    # Call _embed via the mock to get deterministic vectors
    embeddings = mock_embed.side_effect(docs)
    rag_service._collection.add(
        ids=ids,
        documents=docs,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return rag_service


# ---------------------------------------------------------------------------
# Empty knowledge base
# ---------------------------------------------------------------------------

class TestEmptyKnowledgeBase:
    def test_answer_question_empty_kb_returns_message(self, rag_service, mock_llm):
        """With no indexed documents, answer_question returns the specific empty-KB message."""
        # Patch _get_graph to return None so we go to the fallback direct path
        with patch.object(rag_service, "_get_graph", return_value=None):
            result = rag_service.answer_question("What is DP?")

        assert result["retrieval_count"] == 0
        assert result["sources"] == []
        assert "No indexed knowledge" in result["answer"]
        assert "Upload" in result["answer"]
        # LLM should never be called when KB is empty
        mock_llm.answer_with_context.assert_not_called()

    def test_retrieve_empty_returns_empty_list(self, rag_service):
        result = rag_service.retrieve("any query")
        assert result == []

    def test_stats_empty_returns_zero_chunks(self, rag_service):
        stats = rag_service.stats()
        assert stats["chunks"] == 0
        assert stats["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
        assert stats["vector_store"] == "ChromaDB"


# ---------------------------------------------------------------------------
# Retrieval with seeded data
# ---------------------------------------------------------------------------

class TestRetrieval:
    def test_retrieve_returns_scored_chunks(self, seeded_rag_service, mock_embed):
        results = seeded_rag_service.retrieve("dynamic programming", top_k=2)
        assert len(results) <= 2
        assert all(isinstance(r["score"], float) for r in results)
        assert all("source_id" in r and "filename" in r and "text" in r for r in results)
        assert mock_embed.called

    def test_similar_problem(self, seeded_rag_service):
        result = seeded_rag_service.similar_problem("overlapping subproblems", top_k=3)
        assert "matches" in result
        assert isinstance(result["matches"], list)


# ---------------------------------------------------------------------------
# answer_question with LangGraph
# ---------------------------------------------------------------------------

class TestAnswerQuestionWithGraph:
    def test_langgraph_path_relevant(self, seeded_rag_service, mock_llm, mock_embed):
        """When LangGraph grades sources as relevant, generate fires."""
        mock_llm._complete.return_value = "RELEVANT"

        result = seeded_rag_service.answer_question("What is dynamic programming?")

        assert result["answer"] == "Mock RAG answer grounded in context"
        assert result["retrieval_count"] > 0
        # Verify LLM was used for both grading and generation
        mock_llm._complete.assert_called_once()
        mock_llm.answer_with_context.assert_called_once()

    def test_langgraph_path_irrelevant(self, seeded_rag_service, mock_llm, mock_embed):
        """When LangGraph grades sources as irrelevant, fallback message returned."""
        mock_llm._complete.return_value = "IRRELEVANT"

        result = seeded_rag_service.answer_question("Quantum field theory basics?")

        assert "does not appear relevant" in result["answer"]
        mock_llm._complete.assert_called_once()
        mock_llm.answer_with_context.assert_not_called()

    def test_fallback_when_graph_unavailable(self, seeded_rag_service, mock_llm, mock_embed):
        """When LangGraph import fails, direct RAG fallback is used."""
        with patch.object(seeded_rag_service, "_get_graph", return_value=None):
            result = seeded_rag_service.answer_question("What is DP?")

        # Direct RAG: retrieves then calls LLM directly
        mock_llm.answer_with_context.assert_called_once()
        assert result["answer"] == "Mock RAG answer grounded in context"
        assert result["retrieval_count"] > 0


# ---------------------------------------------------------------------------
# Text splitting
# ---------------------------------------------------------------------------

class TestTextSplitting:
    def test_split_text_chunks_long_text(self, rag_service):
        text = "word " * 500  # ~2500 chars, chunk_size=900
        chunks = rag_service._split_text(text)
        assert len(chunks) >= 2
        for chunk in chunks:
            # Each chunk should be roughly within chunk size
            assert len(chunk) <= 1200  # allow some slack for splitter behavior

    def test_split_text_short_text_single_chunk(self, rag_service):
        text = "short text"
        chunks = rag_service._split_text(text)
        assert len(chunks) == 1
        assert chunks[0] == "short text"


# ---------------------------------------------------------------------------
# File extraction
# ---------------------------------------------------------------------------

class TestFileExtraction:
    def test_extract_text_plain(self, rag_service):
        text = rag_service._extract_text("notes.txt", b"Hello world")
        assert text == "Hello world"

    def test_extract_text_markdown(self, rag_service):
        md = b"# Header\n\nParagraph content"
        text = rag_service._extract_text("readme.md", md)
        assert "Header" in text
        assert "Paragraph" in text

    def test_extract_text_python(self, rag_service):
        code = b"def foo():\n    return 42"
        text = rag_service._extract_text("main.py", code)
        assert "def foo" in text

    def test_extract_json(self, rag_service):
        data = json.dumps({"key": "value"}).encode()
        text = rag_service._extract_text("data.json", data)
        parsed = json.loads(text)
        assert parsed["key"] == "value"

    def test_extract_csv(self, rag_service):
        csv_data = b"name,age\nAlice,30\nBob,25"
        text = rag_service._extract_text("data.csv", csv_data)
        assert "Alice" in text
        assert "Bob" in text

    def test_extract_unsupported_binary_raises(self, rag_service):
        with patch.object(rag_service, "_decode_text", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):
            with pytest.raises(ValueError, match="unsupported binary"):
                rag_service._extract_text("data.xyz", b"\xff\xfe")

    def test_text_extensions_contains_common_types(self):
        assert ".py" in TEXT_EXTENSIONS
        assert ".md" in TEXT_EXTENSIONS
        assert ".js" in TEXT_EXTENSIONS
        assert ".txt" in TEXT_EXTENSIONS
        assert ".ts" in TEXT_EXTENSIONS
        assert ".json" in TEXT_EXTENSIONS


# ---------------------------------------------------------------------------
# Normalize and source ID helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_normalize_text_strips_blank_lines(self, rag_service):
        text = "line one\n\n  \n  line two  \n"
        result = rag_service._normalize_text(text)
        assert result == "line one\nline two"

    def test_source_id_deterministic(self, rag_service):
        id1 = rag_service._source_id("test.txt", b"content")
        id2 = rag_service._source_id("test.txt", b"content")
        assert id1 == id2

    def test_source_id_different_for_different_content(self, rag_service):
        id1 = rag_service._source_id("test.txt", b"content1")
        id2 = rag_service._source_id("test.txt", b"content2")
        assert id1 != id2

    def test_decode_text_utf8(self, rag_service):
        assert rag_service._decode_text(b"hello") == "hello"

    def test_decode_text_latin1_fallback(self, rag_service):
        # Latin-1 encoded byte that's invalid UTF-8
        result = rag_service._decode_text(b"\xe9l\xe8ve")
        assert "l" in result  # should decode somehow
