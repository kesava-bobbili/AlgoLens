from __future__ import annotations

import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.llm import prompts
from app.llm.client import LLMClient

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    question: str
    sources: list[dict[str, Any]]
    is_relevant: bool
    answer: str


RELEVANCE_PROMPT = """You are a grading assistant. Decide whether the retrieved context is relevant to the user's question.

User question:
{question}

Retrieved context (summaries):
{context_summary}

Respond with EXACTLY one word: RELEVANT or IRRELEVANT
"""


def _build_context_summary(sources: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, s in enumerate(sources, 1):
        score = s.get("score", 0)
        text_preview = s.get("text", "")[:200]
        lines.append(f"Source {i} (score={score:.2f}): {text_preview}")
    return "\n".join(lines)


def build_rag_graph(
    retrieve_fn,
    llm: LLMClient,
    top_k: int = 5,
) -> StateGraph:
    """Build a LangGraph StateGraph for the RAG pipeline.

    Nodes:
        retrieve  -> grade -> generate (if relevant)
                           -> fallback  (if not relevant)
    """

    def retrieve_node(state: RAGState) -> dict:
        sources = retrieve_fn(state["question"], top_k=top_k)
        return {"sources": sources}

    def grade_node(state: RAGState) -> dict:
        sources = state.get("sources", [])
        if not sources:
            return {"is_relevant": False}

        avg_score = sum(s.get("score", 0) for s in sources) / len(sources)
        if avg_score < 0.25:
            logger.info("Average score %.3f below threshold, marking irrelevant.", avg_score)
            return {"is_relevant": False}

        context_summary = _build_context_summary(sources)
        prompt = RELEVANCE_PROMPT.format(
            question=state["question"],
            context_summary=context_summary[:4000],
        )
        verdict = llm._complete(prompt, max_tokens=10).strip().upper()
        is_relevant = "RELEVANT" in verdict and "IRRELEVANT" not in verdict
        logger.info("Relevance grading verdict: %s -> is_relevant=%s", verdict, is_relevant)
        return {"is_relevant": is_relevant}

    def generate_node(state: RAGState) -> dict:
        answer = llm.answer_with_context(state["question"], state["sources"])
        return {"answer": answer}

    def fallback_node(state: RAGState) -> dict:
        return {
            "answer": (
                "The retrieved context does not appear relevant to your question. "
                "Try rephrasing your question, or upload more specific notes and "
                "editorials to your knowledge base for better retrieval."
            )
        }

    def route_after_grade(state: RAGState) -> str:
        return "generate" if state.get("is_relevant", False) else "fallback"

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("generate", generate_node)
    graph.add_node("fallback", fallback_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", route_after_grade, {"generate": "generate", "fallback": "fallback"})
    graph.add_edge("generate", END)
    graph.add_edge("fallback", END)

    return graph.compile()
