from __future__ import annotations

import logging

from groq import Groq

from app.config import get_settings
from app.llm import prompts

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.llm_model
        self._client = (
            Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        )

    def _complete(self, prompt: str, max_tokens: int = 1200) -> str:
        if not self._client:
            return (
                "LLM unavailable: set GROQ_API_KEY in .env. "
                "Classification and other features still work."
            )
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.4,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.warning("LLM completion failed: %s", exc, exc_info=True)
            return f"LLM error: {exc}"

    def explain_problem(
        self,
        problem_text: str,
        pattern: str,
        time_complexity: str,
        space_complexity: str,
    ) -> str:
        prompt = prompts.ANALYZE_PROMPT.format(
            problem_text=problem_text,
            pattern=pattern,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
        )
        return self._complete(prompt, max_tokens=1000)

    def interview_question(self, problem_text: str, pattern: str) -> str:
        prompt = prompts.INTERVIEW_START_PROMPT.format(
            problem_text=problem_text,
            pattern=pattern,
        )
        return self._complete(prompt, max_tokens=300)

    def interview_evaluate(
        self,
        problem_text: str,
        question: str,
        answer: str,
    ) -> str:
        prompt = prompts.INTERVIEW_EVALUATE_PROMPT.format(
            problem_text=problem_text,
            question=question,
            answer=answer,
        )
        return self._complete(prompt, max_tokens=600)



    def answer_with_context(
        self,
        question: str,
        sources: list[dict],
    ) -> str:
        context = "\n\n".join(
            f"SOURCE {index}: {source['filename']} chunk {source['chunk_index']} "
            f"(score {source['score']})\n{source['text']}"
            for index, source in enumerate(sources, start=1)
        )
        prompt = prompts.RAG_ANSWER_PROMPT.format(
            question=question,
            context=context[:12000],
        )
        return self._complete(prompt, max_tokens=1000)

    def analyze_github_repo(
        self,
        repo_full_name: str,
        description: str,
        language: str,
        topics: list[str],
        languages_block: str,
        tree: str,
        readme_excerpt: str,
    ) -> str:
        meta = prompts.GITHUB_ANALYSIS_PROMPT_META.format(
            repo_full_name=repo_full_name,
            description=description or "No description",
            language=language or "Unknown",
            topics=", ".join(topics) if topics else "None",
            languages_block=languages_block or "Unavailable",
        )
        safe_readme = (readme_excerpt or "")[:8000]
        prompt = (
            meta
            + prompts.GITHUB_ANALYSIS_PROMPT_TAIL
            + tree
            + prompts.GITHUB_ANALYSIS_README_MARKER
            + safe_readme
        )
        return self._complete(prompt, max_tokens=2500)
